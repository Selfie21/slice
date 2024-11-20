#ifndef _HEADERS_
#define _HEADERS_

typedef bit<48> macaddr_t;
typedef bit<12> vlanid_t;
typedef bit<32> ip4addr_t;
typedef bit<128> ipv6_addr_t;
typedef bit<9> egress_spec_t;
typedef bit<8> slice_id_t;

typedef bit<16> ethertype_t;
const ethertype_t TYPE_IPV4 = 0x800;
const ethertype_t TYPE_IPV6 = 0x86dd;
const ethertype_t TYPE_VLAN = 0x8100;

typedef bit<8> iptype_t;
const iptype_t IP_PROTO_ICMP = 1;
const iptype_t IP_PROTO_TCP = 6;
const iptype_t IP_PROTO_UDP = 17;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

header ethernet_t {
  macaddr_t dst_addr;
  macaddr_t src_addr;
  ethertype_t ether_type;
}

header vlan_t {
  bit<3> pcp;
  bit<1> dei;
  vlanid_t vid;
  ethertype_t ether_type;
}

header mpls_h {
  bit<20> label;
  bit<3> exp;
  bit<1> bos;
  bit<8> ttl;
}

header ipv4_t {
  bit<4> version;
  bit<4> ihl;
  bit<6> diffserv;
  bit<2> ecn;
  bit<16> total_len;
  bit<16> identification;
  bit<3> flags;
  bit<13> frag_offset;
  bit<8> ttl;
  bit<8> protocol;
  bit<16> hdr_checksum;
  ip4addr_t src_addr;
  ip4addr_t dst_addr;
}

header ipv6_t {
  bit<4> version;
  bit<6> diffserv;
  bit<2> ecn;
  bit<20> flow_label;
  bit<16> payload_len;
  bit<8> next_hdr;
  bit<8> hop_limit;
  ipv6_addr_t src_addr;
  ipv6_addr_t dst_addr;
}

header tcp_t {
  bit<16> src_port;
  bit<16> dst_port;
  bit<32> seq_no;
  bit<32> ack_no;
  bit<4> data_offset;
  bit<4> res;
  bit<1> cwr;
  bit<1> ece;
  bit<1> urg;
  bit<1> ack;
  bit<1> psh;
  bit<1> rst;
  bit<1> syn;
  bit<1> fin;
  bit<16> window;
  bit<16> checksum;
  bit<16> urgen_ptr;
}

header udp_t {
  bit<16> src_port;
  bit<16> dst_port;
  bit<16> len;
  bit<16> checksum;
}

header icmp_h {
  bit<8> type_;
  bit<8> code;
  bit<16> checksum;
}

header arp_t {
  bit<16> hw_type;
  bit<16> prototype;
  bit<8> hw_addr_len;
  bit<8> proto_addr_len;
  bit<16> opcode;
}

header ipv6_srh_t {
  bit<8> next_hdr;
  bit<8> hdr_ext_len;
  bit<8> routing_type;
  bit<8> seg_left;
  bit<8> last_entry;
  bit<8> flags;
  bit<16> tag;
}

header vxlan_t {
  bit<8> flags;
  bit<24> reserved;
  bit<24> vni;
  bit<8> reserved2;
}

header gre_t {
  bit<1> C;
  bit<1> R;
  bit<1> K;
  bit<1> S;
  bit<1> s;
  bit<3> recurse;
  bit<5> flags;
  bit<3> version;
  bit<16> proto;
}


struct header_t {
  // pktgen headers
  pktgen_timer_header_t timer;
  pktgen_port_down_header_t port_down;
  pktgen_recirc_header_t recirc;
  // normal header
  ethernet_t ethernet;
  vlan_t vlan;
  ipv4_t ipv4;
  ipv6_t ipv6;
  tcp_t tcp;
  udp_t udp;
  icmp_h icmp;
}

struct empty_header_t {
} struct empty_metadata_t {
}

#endif /* _HEADERS_ */