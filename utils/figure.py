import re
from collections import defaultdict
import matplotlib.pyplot as plt
from configuration import RESULTS_DIR
import os

psnr_path = os.path.join(RESULTS_DIR, "latency_psnr_summary.txt")

psnr_dict = {}
latency_dict = defaultdict(dict)

with open(psnr_path, "r") as f:
    current_method = None
    section = None
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith("==="):
            if "PSNR" in line:
                section = "psnr"
            elif "Latency" in line:
                section = "latency"
            continue

        if section == "psnr":
            match = re.match(r"(\w+(?:_\d+\.\d+)?): Avg PSNR = ([\d.]+)", line)
            if match:
                method, value = match.groups()
                psnr_dict[method] = float(value)

        elif section == "latency":
            if not line.startswith("Second"):
                current_method = line.replace(":", "")
            else:
                match = re.match(r"Second (\d+): ([\d.]+) s", line)
                if match:
                    sec, val = match.groups()
                    latency_dict[current_method][int(sec)] = float(val)

# === Plot 1: PSNR Bar Chart ===
plt.figure(figsize=(8, 5), dpi=300)
sorted_psnr = dict(sorted(psnr_dict.items(), key=lambda x: -x[1]))
bars = plt.bar(sorted_psnr.keys(), sorted_psnr.values(), color='cornflowerblue')

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height + 0.5,
             f"{height:.2f}", ha='center', va='bottom', fontsize=8)
plt.title("Average PSNR per Method")
plt.ylabel("PSNR (dB)")
plt.xticks(rotation=30)
plt.grid(axis='y')
plt.tight_layout()
plt.savefig("./results/psnr.png")
plt.show()

# === Plot 2: Latency Line Chart ===
plt.figure(figsize=(10, 6),dpi=300)
seconds = [1, 2, 3, 4, 5]
for method, sec_dict in latency_dict.items():
    y_vals = [sec_dict.get(sec, 0) for sec in seconds]
    plt.plot(seconds, y_vals, marker='o', label=method)

plt.title("Average Latency per Second")
plt.xlabel("Second")
plt.ylabel("Latency (s)")
plt.xticks(seconds)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("./results/latency.png")
plt.show()
