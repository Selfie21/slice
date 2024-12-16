# Pipe variable
pipe = bfrt.slice.pipe

# Table variable
ipv4 = pipe.Ingress.ipv4_lpm
vlan = pipe.Ingress.vlan_exact
slice_ident = pipe.Ingress.slice_ident
meter_filter = pipe.Ingress.m_filter
egress = pipe.Ingress.egress_check
arp = pipe.Ingress.arp

egress.add_with_is_egress_border(ucast_egress_port=132)
egress.add_with_is_egress_border(ucast_egress_port=140)

# Add arp entries
arp.add_with_forward(tpa="192.169.26.1", port=132)
arp.add_with_forward(tpa="192.169.26.2", port=140)

# Add forwarding rules IP
ipv4.add_with_ipv4_forward(hdr_ipv4_dst_addr="192.169.26.1", hdr_ipv4_dst_addr_p_length=32, dst_addr="1c:34:da:68:d4:02", port=132)
ipv4.add_with_ipv4_forward(hdr_ipv4_dst_addr="192.169.26.2", hdr_ipv4_dst_addr_p_length=32, dst_addr="1c:34:da:68:d4:1a", port=140)

# Add forwarding rules VLAN
vlan.add_with_vlan_forward(dst_addr="1c:34:da:68:d4:02", vlan_id=1, port=132)
vlan.add_with_vlan_forward(dst_addr="1c:34:da:68:d4:1a", vlan_id=2, port=140)

