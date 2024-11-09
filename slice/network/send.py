#!/usr/bin/env python3
import datetime
import sys
import socket

from scapy.all import sendp, get_if_list, get_if_hwaddr, get_if_addr
from scapy.all import Ether, IP, UDP, TCP


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
        print("pass 1 arguments: <destination> <bandwidth Packets/s>")
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    packets_per_second = int(sys.argv[2])
    interval = 1 / packets_per_second
    count = TIME_TO_SEND / interval
    payload = "hola muchacho"

    print("Packet that will be sent:")
    pkt = Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff")
    pkt = pkt / IP(src=get_if_addr(iface), dst=addr) / UDP(sport=42, dport=42) / payload
    # pkt = pkt / IP(src=get_if_addr(iface), dst=addr) / TCP(dport=5001, sport=random.randint(2000,65535), flags='S', seq=random.randint(1000, 9000), ack=0) / payload
    pkt.show()

    print(
        f"sending on interface {iface} to {str(addr)} with a bandwidth of {packets_per_second} packets/second (UDP packages) Duration: {TIME_TO_SEND} seconds"
    )
    start = datetime.datetime.now()
    sendp(pkt, iface=iface, verbose=False, inter=interval, count=count)
    end = datetime.datetime.now()
    print(f"Sending took {end - start}")


if __name__ == "__main__":
    main()
