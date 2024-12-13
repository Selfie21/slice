import re
import json
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

FILE_PATH = "/home/selfie/Documents/pro/slice/test_data/test2/"
SAMPLES_SERVER = ["server1.json", "server2.json", "server3.json"]
SAMPLES_PING = ["ping1.log", "ping2.log", "ping3.log"]
all_data = {}

# Prepare Data
for i in range(len(SAMPLES_SERVER)):
    sample = SAMPLES_SERVER[i]
    with open(FILE_PATH + sample, "r") as fd:
        data = json.load(fd)
    intervals = data["intervals"]
    
    parsed_data = [
        {
            "start": int(interval["sum"]["start"]),
            "end": int(interval["sum"]["end"]),
            "bits_per_second": interval["sum"]["bits_per_second"] / 1000000,
            "jitter": interval["sum"]["jitter_ms"],
            "lost_packets": interval["sum"]["lost_packets"]
        }
        for interval in intervals
    ]
    df = pd.DataFrame(parsed_data)

    # Ping Responses
    icmp_seq = []
    rtt = []
    with open(FILE_PATH + SAMPLES_PING[i], 'r') as file:
        for line in file:
            seq_match = re.search(r"icmp_seq=(\d+)", line)
            time_match = re.search(r"time=([\d.]+)", line)
            
            if seq_match and time_match and int(seq_match.group(1)) <= 60:
                icmp_seq.append(int(seq_match.group(1)))
                rtt.append(float(time_match.group(1)))
    df['rtt'] = rtt

    sample_name = sample.split("/")[-1].replace(".json", "")
    all_data[sample_name] = df.set_index(["start", "end"])
merged_df = pd.concat(all_data, axis=1)
print(merged_df)

# Average
merged_df["average_bits_per_second"] = merged_df.filter(like='bits_per_second').mean(axis=1)
merged_df["average_jitter"] = merged_df.filter(like='jitter').mean(axis=1)
merged_df["average_lost_packets"] = merged_df.filter(like='lost_packets').mean(axis=1)
merged_df["average_rtt"] = merged_df.filter(like='rtt').mean(axis=1)

merged_df = merged_df.reset_index()
for sample in SAMPLES_SERVER:
    sample_name = sample.split("/")[-1].replace(".json", "")
    merged_df = merged_df.drop(columns=[(sample_name, 'bits_per_second')])
    merged_df = merged_df.drop(columns=[(sample_name, 'jitter')])
    merged_df = merged_df.drop(columns=[(sample_name, 'lost_packets')])


# Averages without attack and during attack
data_0_30 = merged_df[(merged_df['start'] >= 0) & (merged_df['start'] <= 30)]
data_30_60 = merged_df[(merged_df['start'] > 30) & (merged_df['start'] <= 60)]

# Calculate the average for the first interval (0-30 seconds)
average_0_30_bits_per_second = data_0_30["average_bits_per_second"].mean(axis=0)
average_0_30_jitter = data_0_30["average_jitter"].mean(axis=0)
average_0_30_lost_packets = data_0_30["average_lost_packets"].mean(axis=0)
average_0_30_rtt = data_0_30["average_rtt"].mean(axis=0)

# Calculate the average for the second interval (30-60 seconds)
average_30_60_bits_per_second = data_30_60["average_bits_per_second"].mean(axis=0)
average_30_60_jitter = data_30_60["average_jitter"].mean(axis=0)
average_30_60_lost_packets = data_30_60["average_lost_packets"].mean(axis=0)
average_30_60_rtt = data_30_60["average_rtt"].mean(axis=0)

# Print the results
print("Averages from 0-30 seconds:")
print(f"Average Bits per Second: {average_0_30_bits_per_second}")
print(f"Average Jitter: {average_0_30_jitter}")
print(f"Average Lost Packets: {average_0_30_lost_packets}")
print(f"Average RTT: {average_0_30_rtt}")

print("\nAverages from 30-60 seconds:")
print(f"Average Bits per Second: {average_30_60_bits_per_second}")
print(f"Average Jitter: {average_30_60_jitter}")
print(f"Average Lost Packets: {average_30_60_lost_packets}")
print(f"Average RTT: {average_30_60_rtt}")


# Plots
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)

sns.lineplot(x=df['start'], y=merged_df['average_bits_per_second'], ax=axes[0], color='royalblue', marker='o', label='Average Mbit/s')
axes[0].set_ylabel('Mbit/s')
axes[0].legend()
axes[0].grid(True)

sns.lineplot(x=df['start'], y=merged_df['average_jitter'], ax=axes[1], color='seagreen', marker='^', label='Average Jitter')
axes[1].set_ylabel('Jitter [ms]')
axes[1].legend()
axes[1].grid(True)

sns.lineplot(x=df['start'], y=merged_df['average_lost_packets'], ax=axes[2], color='tomato', marker='s', label='Average Lost Packets')
axes[2].set_ylabel('#Lost Packets')
axes[2].legend()
axes[2].grid(True)

sns.lineplot(x=df['start'], y=merged_df['average_rtt'], ax=axes[3], color='dodgerblue', marker='x', label='Average Round Trip Time')
axes[3].set_ylabel('RTT [ms]')
axes[3].legend()
axes[3].grid(True)

for ax in axes:
    ax.axvline(x=30, color='darkorange', linestyle='--')
    ax.text(30, ax.get_ylim()[1], 'Time of Attack', color='darkorange', ha='center', va='bottom', fontsize=12)

axes[2].set_xlabel('Time in Seconds')
plt.tight_layout()
plt.savefig("graphs/test2.png", dpi=400)
plt.show()


