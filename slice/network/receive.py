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

counter = 0

def handle_pkt(pkt):
    global counter  # Access the global counter
    counter += 1
    print(f"Packet count: {counter}")
    # Uncomment to display packet details
    # pkt.show()

def main():
    iface = get_if()
    print(f"Listening on {iface}")
    sniff(iface=iface, prn=handle_pkt, store=0)


if __name__ == "__main__":
    main()
