import pandas as pd
import json
from pprint import pprint

FILE_PATH = "/home/selfie/Documents/pro/slice/test_data/test3/"
PORTS_START = ["ports_start_1.json", "ports_start_2.json", "ports_start_3.json"]
PORTS_END = ["ports_end_1.json", "ports_end_2.json", "ports_end_3.json"]
all_data = []

for i in range(len(PORTS_START)):
    with open(FILE_PATH + PORTS_START[i], "r") as fd:
        data = json.load(fd)

    extracted_values = {
        'tx_rate_l1': data['tx_rate_l1'],
        'tx_rate_l2': data['tx_rate_l2'],
        'rx_rate_l1': data['rx_rate_l1'],
        'rx_rate_l2': data['rx_rate_l2']
    }
    # Print the extracted dictionary (optional for debugging)
    df = pd.DataFrame(extracted_values)
    all_data.append(df)

final_df = pd.concat(all_data, axis=0)
final_df = final_df.reset_index().rename(columns={'index': 'key'})
final_df.set_index('key', inplace=True)
average_values = final_df.mean(axis=0)

# Print the final DataFrame
print(average_values)
