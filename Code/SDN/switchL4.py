# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import udp
from ryu.lib.packet import in_proto
import sqlite3

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.initial = True
        self.security_alert = False

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        self.initial = True
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        self.initial = False

    # Adds a flow into a specific datapath, with a hard_timeout of 5 minutes.
    # Meaning that a certain packet flow ceases existing after 5 minutes.
    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            if self.initial == True:
                mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                        priority=priority, match=match,
                                        instructions=inst)
            elif self.initial == False:
                mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                        priority=priority, match=match,
                                        instructions=inst,hard_timeout=300)
        else:
            if self.initial == True:
                mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                        match=match, instructions=inst)

            elif self.initial == False:
                mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                        match=match, instructions=inst,
                                        hard_timeout=300)
        datapath.send_msg(mod)

    # Adds a security flow into the controlled device, a secured flow differs from a normal
    # flow in it's duration, a security flow has a duration of 2 hours.
    def add_security_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        #inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
        #                                     actions)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_CLEAR_ACTIONS, [])]

        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority,match=match,command=ofproto.OFPFC_ADD,
                                    instructions=inst, hard_timeout=7200)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst, command=ofproto.OFPFC_ADD,
                                    hard_timeout=7200)

        datapath.send_msg(mod)

    # Deletes a already existing flow that matches has a given packet match.
    def del_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath,buffer_id=buffer_id,
                                    priority=priority,match=match,instruction=inst,
                                    command=ofproto.OFPFC_DELETE)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst,
                                    command=ofproto.OFPFC_DELETE)

        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            # check IP Protocol and create a match for IP
            if eth.ethertype == ether_types.ETH_TYPE_IP:
                conn = sqlite3.connect("database/sdnDatabase.db")
                cursor = conn.cursor()
                ip = pkt.get_protocol(ipv4.ipv4)
                srcip = ip.src
                dstip = ip.dst
                protocol = ip.proto

                # ICMP Protocol
                if protocol == in_proto.IPPROTO_ICMP:
                    print("WARN - We have a ICMP packet")
                    cursor.execute('select id from knownAttackers where srcaddr =  \"{0}\" and dstaddr = \"{1}\" and protocol = "icmp";'.format(srcip, dstip))
                    result = cursor.fetchall()
                    match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=srcip, ipv4_dst=dstip,
                                            ip_proto=protocol)
                    if len(result) == 0:
                        self.security_alert = False
                    else:
                        self.security_alert = True

                # TCP Protocol
                elif protocol == in_proto.IPPROTO_TCP:
                    print("WARN - We have a TCP packet")
                    t = pkt.get_protocol(tcp.tcp)
                    cursor.execute('select id from knownAttackers where srcaddr =  \"{0}\" and dstaddr = \"{1}\" and dstport = \"{2}\" and protocol = "tcp";'.format(srcip, dstip, t.dst_port))
                    result = cursor.fetchall()
                    if len(result) == 0:
                        self.security_alert = False
                        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=srcip, ipv4_dst=dstip,
                                                ip_proto=protocol, tcp_src=t.src_port, tcp_dst=t.dst_port)
                    else:
                        print("We have a register in the database for this specific packet: {0}".format(result))
                        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=srcip, ipv4_dst=dstip,
                                                ip_proto=protocol, tcp_dst=t.dst_port)
                        self.security_alert = True

                # UDP Protocol
                elif protocol == in_proto.IPPROTO_UDP:
                    print("WARN - We have a UDP packet")
                    u = pkt.get_protocol(udp.udp)
                    cursor.execute('select id from knownAttackers where srcaddr =  \"{0}\" and dstaddr = \"{1}\" and dstport = \"{2}\" and protocol = "udp";'.format(srcip, dstip, u.dst_port))
                    result = cursor.fetchall()

                    if len(result) == 0:
                        self.security_alert = False
                        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=srcip, ipv4_dst=dstip,
                                                ip_proto=protocol, udp_src=u.src_port, udp_dst=u.dst_port)
                    else:
                        self.security_alert = True
                        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=srcip, ipv4_dst=dstip,
                                                ip_proto=protocol, udp_dst=u.dst_port)

                else:
                    self.security_alert = False
                    match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)

                # verify if we have a valid buffer_id, if yes avoid to send both
                # flow_mod & packet_out
                if self.security_alert == False:
                    if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                        self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                        return
                    else:
                        self.add_flow(datapath, 1, match, actions)

                elif self.security_alert == True:
                    if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                        self.add_security_flow(datapath, 1, match, actions, msg.buffer_id)
                        return
                    else:
                        self.add_security_flow(datapath, 1, match, actions)


        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        if self.security_alert == False:
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)
