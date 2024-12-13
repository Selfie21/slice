import os
from p4utils.utils.compiler import BF_P4C
from p4utils.mininetlib.network_API import NetworkAPI

SDE = os.environ["SDE"]
SDE_INSTALL = SDE + "/install"
net = NetworkAPI(auto_arp_tables=True)

# Network general options
net.setLogLevel('info')
net.setCompiler(compilerClass=BF_P4C, sde=SDE, sde_install=SDE_INSTALL)

# Network definition
net.addTofino("s1", sde=SDE, sde_install=SDE_INSTALL)
net.setP4SourceAll("../slice/slice.p4")

net.addHost("h11")
net.addHost("h12")


net.addLink("s1", "h11")
net.addLink("s1", "h12")

# Assignment strategy
net.mixed()

# Nodes general options
net.enablePcapDumpAll()
net.enableLogAll()

# Start the network
net.startNetwork()
