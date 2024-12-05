from scapy.all import sniff, get_if_list

def get_if():
    ifaces_list = [(index, item) for index, item in enumerate(get_if_list())]
    print(ifaces_list)
    index = input("Choose interface to listen from: ")
    return ifaces_list[int(index)][1]

counter = 0
def handle_pkt(pkt):
    global counter  # Access the global counter
    counter += 1
    print(f"Packet count: {counter}")
    # pkt.show()

def main():
    iface = get_if()
    print(f"Listening on {iface}")
    sniff(iface=iface, prn=handle_pkt, store=0)


if __name__ == "__main__":
    main()
