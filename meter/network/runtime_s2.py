# Pipe variable
p4 = bfrt.meter.pipe

# Table variable
l3 = p4.Ingress.ipv4_lpm

# Add forwarding rules
l3.add_with_ipv4_forward(hdr_ipv4_dstAddr='10.0.1.11', hdr_ipv4_dstAddr_p_length=32, dstAddr='00:00:0a:00:01:0b', port=3)
l3.add_with_ipv4_forward(hdr_ipv4_dstAddr='10.0.1.12', hdr_ipv4_dstAddr_p_length=32, dstAddr='00:00:0a:00:01:0c', port=3)

l3.add_with_ipv4_forward(hdr_ipv4_dstAddr='10.0.2.21', hdr_ipv4_dstAddr_p_length=32, dstAddr='00:00:0a:00:02:15', port=1)
l3.add_with_ipv4_forward(hdr_ipv4_dstAddr='10.0.2.22', hdr_ipv4_dstAddr_p_length=32, dstAddr='00:00:0a:00:02:16', port=2)
