from scapy.all import sniff, get_if_list


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
    pkt.show()


def main():
    sniff(iface=iface, prn=lambda x: handle_pkt(x), filter="udp", store=0)


if __name__ == "__main__":
    main()
