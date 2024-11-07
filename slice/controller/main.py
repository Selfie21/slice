import sys
from bfrt_client import Client
from loguru import logger
    
logger.remove(0)
logger.add(sys.stderr, level="DEBUG", diagnose=False)
client = Client()
client.get_base_info()

t = client.dump_table("Ingress.meter")
client.info_table("Ingress.m_meter")

base_model = client.bfrt_info.learn_get("digest_inst")
client.loop_digest(base_model)