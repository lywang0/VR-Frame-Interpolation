import os
import re
from collections import defaultdict
from configuration import RESULTS_DIR

def parse_latency_logs(results_dir, output_log="latency_psnr_summary.txt"):
    second_latency = defaultdict(lambda: defaultdict(list))  # method+threshold -> second -> list[latency]
    interp_dirs = [d for d in os.listdir(results_dir) if "interp" in d]
    
    for d in interp_dirs:
        dir_path = os.path.join(results_dir, d)

        # method 设为 mean、rife、adaptive_0.6 等
        if d.startswith("adaptive_interp_"):
            threshold = d.split("_")[-1]
            method = f"adaptive_{threshold}"
        else:
            method = d.split("_")[0]  # mean or rife

        log_filename = f"{method.split('_')[0]}_latency_log.txt"  # mean_latency_log.txt / rife_latency_log.txt / adaptive_latency_log.txt
        log_path = os.path.join(dir_path, log_filename)
        if not os.path.exists(log_path):
            continue

        with open(log_path, "r") as f:
            for line in f:
                match = re.match(r"(\d+)_\d+_\d+.*LATENCY=([\d.]+)s", line)
                if match:
                    sec = int(match.group(1))
                    latency = float(match.group(2))
                    second_latency[method][sec].append(latency)

    # 汇总平均延时
    latency_summary = {}
    for method in second_latency:
        latency_summary[method] = {}
        for sec in range(1, 6):
            vals = second_latency[method].get(sec, [])
            avg = sum(vals) / len(vals) if vals else 0
            latency_summary[method][sec] = avg

    return latency_summary


def parse_psnr_logs(psnr_dir):
    import re
    psnr_summary = {}

    for fname in os.listdir(psnr_dir):
        if not fname.endswith(".txt"):
            continue

        method = fname.replace(".txt", "")  # e.g., "adaptive_0.6"
        if method not in psnr_summary:
            psnr_summary[method] = []

        with open(os.path.join(psnr_dir, fname), "r") as f:
            lines = f.readlines()
            if len(lines) >= 124:
                line = lines[123]  # 第 124 行
                match = re.search(r"Avg PSNR.*?: ([\d.]+)", line)
                if match:
                    psnr_value = float(match.group(1))
                    psnr_summary[method].append(psnr_value)

    return psnr_summary


def write_summary_to_log(latency_summary, psnr_summary, output_path="latency_psnr_summary.txt"):
    with open(output_path, "w") as log:
        log.write("=== PSNR Summary ===\n")
        for method, psnrs in psnr_summary.items():
            avg_psnr = sum(psnrs) / len(psnrs) if psnrs else 0
            log.write(f"{method}: Avg PSNR = {avg_psnr:.2f} dB\n")

        log.write("\n=== Latency Summary per Second ===\n")
        for method in latency_summary:
            log.write(f"\n{method}:\n")
            for sec in range(1, 6):
                avg = latency_summary[method].get(sec, 0)
                log.write(f"  Second {sec}: {avg:.3f} s\n")

results_dir = RESULTS_DIR
psnr_dir = os.path.join(results_dir, "psnr")
latency_summary = parse_latency_logs(results_dir)
psnr_summary = parse_psnr_logs(psnr_dir)
write_summary_to_log(latency_summary, psnr_summary, f"{psnr_dir}/latency_psnr_summary.txt")
