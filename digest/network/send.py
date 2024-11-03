#!/usr/bin/env python3
import sys
import socket
import random
import time

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

    if len(sys.argv) < 2:
        print("pass 1 arguments: <destination>")
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()
    payload = "hola muchacho"

    print("Packet that will be sent:")
    while True:
        srcIP = f"10.0.2.{int(random.gauss(sigma=25, mu=100))}" #get_if_addr(iface)
        pkt = Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff")
        pkt = pkt / IP(src=srcIP, dst=addr) / UDP(sport=42, dport=42) / payload
        #pkt = pkt / IP(src=get_if_addr(iface), dst=addr) / TCP(dport=5001, sport=random.randint(2000,65535), flags='S', seq=random.randint(1000, 9000), ack=0) / payload
        #pkt.show()
        #print(f"sending on interface {iface} to {str(addr)} (UDP package)")
        sendp(pkt, iface=iface, verbose=False)
        time.sleep(0.05)


if __name__ == "__main__":
    main()
