# Pipe variable
pipe = bfrt.slice.pipe

# Table variable
ipv4 = pipe.Ingress.ipv4_lpm
vlan = pipe.Ingress.vlan_exact
slice_ident = pipe.Ingress.slice_ident
meter_filter = pipe.Ingress.m_filter
egress = pipe.Ingress.egress_check
meter = pipe.Ingress.meter

# Add forwarding rules VLAN
#vlan.add_with_vlan_forward(vlan_id=1, dst_addr='00:00:0a:00:01:0b', port=1)
#vlan.add_with_vlan_forward(vlan_id=2, dst_addr='00:00:0a:00:01:0c', port=2)
#vlan.add_with_vlan_forward(vlan_id=3, dst_addr='00:00:0a:00:02:15', port=3)
#vlan.add_with_vlan_forward(vlan_id=4, dst_addr='00:00:0a:00:02:16', port=3)

egress.add_with_is_egress_border(ucast_egress_port=1)
egress.add_with_is_egress_border(ucast_egress_port=2)

# Add forwarding rules IP
ipv4.add_with_ipv4_forward(hdr_ipv4_dst_addr='10.0.1.11', hdr_ipv4_dst_addr_p_length=32, dst_addr='00:00:0a:00:01:0b', port=1)
ipv4.add_with_ipv4_forward(hdr_ipv4_dst_addr='10.0.1.12', hdr_ipv4_dst_addr_p_length=32, dst_addr='00:00:0a:00:01:0c', port=2)

# Slice Configuration
#meter_filter.add_with_drop(meter_tag=3)


slice_ident.add_with_set_sliceid(src_addr='10.0.1.11', dst_addr='10.0.1.12', protocol=1, slice_id=1)
slice_ident.add_with_set_sliceid(src_addr='10.0.1.11', dst_addr='10.0.1.12', protocol=6, slice_id=1)
slice_ident.add_with_set_sliceid(src_addr='10.0.1.11', dst_addr='10.0.1.12', protocol=17, slice_id=1)

slice_ident.add_with_set_sliceid(src_addr='10.0.1.12', dst_addr='10.0.1.11', protocol=1, slice_id=2)
slice_ident.add_with_set_sliceid(src_addr='10.0.1.12', dst_addr='10.0.1.11', protocol=6, slice_id=2)
slice_ident.add_with_set_sliceid(src_addr='10.0.1.12', dst_addr='10.0.1.11', protocol=17, slice_id=2)

meter.add(METER_INDEX=255, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=100000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
