import sys
from controller.controller import Client
from loguru import logger
from scapy.all import Ether, Dot1Q, IP, UDP, TCP
from util import ip2int

ANNOTATIONS = ["ipv4", "ipv6", "mac", "bytes"]
logger.remove(0)
logger.add(sys.stderr, level="DEBUG", diagnose=False)
client = Client()
client.get_base_info()

ip_table = client._get_table("Ingress.ipv4_lpm")
#ip_table.info.key_field_annotation_add(field_name="dstAddr", custom_annotation="ipv4")
ip_table.info.data_field_annotation_add(field_name="dstAddr", action_name="Ingress.ipv4_forward", custom_annotation="ipv4")
logger.info(ip2int('10.0.2.21'))
key = client.gc.KeyTuple('hdr.ipv4.dstAddr', ip2int('10.0.2.21'), prefix_len=32)
client.info_table(ip_table)
client.dump_table(ip_table)
client.dump_entry(ip_table, key)

sport = 1234
src_mac = "00:00:0a:00:01:0b"
dst_mac = "00:00:0a:00:02:15"
p = (
    Ether(src=src_mac, dst=dst_mac)
    / IP(src="10.0.1.11", dst="10.0.2.21")
    / UDP(dport=443, sport=sport)
)
client.generate_packets(packet=p, interval_nanoseconds=100000000)

base_model = client.bfrt_info.learn_get("digest_inst")
client.loop_digest(base_model)

"""
TRY ON HW:
resp = self.port_table.entry_get(target, [], {"from_hw": False})
for d, k in resp:
    key_fields = k.to_dict()
    data_fields = d.to_dict()
    print(key_fields[b'$DEV_PORT']['value'], data_fields[b'$PORT_NAME'])
"""
