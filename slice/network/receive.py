from scapy.all import sniff, get_if_list, Ether, Dot1Q, IP, UDP


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


count = [0, 0, 0]
iface = get_if()
print(f"listening on {iface}")


def handle_pkt(pkt):

    if IP in pkt:

        # if get_if_hwaddr(iface) == pkt[Ether].src:
        #    print("dropping packet, because sent from this iface")
        #    return
        # pkt.show()
        meter = pkt[UDP].dport
        if meter == 0:
            count[0] += 1
        elif meter == 1:
            count[1] += 1
        elif meter == 2:
            count[2] += 1

        total = count[0] + count[1] + count[2]
        print(
            f"Green {int((count[0] / total) * 100)}  Yellow {int((count[1] / total) * 100)}  Red {int((count[2] / total) * 100)} ~~ SLICE ID {pkt[Dot1Q].vlan}"
        )


def main():
    sniff(iface=iface, prn=lambda x: handle_pkt(x), filter="udp", store=0)


if __name__ == "__main__":
    main()
