import json
import pandas as pd
from pprint import pprint

EXPERIMENT_NAME = "experiment_5"
FILE_PATH = f"/home/selfie/Documents/pro/p4slice/slice/test_data/{EXPERIMENT_NAME}/"
PORTS_START = ["ports_start_1.json", "ports_start_2.json", "ports_start_3.json"]
PORTS_END = ["ports_end_1.json", "ports_end_2.json", "ports_end_3.json"]
GIGABIT = 1000000000
DECIMAL_PLACES = 10
final_sum = ""


for i in range(len(PORTS_START)):
    with open(FILE_PATH + PORTS_START[i], "r") as fd:
        data = json.load(fd)

    extracted_values = {
        "tx_rate_l1": data["tx_rate_l1"],
        "tx_rate_l2": data["tx_rate_l2"],
        "rx_rate_l1": data["rx_rate_l1"],
        "rx_rate_l2": data["rx_rate_l2"]
    }
    df_start = pd.DataFrame(extracted_values)

for i in range(len(PORTS_END)):
    RUN_NUMBER = i + 1
    with open(FILE_PATH + PORTS_END[i], "r") as fd:
        data = json.load(fd)

    extracted_values = {
        "tx_rate_l1": data["tx_rate_l1"],
        "tx_rate_l2": data["tx_rate_l2"],
        "rx_rate_l1": data["rx_rate_l1"],
        "rx_rate_l2": data["rx_rate_l2"]
    }
    df_end = pd.DataFrame(extracted_values)
    df_all = pd.concat([df_start, df_end])

    # Calculate averages and convert to Gigabit/s
    df_all.drop("48", inplace=True)
    df_all.drop("56", inplace=True)

    df_all["tx_rate_l1"] = (df_all["tx_rate_l1"].values / GIGABIT).round(decimals=DECIMAL_PLACES)
    df_all["tx_rate_l2"] = (df_all["tx_rate_l2"].values / GIGABIT).round(decimals=DECIMAL_PLACES)
    df_all["rx_rate_l1"] = (df_all["rx_rate_l1"].values / GIGABIT).round(decimals=DECIMAL_PLACES)
    df_all["rx_rate_l2"] = (df_all["rx_rate_l2"].values / GIGABIT).round(decimals=DECIMAL_PLACES)

    df_all.to_csv(f"/home/selfie/Documents/pro/p4slice/slice/graphs/experiment_5/{EXPERIMENT_NAME}_{RUN_NUMBER}.csv", sep=',')
    print(df_all)


    tx_rate_l1 = round(float(df_all["tx_rate_l1"].sum()), DECIMAL_PLACES)
    tx_rate_l2 = round(float(df_all["tx_rate_l2"].sum()), DECIMAL_PLACES)
    rx_rate_l1 = round(float(df_all["rx_rate_l1"].sum()), DECIMAL_PLACES)
    rx_rate_l2 = round(float(df_all["rx_rate_l2"].sum()), DECIMAL_PLACES)
    output_string = (
        f"\nRUN {RUN_NUMBER}\n"
        f"tx_rate_l1: {tx_rate_l1}\n"
        f"tx_rate_l2: {tx_rate_l2}\n"
        f"rx_rate_l1: {rx_rate_l1}\n"
        f"rx_rate_l2: {rx_rate_l2}\n"
    )
    final_sum += output_string

with open(f"/home/selfie/Documents/pro/p4slice/slice/graphs/experiment_5/{EXPERIMENT_NAME}_SUM.txt", 'w') as file:
    file.write(final_sum)
