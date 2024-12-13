# Pipe variable
pipe = bfrt.slice.pipe

# Table variable
ipv4 = pipe.Ingress.ipv4_lpm
vlan = pipe.Ingress.vlan_exact
slice_ident = pipe.Ingress.slice_ident
meter_filter = pipe.Ingress.m_filter
egress = pipe.Ingress.egress_check
arp = pipe.Ingress.arp

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

vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=25, port=184)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=26, port=176)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=27, port=168)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=28, port=160)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=29, port=144)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=30, port=152)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=31, port=128)
vlan.add_with_vlan_forward(dst_addr="ff:ff:ff:ff:ff:ff", vlan_id=32, port=136)

# Slice Idents 1-8 25-32
slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.1', slice_id=1)
slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.2', slice_id=2)
slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.3', slice_id=3)
slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.4', slice_id=4)
slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.5', slice_id=5)
slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.6', slice_id=6)
slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.7', slice_id=7)
slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.8', slice_id=8)

slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.25', slice_id=25)
slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.26', slice_id=26)
slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.27', slice_id=27)
slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.28', slice_id=28)
slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.29', slice_id=29)
slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.30', slice_id=30)
slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.31', slice_id=31)
slice_ident.add_with_set_sliceid(src_addr='192.168.178.10', dst_addr='192.168.178.32', slice_id=32)


# Metering
meter.add(METER_INDEX=1, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
meter.add(METER_INDEX=2, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
meter.add(METER_INDEX=3, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
meter.add(METER_INDEX=4, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
meter.add(METER_INDEX=5, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
meter.add(METER_INDEX=6, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
meter.add(METER_INDEX=7, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
meter.add(METER_INDEX=8, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
meter.add(METER_INDEX=25, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
meter.add(METER_INDEX=26, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
meter.add(METER_INDEX=27, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
meter.add(METER_INDEX=28, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
meter.add(METER_INDEX=29, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
meter.add(METER_INDEX=30, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
meter.add(METER_INDEX=31, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)
meter.add(METER_INDEX=32, METER_SPEC_CIR_KBPS=50000000, METER_SPEC_PIR_KBPS=75000000, METER_SPEC_CBS_KBITS=1500, METER_SPEC_PBS_KBITS=1500)

