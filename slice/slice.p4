/* -*- P4_16 -*- */
#include <core.p4>
#include <tna.p4>

#include "common/headers.p4"
#include "common/utils.p4"

#define MAX_SLICES 256
#define CONST_MAX_PORTS 32
#define PACKET_GEN_PORT 68
#define ROUTE_TABLE_SIZE 4096
#define CONST_PCP 5
#define CONST_DEI 0

struct digest_t {
  bit<3> digest_type;
  slice_id_t slice_id;
  ip4addr_t src_addr;
  ip4addr_t dst_addr;
  bit<16> src_port;
  bit<16> dst_port;
}

struct pvs_pgen_key_t {
  bit<3> pad;
  bit<2> pipe_id;
  bit<3> app_id;
}

struct metadata_t {
  bit<16> src_port;
  bit<16> dst_port;
  bit<8> meter_tag;
  slice_id_t slice_id;
}

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

/***********************  P A R S E R  **************************/
parser IngressParser(packet_in pkt, out header_t hdr, out metadata_t meta,
              out ingress_intrinsic_metadata_t ig_intr_md) {
  // Resubmit package and intrinsic metadata
  TofinoIngressParser() tofino_parser;

  state start {
    tofino_parser.apply(pkt, ig_intr_md);
    transition select(ig_intr_md.ingress_port) {
    PACKET_GEN_PORT:
      parse_pktgen_timer;
      default:
        parse_ethernet;
    }
  }

  state parse_pktgen_timer {
    pkt.extract(hdr.timer);
    transition parse_ethernet;
  }

  state parse_ethernet {
    pkt.extract(hdr.ethernet);
    transition select(hdr.ethernet.ether_type) {
    TYPE_VLAN:
      parse_vlan;
    TYPE_ARP:
      parse_arp;
    TYPE_IPV4:
      parse_ipv4;
    TYPE_IPV6:
      parse_ipv6;
      default:
        accept;
    }
  }

  state parse_vlan {
    pkt.extract(hdr.vlan);
    transition select(hdr.vlan.ether_type) {
    TYPE_IPV4:
      parse_ipv4;
    TYPE_IPV6:
      parse_ipv6;
      default:
        accept;
    }
  }

  state parse_arp {
      pkt.extract(hdr.arp);
      transition accept;
  }

  state parse_ipv4 {
    pkt.extract(hdr.ipv4);
    transition select(hdr.ipv4.protocol) {
    IP_PROTO_TCP:
      parse_tcp;
    IP_PROTO_UDP:
      parse_udp;
    IP_PROTO_ICMP:
      parse_icmp;
      default:
        accept;
    }
  }

  state parse_ipv6 {
    pkt.extract(hdr.ipv6);
    transition select(hdr.ipv6.next_hdr) {
    IP_PROTO_TCP:
      parse_tcp;
    IP_PROTO_UDP:
      parse_udp;
    IP_PROTO_ICMP:
      parse_icmp;
      default:
        accept;
    }
  }

  state parse_tcp {
    pkt.extract(hdr.tcp);
    meta.src_port = hdr.tcp.src_port;
    meta.dst_port = hdr.tcp.dst_port;
    transition accept;
  }

  state parse_udp {
    pkt.extract(hdr.udp);
    meta.src_port = hdr.udp.src_port;
    meta.dst_port = hdr.udp.dst_port;
    transition accept;
  }

  state parse_icmp {
    pkt.extract(hdr.icmp);
    transition accept;
  }
}

/***************** M A T C H - A C T I O N  *********************/
control Ingress(inout header_t hdr, inout metadata_t meta,
                in ingress_intrinsic_metadata_t ig_intr_md,
                in ingress_intrinsic_metadata_from_parser_t ig_prsr_md,
                inout ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md,
                inout ingress_intrinsic_metadata_for_tm_t ig_tm_md) {
  Meter<bit<8>>(MAX_SLICES, MeterType_t.BYTES) meter;
  action drop() {
    ig_dprsr_md.drop_ctl = 1;
  }

  // Slice
  action set_sliceid(slice_id_t slice_id) {
    meta.slice_id = slice_id;

    // Set VLAN Header
    hdr.vlan.setValid();
    hdr.vlan.pcp = CONST_PCP;
    hdr.vlan.dei = CONST_DEI;
    hdr.vlan.vlan_id = (bit<12>)slice_id;

    // preserve original ether_type
    hdr.vlan.ether_type = hdr.ethernet.ether_type;
    hdr.ethernet.ether_type = TYPE_VLAN;
  }

  table slice_ident {
    key = { hdr.ipv4.dst_addr : exact;
    hdr.ipv4.src_addr : exact;
  }
  actions = { set_sliceid;
  drop;
  NoAction;
}
size = MAX_SLICES;
default_action = NoAction();
}

// Meter
action m_update(slice_id_t meter_index) {
  meta.meter_tag = meter.execute(meter_index);
}


table m_filter {
  key = { meta.meter_tag : exact;
}
actions = { drop;
NoAction;
}
default_action = NoAction;
size = 8;
}

// For ARP Requests we flood on all ports
action forward(egress_spec_t port) {
  ig_tm_md.ucast_egress_port = port;
}

table arp {
  key = { hdr.arp.tpa : exact;
}
actions = {
forward;
NoAction;
}
default_action = NoAction;
size = ROUTE_TABLE_SIZE;
}

// Firewall
table firewall {
  key = { hdr.ipv4.src_addr : lpm;
}
actions = { drop;
NoAction;
}
default_action = NoAction;
size = MAX_SLICES;
}

// IP Forward
action ipv4_forward(macaddr_t dst_addr, egress_spec_t port) {
  ig_tm_md.ucast_egress_port = port;
  hdr.ethernet.src_addr = hdr.ethernet.dst_addr;
  hdr.ethernet.dst_addr = dst_addr;
  hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
}

table ipv4_lpm {
  key = { hdr.ipv4.dst_addr : lpm;
}
actions = { ipv4_forward;
drop;
NoAction;
}
size = ROUTE_TABLE_SIZE;
default_action = NoAction();
}

action ipv6_forward(macaddr_t dst_addr, egress_spec_t port) {
  ig_tm_md.ucast_egress_port = port;
  hdr.ethernet.src_addr = hdr.ethernet.dst_addr;
  hdr.ethernet.dst_addr = dst_addr;
  hdr.ipv6.hop_limit = hdr.ipv6.hop_limit - 1;
}

table ipv6_lpm {
  key = { hdr.ipv6.dst_addr : lpm;
}
actions = { ipv6_forward;
drop;
NoAction;
}
size = ROUTE_TABLE_SIZE;
default_action = NoAction();
}

// VLAN
action vlan_forward(macaddr_t dst_addr, egress_spec_t port) {
  ig_tm_md.ucast_egress_port = port;
  hdr.ethernet.src_addr = hdr.ethernet.dst_addr;
  hdr.ethernet.dst_addr = dst_addr;
}

table vlan_exact {
  key = { hdr.vlan.vlan_id : exact;
}
actions = { vlan_forward;
drop;
NoAction;
}
size = ROUTE_TABLE_SIZE;
default_action = NoAction();
}

action is_egress_border() {
  hdr.ethernet.ether_type = hdr.vlan.ether_type;
  hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
  hdr.vlan.setInvalid();
}

table egress_check {
  key = { ig_tm_md.ucast_egress_port : exact;
}
actions = { NoAction;
is_egress_border;
}
default_action = NoAction;
size = CONST_MAX_PORTS;
}

apply {

  // First Firewall Processing
  if (hdr.ipv4.isValid()){
    firewall.apply();
  }

  // We only process packets, identifiable in a slice. Or if the packet was already
  // tagged. Others get dropped
  bool valid_packet = false;
  if (hdr.vlan.isValid()) {
      meta.slice_id = (bit<8>)hdr.vlan.vlan_id;
  }
  if (slice_ident.apply().hit) {
    valid_packet = true;
  }

  if (valid_packet) {
    // update meter, send digests and filter
    m_update(meta.slice_id);
    if(meta.meter_tag == 8w3){
      ig_dprsr_md.digest_type = 1;
    }

    if (m_filter.apply().miss){
      // Routing Decisions
      if (hdr.vlan.isValid()) {
        // If we have no VLAN routing we opt for normal IP routing
        if (vlan_exact.apply().miss){
          if (hdr.ipv4.isValid()) {
            ipv4_lpm.apply();
          }else if (hdr.ipv6.isValid()) {
            ipv6_lpm.apply();
          } else {
            drop();
          }
        }
      }

      if (hdr.vlan.isValid()) {
        egress_check.apply();
      }
    }
  }else if(hdr.arp.isValid()){
    arp.apply();
  }else{
    drop();
  }
}
}

/*********************  D E P A R S E R  ************************/

control IngressDeparser(packet_out pkt, inout header_t hdr, in metadata_t meta,
                        in ingress_intrinsic_metadata_for_deparser_t
                            ig_dprsr_md) {
  Checksum() ipv4_checksum;
  Digest<digest_t>() digest_inst;

  apply {
    if (ig_dprsr_md.digest_type == 1) {
      digest_inst.pack({ig_dprsr_md.digest_type, meta.slice_id, hdr.ipv4.src_addr, hdr.ipv4.dst_addr, meta.src_port, meta.dst_port});
    }
    hdr.ipv4.hdr_checksum = ipv4_checksum.update(
        {hdr.ipv4.version, hdr.ipv4.ihl, hdr.ipv4.diffserv, hdr.ipv4.ecn,
         hdr.ipv4.total_len, hdr.ipv4.identification, hdr.ipv4.flags,
         hdr.ipv4.frag_offset, hdr.ipv4.ttl, hdr.ipv4.protocol,
         hdr.ipv4.src_addr, hdr.ipv4.dst_addr});

    pkt.emit(hdr);
  }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/
// Empty

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

Pipeline(IngressParser(), Ingress(), IngressDeparser(), TofinoEgressParser(),
         EmptyEgress(), EmptyEgressDeparser()) pipe;
Switch(pipe) main;
