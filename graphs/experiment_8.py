import re
import json
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

EXPERIMENT_NAME = "experiment_8_ver_4"
FILE_PATH = f"/home/selfie/Documents/pro/p4slice/slice/test_data/{EXPERIMENT_NAME}/"
SAMPLES_SERVER = ["server1_64_10.json", "server1_64_25.json", "server1_64_50.json", "server1_64_75.json", "server1_64_775.json", "server1_64_80.json", "server1_64_85.json", "server1_64_99.json"]
SAMPLES_PING = ["ping1_64_10.log", "ping1_64_25.log", "ping1_64_50.log", "ping1_64_75.log", "ping1_64_775.log", "ping1_64_80.log", "ping1_64_85.log", "ping1_64_99.log"] 
#SAMPLES_SERVER = ["server1_128.json"]
#SAMPLES_PING = ["ping1_128.log"]
final_averages = ""
DECIMAL_PLACES = 4

# Prepare Data
for i in range(len(SAMPLES_SERVER)):
    RUN_NUMBER = i + 1
    sample = SAMPLES_SERVER[i]
    print(f"Processing {sample}")
    with open(FILE_PATH + sample, "r") as fd:
        data = json.load(fd)
    intervals = data["intervals"]
    
    parsed_data = [
        {
            "start": round(interval["sum"]["start"]),
            "end": round(interval["sum"]["end"]),
            "bits_per_second": interval["sum"]["bits_per_second"] / 1000000,
            "jitter": interval["sum"]["jitter_ms"],
            "lost_packets": interval["sum"]["lost_percent"]
        }
        for interval in intervals
    ]
    df = pd.DataFrame(parsed_data)

    # Ping Responses
    icmp_seq = []
    rtt = []
    with open(FILE_PATH + SAMPLES_PING[i], "r") as file:
        for line in file:
            seq_match = re.search(r"icmp_seq=(\d+)", line)
            time_match = re.search(r"time=([\d.]+)", line)
            
            if seq_match and time_match and int(seq_match.group(1)) <= 60:
                icmp_seq.append(int(seq_match.group(1)))
                rtt.append(float(time_match.group(1)))
    
    
    # Create a DataFrame for the new data from icmp_seq and rtt
    icmp_data = pd.DataFrame({"index": icmp_seq, "rtt": rtt})
    icmp_data.set_index("index", inplace=True)
    df.set_index("end", inplace=True) 
    df = df.merge(icmp_data, left_index=True, right_index=True, how="left")

    # Averages without attack and during attack
    data_0_30 = df[(df["start"] >= 0) & (df["start"] <= 30)]
    data_30_60 = df[(df["start"] > 30) & (df["start"] <= 60)]

    average_0_30_bits_per_second = round(data_0_30["bits_per_second"].mean(axis=0), DECIMAL_PLACES)
    average_0_30_jitter = round(data_0_30["jitter"].mean(axis=0), DECIMAL_PLACES)
    average_0_30_lost_packets = round(data_0_30["lost_packets"].mean(axis=0), DECIMAL_PLACES)
    average_0_30_rtt = round(data_0_30["rtt"].mean(axis=0), DECIMAL_PLACES)
    average_30_60_bits_per_second = round(data_30_60["bits_per_second"].mean(axis=0), DECIMAL_PLACES)
    average_30_60_jitter = round(data_30_60["jitter"].mean(axis=0), DECIMAL_PLACES)
    average_30_60_lost_packets = round(data_30_60["lost_packets"].mean(axis=0), DECIMAL_PLACES)
    average_30_60_rtt = round(data_30_60["rtt"].mean(axis=0), DECIMAL_PLACES)

    # File output
    output_string = (
        f"\nRUN {sample}\n"
        "Averages from 0-30 seconds:\n"
        f"Bits per Second: {average_0_30_bits_per_second}\n"
        f"Jitter: {average_0_30_jitter}\n"
        f"Packet Loss: {average_0_30_lost_packets}\n"
        f"RTT: {average_0_30_rtt}\n"
        "\nAverages from 30-60 seconds:\n"
        f"Bits per Second: {average_30_60_bits_per_second}\n"
        f"Jitter: {average_30_60_jitter}\n"
        f"Packet Loss: {average_30_60_lost_packets}\n"
        f"RTT: {average_30_60_rtt}\n"
    )

    # Plots
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)

    sns.lineplot(x=df["start"], y=df["bits_per_second"], ax=axes[0], color="royalblue", marker="o", label="Mbit/s")
    axes[0].set_ylabel("Bandwidth [Mbit/s]")
    axes[0].legend()
    axes[0].grid(True)

    sns.lineplot(x=df["start"], y=df["jitter"], ax=axes[1], color="seagreen", marker="^", label="Jitter")
    axes[1].set_ylabel("Jitter [ms]")
    axes[1].legend()
    axes[1].grid(True)

    sns.lineplot(x=df["start"], y=df["lost_packets"], ax=axes[2], color="tomato", marker="s", label="Percentage Packet Loss")
    axes[2].set_ylabel("Packet Loss %")
    axes[2].legend()
    axes[2].grid(True)

    sns.lineplot(x=df["start"], y=df["rtt"], ax=axes[3], color="dodgerblue", marker="x", label="Round Trip Time")
    axes[3].set_ylabel("RTT [ms]")
    axes[3].legend()
    axes[3].grid(True)

    for ax in axes:
        ax.axvline(x=30, color="darkorange", linestyle="--")
        ax.text(30, ax.get_ylim()[1], "Time of Attack", color="darkorange", ha="center", va="bottom", fontsize=12)

    axes[2].set_xlabel("Time in Seconds")
    plt.tight_layout()
    plt.savefig(f"/home/selfie/Documents/pro/p4slice/slice/graphs/experiment_8/{EXPERIMENT_NAME}_{sample}.png", dpi=400)
    #plt.show()

    final_averages += output_string

with open(f"/home/selfie/Documents/pro/p4slice/slice/graphs/experiment_8/{EXPERIMENT_NAME}_AVERAGES.txt", 'w') as file:
    file.write(final_averages)
print(final_averages)