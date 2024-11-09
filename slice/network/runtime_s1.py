# Pipe variable
pipe = bfrt.slice.pipe

# Table variable
ipv4 = pipe.Ingress.ipv4_lpm
meter = pipe.Ingress.m_meter
meter_filter = pipe.Ingress.m_filter

# Add forwarding rules IP
ipv4.add_with_ipv4_forward(hdr_ipv4_dstAddr='10.0.1.11', hdr_ipv4_dstAddr_p_length=32, dstAddr='00:00:0a:00:01:0b', port=1)
ipv4.add_with_ipv4_forward(hdr_ipv4_dstAddr='10.0.1.12', hdr_ipv4_dstAddr_p_length=32, dstAddr='00:00:0a:00:01:0c', port=2)

ipv4.add_with_ipv4_forward(hdr_ipv4_dstAddr='10.0.2.21', hdr_ipv4_dstAddr_p_length=32, dstAddr='00:00:0a:00:02:15', port=3)
ipv4.add_with_ipv4_forward(hdr_ipv4_dstAddr='10.0.2.22', hdr_ipv4_dstAddr_p_length=32, dstAddr='00:00:0a:00:02:16', port=3)

# Add forward rules meter
meter.add_with_m_update(srcAddr='10.0.1.11', meterIndex=1)
meter.add_with_m_update(srcAddr='10.0.2.21', meterIndex=2)

meter_filter.add_with_drop(meterTag=3)