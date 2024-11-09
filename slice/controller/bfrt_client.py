import os
import sys
import socket
from pprint import pprint
from tabulate import tabulate
from datetime import datetime, timedelta
from loguru import logger


SDE_INSTALL = os.environ["SDE_INSTALL"]
PYTHON3_VER = "{}.{}".format(sys.version_info.major, sys.version_info.minor)
SDE_PYTHON3 = os.path.join(SDE_INSTALL, "lib", "python" + PYTHON3_VER, "site-packages")
sys.path.append(SDE_PYTHON3)
sys.path.append(os.path.join(SDE_PYTHON3, "tofino"))
sys.path.append(os.path.join(SDE_PYTHON3, "tofino", "bfrt_grpc"))
import bfrt_grpc.client as gc
from bfrt_grpc.client import BfruntimeReadWriteRpcException

NUM_TRIES = 3
FROM_HW = False
PARAM_NAME = {
    "bytes": [
        "$METER_SPEC_CIR_KBPS",
        "$METER_SPEC_PIR_KBPS",
        "$METER_SPEC_CBS_KBITS",
        "$METER_SPEC_PBS_KBITS",
    ],
    "packets": [
        "$METER_SPEC_CIR_PPS",
        "$METER_SPEC_PIR_PPS",
        "$METER_SPEC_CBS_PKTS",
        "$METER_SPEC_PBS_PKTS",
    ],
}


class Client:
    # Wrapper to a grpc client connected to the BF Runtime
    PKT_GEN_PORT = 68

    def __init__(self, grpc_addr="localhost:50052", device_id=0):
        # Add custom bfrt required packages to python path so they are usable
        client_id = 0
        try:
            self.interface = gc.ClientInterface(
                grpc_addr=grpc_addr,
                client_id=client_id,
                device_id=device_id,
                num_tries=NUM_TRIES,
            )
            self.target = gc.Target(device_id=device_id, pipe_id=0xFFFF)
            self.bfrt_info = self.interface.bfrt_info_get()
            self.gc = gc
            logger.info(f"The target runs the program {self.bfrt_info.p4_name_get()}")
            self.interface.bind_pipeline_config(self.bfrt_info.p4_name_get())
            logger.info(f"Connected to BF Runtime Server as client {client_id}")
        except Exception as e:
            logger.exception(f"Could not connect to BF Runtime server - exiting")
            self.interface = None
            sys.exit(1)

    def get_base_info(self):
        logger.info("Getting base info of tables")
        data = []
        for name in self.bfrt_info.table_dict.keys():
            if name.split(".")[0] == "pipe":
                t = self.bfrt_info.table_get(name)
                table_name = t.info.name_get()
                if table_name != name:
                    continue
                table_type = t.info.type_get()
                try:
                    result = t.usage_get(self.target)
                    table_usage = next(result)
                except:
                    table_usage = "n/a"
                table_size = t.info.size_get()
                data.append([table_name, table_type, table_usage, table_size])
        print(tabulate(data, headers=["Full Table Name", "Type", "Usage", "Capacity"]))

    def _get_table(self, table_name):
        return self.bfrt_info.table_get(table_name)

    def info_table(self, table):
        logger.info(f"Getting Information on Table: {table.info.name_get()}")
        table_info = table.info
        table_name = table_info.name_get()
        table_size = table_info.size_get()
        table_type = table_info.type_get()
        print(f"\nName: {table_name}\nSize: {table_size}\nType: {table_type}\n")

        key_field_info = []
        for key_field in table_info.key_field_name_list_get():
            df_type = table_info.key_field_type_get(key_field)
            df_size = table_info.key_field_size_get(key_field)
            kf_match_type = table_info.key_field_match_type_get(key_field)
            key_field_info.append((key_field, df_type, df_size[1], kf_match_type))
        print(
            tabulate(
                key_field_info,
                headers=["Key Field Name", "Type", "Size (bits)", "Match Type"],
            )
        )

        action_info = []
        for action in table_info.action_name_list_get():
            print(f"\nData fields for action: {action}")
            for data_field in table_info.data_field_name_list_get(action):
                df_type = table_info.data_field_type_get(data_field, action_name=action)
                df_size = table_info.data_field_size_get(data_field, action_name=action)
                df_required = table_info.data_field_mandatory_get(
                    data_field, action_name=action
                )
                action_info.append((data_field, df_type, df_size[1], df_required))
            print(
                tabulate(
                    action_info,
                    headers=["Data Field Name", "Type", "Size (bits)", "Required"],
                )
            )

    def dump_table(self, table):
        logger.info(f"Dumping Table: {table.info.name_get()}")
        resp = table.entry_get(self.target, [], {"from_hw": FROM_HW})
        for data, key in resp:
            key_dict = key.to_dict()
            data_dict = data.to_dict()
            pprint(key_dict)
            pprint(data_dict)
            print()

    def dump_entry(self, table, key):
        key = table.make_key([key])
        resp = table.entry_get(self.target, [key], {"from_hw": FROM_HW})
        for data, _ in resp:
            data_dict = data.to_dict()
            pprint(data_dict)

    def add_entry(self, table, key, data):
        try:
            table.entry_add(self.target, [key], [data])
        except BfruntimeReadWriteRpcException:
            logger.error(
                f"Error adding table entry, likely already exists trying entry_mod()"
            )
            table.entry_mod(self.target, [key], [data])
            logger.info("Modified entry succesfully!")
        except Exception:
            logger.exception(f"Adding entry failed!")

    def program_meter(self, meter, meter_index, meter_type, cir, pir, cbs, pbs):
        key = meter.make_key([gc.KeyTuple("$METER_INDEX", meter_index)])
        data = meter.make_data(
            [
                gc.DataTuple(PARAM_NAME[meter_type][0], cir),
                gc.DataTuple(PARAM_NAME[meter_type][1], pir),
                gc.DataTuple(PARAM_NAME[meter_type][2], cbs),
                gc.DataTuple(PARAM_NAME[meter_type][3], pbs),
            ]
        )
        try:
            meter.entry_add(self.target, [key], [data])
            logger.info("Succesfully programmed meter with the following information: ")
            self.dump_table(table=meter, key_name="$METER_INDEX", key_value=meter_index)
        except Exception:
            logger.exception(f"Unable to program meter!")

    def loop_digest(self, base_model):
        while True:
            self.single_digest(base_model)

    def single_digest(self, base_model):
        """
        base_model = client.bfrt_info.learn_get("digest_inst")
        base_model.info.data_field_annotation_add("srcAddr", "ipv4")
        """
        try:
            digest = self.interface.digest_get(timeout=10)
            device_id = digest.target.device_id
            pipe_id = digest.target.pipe_id
            data_list = base_model.make_data_list(digest)

            for item in data_list:
                data_dict = item.to_dict()
                pprint(data_dict)
        except RuntimeError:
            logger.exception("No digest message received this cycle!")

    def generate_packets(self, packet, interval_nanoseconds=1000000000):
        logger.info("Configuring packet gen tables to generate Packets")
        pktgen_port = self._get_table("tf1.pktgen.port_cfg")
        pktgen_buffer = self._get_table("tf1.pktgen.pkt_buffer")
        pktgen_app = self._get_table("tf1.pktgen.app_cfg")

        logger.info(f"Sending out packets with length: {len(packet)}")
        pktgen_port_key = pktgen_port.make_key(
            [gc.KeyTuple("dev_port", self.PKT_GEN_PORT)]
        )
        pktgen_port_action_data = pktgen_port.make_data(
            [gc.DataTuple("pktgen_enable", bool_val=True)]
        )
        self.add_entry(pktgen_port, pktgen_port_key, pktgen_port_action_data)

        offset = 0
        pktgen_pkt_buf_key = pktgen_buffer.make_key(
            [
                gc.KeyTuple("pkt_buffer_offset", offset),
                gc.KeyTuple("pkt_buffer_size", len(packet)),
            ]
        )
        pktgen_pkt_buf_action_data = pktgen_buffer.make_data(
            [gc.DataTuple("buffer", bytearray(bytes(packet)))]
        )
        self.add_entry(pktgen_buffer, pktgen_pkt_buf_key, pktgen_pkt_buf_action_data)

        pktgen_app_key = pktgen_app.make_key([gc.KeyTuple("app_id", 0)])
        pktgen_app_action_data = pktgen_app.make_data(
            [
                gc.DataTuple("timer_nanosec", interval_nanoseconds),
                gc.DataTuple("app_enable", bool_val=True),
                gc.DataTuple("pkt_len", len(packet)),
                gc.DataTuple("pkt_buffer_offset", 0),
                gc.DataTuple("pipe_local_source_port", 68),
                gc.DataTuple("increment_source_port", bool_val=False),
                gc.DataTuple("batch_count_cfg", 0),
                gc.DataTuple("packets_per_batch_cfg", 1),
                gc.DataTuple("ibg", 10000),
                gc.DataTuple("ibg_jitter", 0),
                gc.DataTuple("ipg", 500),
                gc.DataTuple("ipg_jitter", 1000),
                gc.DataTuple("batch_counter", 0),
                gc.DataTuple("pkt_counter", 0),
                gc.DataTuple("trigger_counter", 0),
            ],
            "trigger_timer_periodic",
        )
        self.add_entry(pktgen_app, pktgen_app_key, pktgen_app_action_data)


# TODO: Table for adding slice members
