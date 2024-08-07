const bit<16> TYPE_IPV4 = 0x800;
const bit<16> TYPE_IPV6 = 0x86dd;
const bit<16> TYPE_VLAN = 0x8100;

const bit<8> IP_PROTO_ICMP   = 1;
const bit<8> IP_PROTO_TCP    = 6;
const bit<8> IP_PROTO_UDP    = 17;

#define CONST_MAX_PORTS     32
#define CONST_MAX_LABELS    64

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<16>  etherType_t;
typedef bit<12>  vlanid_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<128> ip6Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    etherType_t etherType;
}

header vlan_t {
    bit<3> pcp;
    bit<1> dei;
    vlanid_t vid;
    etherType_t etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<6>    diffserv;
    bit<2>    ecn;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header ipv6_t {
    bit<4>    version;
    bit<6>    diffserv;
    bit<2>    ecn;
    bit<20>   flow_label;
    bit<16>   payload_len;
    bit<8>    next_hdr;
    bit<8>    hop_limit;
    ip6Addr_t  src_addr;
    ip6Addr_t  dst_addr;
}

header tcp_t{
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<4>  res;
    bit<1>  cwr;
    bit<1>  ece;
    bit<1>  urg;
    bit<1>  ack;
    bit<1>  psh;
    bit<1>  rst;
    bit<1>  syn;
    bit<1>  fin;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> len;
    bit<16> checksum;
}


struct metadata {
    bit<8> meter_tag;
    bit<1> is_ingress_border;
    bit<1> is_egress_border;
}

struct headers {
    ethernet_t   ethernet;
    vlan_t      vlan;
    ipv4_t       ipv4;
    ipv6_t       ipv6;
    tcp_t        tcp;
    udp_t        udp;
}
