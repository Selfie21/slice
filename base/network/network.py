from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI(auto_arp_tables=True)

# Network general options
net.setLogLevel("info")
net.enableCli()

# Network definition
net.addP4Switch("s1")
net.setP4CliInput("s1", "s1_runtime.txt")
net.addP4Switch("s2")
net.setP4CliInput("s2", "s2_runtime.txt")
net.setP4SourceAll("../meter.p4")

net.addHost("h1")
net.addHost("h11")
net.addHost("h2")
net.addHost("h22")

net.addLink("s1", "h1")
net.addLink("s1", "h2")
net.addLink("s2", "h11")
net.addLink("s2", "h22")
net.addLink(node1="s1", node2="s2", port1=3, port2=3)

# Assignment strategy
net.mixed()

# Nodes general options
net.enablePcapDumpAll()
net.enableLogAll()

# Start the network
net.startNetwork()
