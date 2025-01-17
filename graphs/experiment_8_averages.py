import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = []
with open("/home/selfie/Documents/pro/p4slice/slice/graphs/experiment_8/experiment_8_ver_4_AVERAGES.txt", "r") as file:
    current_allocation = None
    for line in file:
        if line.startswith("RUN"):
            match = re.search(r"_(\d+)\.json", line)
            if match:
                current_allocation = int(match.group(1))
                if current_allocation == 775:
                    current_allocation = 77.5
        elif "Averages from 0-30 seconds" in line:
            #_ = float(next(file).strip().split(":")[1])
            #_ = float(next(file).strip().split(":")[1])
            #_ = float(next(file).strip().split(":")[1])
            packet_loss_0_30 = float(next(file).strip().split(":")[1])
        elif "Averages from 30-60 seconds" in line:
            #_ = float(next(file).strip().split(":")[1])
            #_ = float(next(file).strip().split(":")[1])
            #_ = float(next(file).strip().split(":")[1])
            packet_loss_30_60 = float(next(file).strip().split(":")[1])
            if current_allocation is not None:
                data.append({
                    "Allocation (%)": current_allocation,
                    "Time Interval": "0-30 seconds",
                    "Packet Loss (%)": packet_loss_0_30
                })
                data.append({
                    "Allocation (%)": current_allocation,
                    "Time Interval": "30-60 seconds",
                    "Packet Loss (%)": packet_loss_30_60
                })
df = pd.DataFrame(data)

plt.figure(figsize=(12, 6))
sns.barplot(
    data=df, 
    x="Allocation (%)", 
    y="Packet Loss (%)", 
    hue="Time Interval",
    palette="viridis"
)
metric = "Bandwidth [Mbit/s]"
plt.title(metric + " vs Allocation limited by P4Slice", fontsize=14)
plt.xlabel("Allocation limited by P4Slice (%)", fontsize=12)
plt.ylabel(f"{metric} over Time Interval [average]", fontsize=12)
plt.legend(title="Time Interval", fontsize=10)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"/home/selfie/Documents/pro/p4slice/slice/graphs/experiment_8/allocation_{metric.replace("/","")}.png", dpi=400)
plt.show()
