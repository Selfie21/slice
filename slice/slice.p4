/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>
#include "headers.p4"
#include "parsers.p4"
#include "debug.p4"



/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    #define CONST_PCP 5
    #define CONST_DEI 0

    meter(32w4, MeterType.packets) my_meter;
    debug_std_meta() debug;

    action drop() {
        mark_to_drop(standard_metadata);
    }

    // ** Custom VLAN Header
    action ingress_border(){
        meta.is_ingress_border = 1;
    }
    table check_is_ingress_border {
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            ingress_border;
            NoAction;
        }
        size = CONST_MAX_PORTS;
        default_action = NoAction;
    }


    // add vlan header
    action add_vlan_header(vlanid_t vid) {
        hdr.vlan.setValid();

        hdr.vlan.pcp = CONST_PCP;
        hdr.vlan.dei = CONST_DEI;
        hdr.vlan.vid = vid;
        //preserve original ethertype
        hdr.vlan.etherType = hdr.ethernet.etherType;
        hdr.ethernet.etherType = TYPE_VLAN;
    }

    table fec_to_vlan {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            add_vlan_header;
            NoAction;
        }
        size = CONST_MAX_LABELS;
        default_action = NoAction;
    }

    // Vlan forward
    action vlan_forward(macAddr_t dstAddr, egressSpec_t port) {
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        standard_metadata.egress_spec = port;
    }

    table vlan_tbl {
        key = {
            hdr.vlan.vid: exact;
        }
        actions = {
            vlan_forward;
            NoAction;
        }
        size = CONST_MAX_LABELS;
        default_action = NoAction;
    }

    // ** IPV4
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    // ** Meter
    action m_update(bit<32> meter_index) {
        my_meter.execute_meter<bit<8>>(meter_index, meta.meter_tag);
    }


    table m_meter {
        key = {
            hdr.ipv4.srcAddr: lpm;
        }
        actions = {
            m_update;
            NoAction;
        }
        default_action = NoAction;
        size = 1024;
    }

    table m_filter {
        key = {
            meta.meter_tag: exact;
        }
        actions = {
            drop;
            NoAction;
        }
        default_action = NoAction;
        size = 16;
    }

    apply {
        m_meter.apply();
        m_filter.apply();

        check_is_ingress_border.apply();
        if(meta.is_ingress_border == 1){
            //valid ip but no vlan header
            if(hdr.ipv4.isValid() && !hdr.vlan.isValid()){
                fec_to_vlan.apply();
            }
        }
        if (hdr.ipv4.isValid()) {
            ipv4_lpm.apply();
        }

        debug.apply(standard_metadata, meta.meter_tag);
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    action egress_border(){
        hdr.vlan.setInvalid();
        hdr.ethernet.etherType = TYPE_IPV4;
    }

    table check_is_egress_border {
        key = {
            standard_metadata.egress_port: exact;
        }
        actions = {
            egress_border;
            NoAction;
        }
        size = CONST_MAX_PORTS;
        default_action = NoAction;
    }


    apply { 
        hdr.udp.dstPort = (bit<16>) meta.meter_tag;
        if (hdr.vlan.isValid()){
            check_is_egress_border.apply();
        }     
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply {
        update_checksum(
            hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.ecn,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

//switch architecture
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;