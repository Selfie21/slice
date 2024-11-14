/* -*- P4_16 -*- */
#include <core.p4>
#include <tna.p4>
#include "common/headers.p4"
#include "common/utils.p4"


struct digest_t {
  bit<8> meterTag;
}

struct pvs_pgen_key_t {
  bit<3> pad;
  bit<2> pipe_id;
  bit<3> app_id;
}

struct metadata_t {
  digest_t tmp_digest;
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
    transition select(hdr.ethernet.etherType) {
    TYPE_VLAN:
      parse_vlan;
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
    transition select(hdr.vlan.etherType) {
    TYPE_IPV4:
      parse_ipv4;
    default:
      accept;
    }
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
    transition select(hdr.ipv6.nextHdr) {
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
    transition accept;
  }

  state parse_udp {
    pkt.extract(hdr.udp);
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

  Meter<bit<8>>(256, MeterType_t.PACKETS) meter;

  action drop() { ig_dprsr_md.drop_ctl = 1; }

  // Meter
  action m_update(bit<8> meterIndex) {
    meta.tmp_digest.meterTag = meter.execute(meterIndex);
    ig_dprsr_md.digest_type = 1;
  }

  table m_meter {
    key = { hdr.ipv4.srcAddr : exact;
    }
    actions = { m_update;
    NoAction;
  }
  default_action = NoAction;
  size = 256;
  }

  table m_filter {
    key = { meta.tmp_digest.meterTag : exact;
  }
  actions = { drop;
  NoAction;
  }
  default_action = NoAction;
  size = 8;
  }

  // IP Forward
  action ipv4_forward(macaddr_t dstAddr, egress_spec_t port) {
    ig_tm_md.ucast_egress_port = port;
    hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
    hdr.ethernet.dstAddr = dstAddr;
    hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
  }

  table ipv4_lpm {
    key = { hdr.ipv4.dstAddr : lpm;
  }
  actions = { ipv4_forward;
  drop;
  NoAction;
  }
  size = 4096;
  default_action = NoAction();
  }

  action ipv6_forward(macaddr_t dstAddr, egress_spec_t port) {
    ig_tm_md.ucast_egress_port = port;
    hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
    hdr.ethernet.dstAddr = dstAddr;
    hdr.ipv6.hopLimit = hdr.ipv6.hopLimit - 1;
  }

  table ipv6_lpm {
      key = { hdr.ipv6.dstAddr : lpm; }
      actions = { ipv6_forward; drop; NoAction; }
      size = 4096;
      default_action = NoAction();
  }

  apply {
    m_meter.apply();
    m_filter.apply();

    if (hdr.ipv4.isValid()) {
      ipv4_lpm.apply();
    }else if (hdr.ipv6.isValid()) {
      ipv6_lpm.apply();
    }
  }
}

/*********************  D E P A R S E R  ************************/

control IngressDeparser(packet_out pkt, inout header_t hdr, in metadata_t meta,
                in ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md) {
  Checksum() ipv4_checksum;
  Digest<digest_t>() digest_inst;

  apply {

    if (ig_dprsr_md.digest_type == 1) {
      digest_inst.pack({meta.tmp_digest.meterTag});
    }

    hdr.ipv4.hdrChecksum = ipv4_checksum.update(
        {hdr.ipv4.version, hdr.ipv4.ihl, hdr.ipv4.diffserv, hdr.ipv4.ecn,
         hdr.ipv4.totalLen, hdr.ipv4.identification, hdr.ipv4.flags,
         hdr.ipv4.fragOffset, hdr.ipv4.ttl, hdr.ipv4.protocol, hdr.ipv4.srcAddr,
         hdr.ipv4.dstAddr});

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