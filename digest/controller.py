import os
import sys

# Add custom bfrt required packages to python path so they are usable 
SDE_INSTALL   = os.environ['SDE_INSTALL']
SDE_PYTHON2   = os.path.join(SDE_INSTALL, 'lib', 'python2.7', 'site-packages')
sys.path.append(SDE_PYTHON2)
sys.path.append(os.path.join(SDE_PYTHON2, 'tofino'))

PYTHON3_VER   = '{}.{}'.format(
    sys.version_info.major,
    sys.version_info.minor)
SDE_PYTHON3   = os.path.join(SDE_INSTALL, 'lib', 'python' + PYTHON3_VER,
                             'site-packages')
sys.path.append(SDE_PYTHON3)
sys.path.append(os.path.join(SDE_PYTHON3, 'tofino'))
sys.path.append(os.path.join(SDE_PYTHON3, 'tofino', 'bfrt_grpc'))


# Connect to the BF Runtime Server
import bfrt_grpc.client as gc
from tabulate import tabulate
from datetime import datetime, timedelta
from pprint import pprint

client_id = 0
try:
    interface = gc.ClientInterface(
        grpc_addr = 'localhost:50052',
        client_id = client_id,
        device_id = 0,
        num_tries = 1)
    print('Connected to BF Runtime Server as client', client_id)
except:
    print('Could not connect to BF Runtime server')
    quit


# Get the information about the running program and bind pipeline
bfrt_info = interface.bfrt_info_get()
print('The target runs the program ', bfrt_info.p4_name_get())
if client_id == 0:
    interface.bind_pipeline_config(bfrt_info.p4_name_get())


# Base Info
dev_tgt = gc.Target(0)
data = []
for name in bfrt_info.table_dict.keys():
    if name.split('.')[0] == 'pipe':
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
            table_usage = 'n/a'
        table_size = t.info.size_get()
        data.append([table_name, table_type, table_usage, table_size])
print(tabulate(data, headers=['Full Table Name','Type','Usage','Capacity']))


# Process digests
srcAddr = {}
dstAddr = {}

def insert_data(key, table):
    if key in table:
        srcAddr[key] = srcAddr[key] + 1
    else:
        srcAddr[key] = 1


# Receive digests
base_model = bfrt_info.learn_get("digest_inst")
base_model.info.data_field_annotation_add("srcAddr", "ipv4")
base_model.info.data_field_annotation_add("dstAddr", "ipv4")
now = datetime.now()
next_print = now + timedelta(seconds=3)

while(True):
    try:
        now = datetime.now()
        digest = interface.digest_get(timeout=10)

        device_id = digest.target.device_id
        pipe_id = digest.target.pipe_id
        data_list = base_model.make_data_list(digest)

        for item in data_list:
            data_dict = item.to_dict()
            src_addr = data_dict["srcAddr"]
            dst_addr = data_dict["dstAddr"]
            id = data_dict["id"]
            insert_data(key=src_addr, table=srcAddr)
            #print(f"Device ID: {device_id} Pipe ID: {pipe_id}")
            #print(f"Digest ID: {id} srcAddr: {src_addr} dstAddr: {dst_addr}")
        
        if now > next_print:
            srcAddr_sorted = sorted(srcAddr.items(), key=lambda x: x[1])
            print("################################ NEW DATA ################################\n")
            pprint(srcAddr_sorted)
            next_print = now + timedelta(seconds=3)

    except RuntimeError as e:
        print("No digest message received this cycle!")
