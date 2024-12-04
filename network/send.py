#!/usr/bin/env python3
import datetime
import sys
import socket

from scapy.all import sendp, get_if_list, get_if_hwaddr, get_if_addr
from scapy.all import Ether, IP, IPv6, UDP, TCP


def get_if():
    iface = None  # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface = i
            break
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface


def main():
    TIME_TO_SEND = 10

    if len(sys.argv) < 3:
        print("pass 1 arguments: <destination> <bandwidth kilobits_per_second>")
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    kilobits_per_second = int(sys.argv[2]) 
    iface = get_if()

    payload = "hola sarai, te amo"
    payload_size = len(payload)
    ether_ip_udp_headers_size = 14 + 20 + 8  # Ethernet (14) + IP (20) + UDP (8) headers
    total_packet_size = payload_size + ether_ip_udp_headers_size 

    total_packet_size_bits = total_packet_size * 8  # Convert bytes to bits
    bits_per_second = kilobits_per_second * 1000
    packets_per_second = bits_per_second / total_packet_size_bits
    interval = 1 / packets_per_second
    count = int(TIME_TO_SEND / interval)


    # Construct IP Packet
    pkt = Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff")
    pkt = pkt / IP(src=get_if_addr(iface), dst=addr) / UDP(sport=23, dport=26) / payload
    # pkt = pkt / IP(src=get_if_addr(iface), dst=addr) / TCP(dport=5001, sport=random.randint(2000,65535), flags='S', seq=random.randint(1000, 9000), ack=0) / payload
    pkt.show()

    print(
        f"sending on interface {iface} to {str(addr)} with a bandwidth of {kilobits_per_second} kilobits_per_second (UDP packages) Duration: {TIME_TO_SEND} seconds"
    )
    start = datetime.datetime.now()
    sendp(pkt, iface=iface, verbose=True, inter=interval, count=count)
    end = datetime.datetime.now()
    print(f"Sending took {end - start}")


if __name__ == "__main__":
    main()
