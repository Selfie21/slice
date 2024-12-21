import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


EXPERIMENT_NAME = "experiment_5"
FILE_PATH = f"/home/selfie/Documents/pro/p4slice/slice/test_data/{EXPERIMENT_NAME}/"
PORTS_START = ["ports_start_1.json", "ports_start_2.json", "ports_start_3.json"]
PORTS_END = ["ports_end_1.json", "ports_end_2.json", "ports_end_3.json"]
GIGABIT = 1000000000
DECIMAL_PLACES = 10
colors1 = ['#B28DFF']
colors2 = ['#FFC3A0']
final_sum = ""

def convert_to_sum_df(df):
    df["tx_rate_l1"] = (df["tx_rate_l1"].values / GIGABIT).round(decimals=DECIMAL_PLACES)
    df["tx_rate_l2"] = (df["tx_rate_l2"].values / GIGABIT).round(decimals=DECIMAL_PLACES)
    df["rx_rate_l1"] = (df["rx_rate_l1"].values / GIGABIT).round(decimals=DECIMAL_PLACES)
    df["rx_rate_l2"] = (df["rx_rate_l2"].values / GIGABIT).round(decimals=DECIMAL_PLACES)

    tx_rate_l1 = round(float(df["tx_rate_l1"].sum()), DECIMAL_PLACES)
    tx_rate_l2 = round(float(df["tx_rate_l2"].sum()), DECIMAL_PLACES)
    rx_rate_l1 = round(float(df["rx_rate_l1"].sum()), DECIMAL_PLACES)
    rx_rate_l2 = round(float(df["rx_rate_l2"].sum()), DECIMAL_PLACES)
    return [tx_rate_l1, tx_rate_l2, rx_rate_l1, rx_rate_l2]


def extract_values(data):
    extracted_values = {
        "tx_rate_l1": data["tx_rate_l1"],
        "tx_rate_l2": data["tx_rate_l2"],
        "rx_rate_l1": data["rx_rate_l1"],
        "rx_rate_l2": data["rx_rate_l2"]
    }
    return extracted_values

for i in range(1):
    RUN_NUMBER = i + 1

    # Start Ports
    with open(FILE_PATH + PORTS_START[i], "r") as fd:
        data = json.load(fd)
    extracted_values = extract_values(data)
    df_start = pd.DataFrame(extracted_values)
    ports_start_values = convert_to_sum_df(df_start)

    # End Ports
    with open(FILE_PATH + PORTS_END[i], "r") as fd:
        data = json.load(fd)
    extracted_values = extract_values(data)
    df_end = pd.DataFrame(extracted_values)
    ports_end_values = convert_to_sum_df(df_end)

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

    tx_rate_l1, tx_rate_l2, rx_rate_l1, rx_rate_l2 = convert_to_sum_df(df_all)
    output_string = (
        f"\nRUN {RUN_NUMBER}\n"
        f"tx_rate_l1: {tx_rate_l1}\n"
        f"tx_rate_l2: {tx_rate_l2}\n"
        f"rx_rate_l1: {rx_rate_l1}\n"
        f"rx_rate_l2: {rx_rate_l2}\n"
    )
    final_sum += output_string

    # Plot
    labels = ["tx_rate_l1", "tx_rate_l2", "rx_rate_l1", "rx_rate_l2"]
    x = np.arange(len(labels))
    bar_width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plotting the bars
    bars_start = ax.bar(x - bar_width / 2, ports_start_values, bar_width, label="aggsw0", color=colors1)
    bars_end = ax.bar(x + bar_width / 2, ports_end_values, bar_width, label="aggsw2", color=colors2)

    # Adding labels and titles
    ax.set_xlabel("Rates")
    ax.set_ylabel("Values (Gbit/s)")
    ax.set_title("Rates of aggsw0 and aggsw2")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    # Adding value annotations
    for bars in [bars_start, bars_end]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}', 
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(f"/home/selfie/Documents/pro/p4slice/slice/graphs/experiment_5/{EXPERIMENT_NAME}_{RUN_NUMBER}.png", dpi=400)
    plt.show()

with open(f"/home/selfie/Documents/pro/p4slice/slice/graphs/experiment_5/{EXPERIMENT_NAME}_SUM.txt", 'w') as file:
    file.write(final_sum)
