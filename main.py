import sys
from loguru import logger
from scapy.all import Ether, Dot1Q, IP, UDP, TCP

from p4slice_api.internals.controller import Client
from p4slice_api.internals.util import ip2int

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

sport = 1234
src_mac = "00:00:0a:00:01:0b"
dst_mac = "00:00:0a:00:02:15"
p = (
    Ether(src=src_mac, dst=dst_mac)
    / IP(src="10.0.1.11", dst="10.0.2.21")
    / UDP(dport=443, sport=sport)
)
#client.generate_packets(packet=p, interval_nanoseconds=100000000)
meter = client.get_table("Ingress.meter")

client.program_meter(meter=meter, meter_index=1, meter_type="packets", cir=10, cbs=20, pir=10, pbs=40)
client.add_slice(src_addr='10.0.1.11', dst_addr='10.0.2.21', src_port=23, dst_port=26, protocol=17, slice_id=1)
client.add_slice(src_addr='10.0.1.12', dst_addr='10.0.2.22', src_port=23, dst_port=26, protocol=17, slice_id=2)

client.dump_table(slice_table)

client.info_table(meter)
client.add_egress_entry(3)
client.add_vlan_route(1, "ff:ff:ff:ff:ff:ff", 1)
#base_model = client.bfrt_info.learn_get("digest_inst")
#client.loop_digest(base_model)

