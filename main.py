import sys
from loguru import logger
from scapy.all import Ether, Dot1Q, IP, UDP, TCP

from controller.controller import Client
from controller.util import ip2int

ANNOTATIONS = ["ipv4", "ipv6", "mac", "bytes"]
logger.remove(0)
logger.add(sys.stderr, level="DEBUG", diagnose=False)
client = Client()
client.get_base_info()
#client.get_port_info()

ip_table = client.get_table("Ingress.ipv4_lpm")
ip_table.info.key_field_annotation_add(field_name="dst_addr", custom_annotation="ipv4")
ip_table.info.data_field_annotation_add(field_name="dst_addr", action_name="Ingress.ipv4_forward", custom_annotation="ipv4")
client.dump_table(ip_table)

slice_table = client.get_table("Ingress.slice_ident")
slice_table.info.key_field_annotation_add(field_name="dst_addr", custom_annotation="ipv4")
slice_table.info.key_field_annotation_add(field_name="src_addr", custom_annotation="ipv4")
client.dump_table(slice_table)

sport = 1234
src_mac = "00:00:0a:00:01:0b"
dst_mac = "00:00:0a:00:02:15"
p = (
    Ether(src=src_mac, dst=dst_mac)
    / IP(src="10.0.1.11", dst="10.0.2.21")
    / UDP(dport=443, sport=sport)
)
#client.generate_packets(packet=p, interval_nanoseconds=100000000)

base_model = client.bfrt_info.learn_get("digest_inst")
client.loop_digest(base_model)
