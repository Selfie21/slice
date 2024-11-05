import os
import sys
import socket
from datetime import datetime, timedelta

# Add custom bfrt required packages to python path so they are usable
SDE_INSTALL = os.environ["SDE_INSTALL"]
SDE_PYTHON2 = os.path.join(SDE_INSTALL, "lib", "python2.7", "site-packages")
sys.path.append(SDE_PYTHON2)
sys.path.append(os.path.join(SDE_PYTHON2, "tofino"))

PYTHON3_VER = "{}.{}".format(sys.version_info.major, sys.version_info.minor)
SDE_PYTHON3 = os.path.join(SDE_INSTALL, "lib", "python" + PYTHON3_VER, "site-packages")
sys.path.append(SDE_PYTHON3)
sys.path.append(os.path.join(SDE_PYTHON3, "tofino"))
sys.path.append(os.path.join(SDE_PYTHON3, "tofino", "bfrt_grpc"))


# Connect to the BF Runtime Server
import bfrt_grpc.client as gc
from tabulate import tabulate


client_id = 0
try:
    interface = gc.ClientInterface(
        grpc_addr="localhost:50052", client_id=client_id, device_id=0, num_tries=1
    )
    print("Connected to BF Runtime Server as client", client_id)
except:
    print("Could not connect to BF Runtime server")
    quit


# Get the information about the running program and bind pipeline
bfrt_info = interface.bfrt_info_get()
print("The target runs the program ", bfrt_info.p4_name_get())
if client_id == 0:
    interface.bind_pipeline_config(bfrt_info.p4_name_get())
dev_tgt = gc.Target(0)


# Base Info
data = []
for name in bfrt_info.table_dict.keys():
    if name.split(".")[0] == "pipe":
        # pdb.set_trace()
        t = bfrt_info.table_get(name)
        table_name = t.info.name_get()
        if table_name != name:
            continue
        table_type = t.info.type_get()
        try:
            result = t.usage_get(dev_tgt)
            table_usage = next(result)
        except:
            table_usage = "n/a"
        table_size = t.info.size_get()
        data.append([table_name, table_type, table_usage, table_size])
print(tabulate(data, headers=["Full Table Name", "Type", "Usage", "Capacity"]))


# Receive meter data
meter_dict = bfrt_info.table_get("Ingress.meter")
meter_table = bfrt_info.table_get("Ingress.m_meter")

METER_TYPE = "packets"
METER_INDEX = 1
param_name = {
    "bytes": ["$METER_SPEC_CIR_KBPS", "$METER_SPEC_PIR_KBPS", "$METER_SPEC_CBS_KBITS", "$METER_SPEC_PBS_KBITS"],
    "packets": ["$METER_SPEC_CIR_PPS", "$METER_SPEC_PIR_PPS", "$METER_SPEC_CBS_PKTS", "$METER_SPEC_PBS_PKTS"]
}
CIR = 20
PIR = 40
CBS = 10
PBS = 20

key = meter_dict.make_key([gc.KeyTuple("$METER_INDEX", METER_INDEX)])
data = meter_dict.make_data(
    [
        gc.DataTuple(param_name[METER_TYPE][0], CIR),
        gc.DataTuple(param_name[METER_TYPE][1], PIR),
        gc.DataTuple(param_name[METER_TYPE][2], CBS),
        gc.DataTuple(param_name[METER_TYPE][3], PBS),
    ]
)


meter_dict.entry_add(dev_tgt, [key], [data])

resp = meter_dict.entry_get(dev_tgt, [key], {"from_hw": False})
for data, key in resp:
    data_dict = data.to_dict()
    key_dict = key.to_dict()
    print(f"Programmed table succesfully: {data_dict}")


# Receive digests
base_model = bfrt_info.learn_get("digest_inst")

while(True):
    try:
        digest = interface.digest_get(timeout=10)
        device_id = digest.target.device_id
        pipe_id = digest.target.pipe_id
        data_list = base_model.make_data_list(digest)

        for item in data_list:
            data_dict = item.to_dict()
            meter_tag = data_dict["meterTag"]
            print(f"Meter Tag: {meter_tag}")
            #print(f"Digest ID: {id} srcAddr: {src_addr} dstAddr: {dst_addr}")

    except RuntimeError as e:
        print("No digest message received this cycle!")