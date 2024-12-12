# Pipe variable
pipe = bfrt.slice.pipe

# Table variable
ipv4 = pipe.Ingress.ipv4_lpm
vlan = pipe.Ingress.vlan_exact
slice_ident = pipe.Ingress.slice_ident
meter_filter = pipe.Ingress.m_filter
egress = pipe.Ingress.egress_check
arp = pipe.Ingress.arp

egress.add_with_is_egress_border(ucast_egress_port=24)

# Add arp entries
arp.add_with_forward(tpa="192.169.26.1", port=24)
arp.add_with_forward(tpa="192.169.26.2", port=16)

# Add forwarding rules IP
ipv4.add_with_ipv4_forward(hdr_ipv4_dst_addr="192.169.26.1", hdr_ipv4_dst_addr_p_length=32, dst_addr="1c:34:da:68:d4:02", port=24)
ipv4.add_with_ipv4_forward(hdr_ipv4_dst_addr="192.169.26.2", hdr_ipv4_dst_addr_p_length=32, dst_addr="1c:34:da:68:d4:1a", port=16)

# VLAN for Traffic Gen
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=21, port=132)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=22, port=140)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=23, port=148)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=24, port=156)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=25, port=164)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=26, port=172)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=27, port=180)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=28, port=188)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=29, port=56)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=30, port=48)

