from snortparser import Parser

#rule = ('alert tcp $HOME_NET 20256 -> $EXTERNAL_NET any (msg:"PROTOCOL-SCADA PCOM Write Data Table binary reply"; flow:to_client,established; byte_test:1,=,102,2; content:"|C4|"; depth:1; offset:18; metadata:ruleset community; reference:url,unitronicsplc.com; classtype:attempted-recon; sid:49032; rev:1;)')
#rule = ('alert tcp any any -> any any (msg:"MALWARE-BACKDOOR - Dagger_1.4.0"; flow:to_client,established; content:"2|00 00 00 06 00 00 00|Drives|24 00|"; depth:16; metadata:ruleset community; classtype:misc-activity; sid:105; rev:14;)')
rule = ('alert tcp any aney -> any any (msg: "ICMP Error";)')
parsed = Parser(rule)

print(parsed.header)
print("\n")
print(parsed.data)
