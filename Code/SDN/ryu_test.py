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
# See the License for the spcific language governing permissions and
# limitations under the License.

import sqlite3
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import arp
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import udp


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

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
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        print(self.mac_to_port)
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        #print("\nEssa é a mensagem recebida: {0}\n".format(msg))
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # ---------- Daniel changes ---------- #
        # Package decodification for the coming packets.
        # Used to match incoming packets with the known attack pattern
        arp_pkt = pkt.get_protocol(arp.arp)
        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
        tcp_pkt = pkt.get_protocol(tcp.tcp)
        udp_pkt = pkt.get_protocol(udp.udp)

        try:
            arp_src = arp_pkt.src_mac
            arp_dst = arp_pkt.dst_mac
        except AttributeError as err:
            arp_src = None
            arp_dst = None
            pass

        try:
            ipv4_src = ipv4_pkt.src
            ipv4_dst = ipv4_pkt.dst
        except AttributeError as err:
            ipv4_src = None
            ipv4_dst = None
            pass

        try:
            tcp_src = tcp_pkt.src_port
            tcp_dst = tcp_pkt.dst_port

        except AttributeError as err:
            tcp_src = None
            tcp_dst = None
            pass

        try:
            udp_src = udp_pkt.src_port
            udp_dst = udp_pkt.dst_port
        except AttributeError as  err:
            udp_src = None
            udp_dst = None
            pass

        conn = sqlite3.connect("database/sdnDatabase.db")
        cursor = conn.cursor()

        if (ipv4_src != None) and (ipv4_dst != None) and (tcp_dst != None) and (tcp_src != None):
            cursor.execute('select id from knownAttackers where srcaddr =  \"{0}\" and dstaddr = \"{1}\" and dstport = \"{2}\" and protocol = "tcp";'.format(ipv4_src,ipv4_dst,tcp_dst))
            result = cursor.fetchall()
            print(result)
            print("\n# --------- NEW TCP traffic ------------- #")
            print("\tIP Source: {0}, IP Dest: {1}, TCP Source Port: {2}, TCP Dest Port: {3}".format(ipv4_src,ipv4_dst,tcp_src,tcp_dst))
            if len(result) != 0:
                print("\tWARNING - Known malicious traffic")
                #proto = self.proto
                instruction = [parser.OFPInstructionActions(ofproto.OFPIT_CLEAR_ACTIONS, [])]
                msg = parser.OFPFlowMod(datapath, priority=1,command=ofproto.OFPFC_ADD, instructions=instruction)
                reply = datapath.send_msg(msg)
                #if reply:
                #    raise Exception
            else:
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
                    match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
                    # verify if we have a valid buffer_id, if yes avoid to send both
                    # flow_mod & packet_out
                    if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                        self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                        return
                    else:
                        self.add_flow(datapath, 1, match, actions)
                data = None
                if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                    data = msg.data

                out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                          in_port=in_port, actions=actions, data=data)
                datapath.send_msg(out)
            print("# --------- TCP End  ----------------- #\n")

        elif (ipv4_src != None) and (ipv4_dst != None) and (udp_src != None) and (udp_dst != None):
            cursor.execute('select id from knownAttackers where srcaddr = \"{0}\" and dstaddr = \"{1}\" and dstport = \"{2}\" and protocol = "tcp";'.format(ipv4_src, ipv4_dst, tcp_dst))
            result = cursor.fetchall()
            print ("\n# -------- NEW UDP Traffic ------------ #")
            print("\tIP Source: {0}, IP Dest: {1}, UDP Source Port: {2}, UDP Dest Port: {3}".format(ipv4_src,ipv4_dst,udp_src,udp_dst))
            if len(result) != 0:
                print("\tWARNING - Known malicious traffic")
                proto = self.proto
                instruction = [parser.OFPInstructionActions(proto.OFPIT_CLEAR_ACTIONS,[])]
                msg = parser.OFPFlowMod(datapath,priority=1,command=proto.OFPFC_ADD,match=None,instructions=instruction)
                reply = datapath.send_msg(msg)
                print(reply)
                if reply:
                    raise Exception
            else:
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
                    match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
                    # verify if we have a valid buffer_id, if yes avoid to send both
                    # flow_mod & packet_out
                    if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                        self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                        return
                    else:
                        self.add_flow(datapath, 1, match, actions)
                data = None
                if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                    data = msg.data

                out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                          in_port=in_port, actions=actions, data=data)
                datapath.send_msg(out)
            print("# ---------- UDP End ---------------- #\n")

        elif (ipv4_src != None) and (ipv4_dst != None):
            print("\n# --------- NEW IPv4 Traffic ---------------- #")
            print("\tIP Source: {0}, IP Dest: {1}".format(ipv4_src,ipv4_dst))
            print("# --------- IPv4 End ---------------------#\n")

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
                match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
                # verify if we have a valid buffer_id, if yes avoid to send both
                # flow_mod & packet_out
                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                    return
                else:
                    self.add_flow(datapath, 1, match, actions)
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data

                out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
                datapath.send_msg(out)

        elif (arp_src != None) and (arp_dst != None):
            print("\n# --------- ARP Traffic ------------- #")
            print("\tARP Source MAC: {0},ARP Destination MAC: {1}".format(arp_src,arp_dst))
            print("# --------- ARP End ----------------- #\n")

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
                match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
                # verify if we have a valid buffer_id, if yes avoid to send both
                # flow_mod & packet_out
                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                    return
                else:
                    self.add_flow(datapath, 1, match, actions)
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data

            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)


