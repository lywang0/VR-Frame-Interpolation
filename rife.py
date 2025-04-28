import os
import time
import subprocess
from utils.configuration import DATA_DIR, RESULTS_DIR, RIFE_DIR

def run_rife_inference(log_path="rife_latency_log.txt"):
    work_dir = RIFE_DIR
    data_dir = DATA_DIR
    output_dir = os.path.join(RESULTS_DIR, "rife_interp")
    os.makedirs(output_dir, exist_ok=True)

    with open(log_path, "w") as log_file:
        for t in range(1, 6):
            for x in range(6):
                for y in range(4):
                    name = f"{t}_{x}_{y}"
                    input_file = f"{name}_out.mp4"
                    output_file = f"{name}_rife.mp4"
                    input_path = os.path.join(data_dir, input_file)
                    output_path = os.path.join(output_dir, output_file)

                    if os.path.exists(input_path):
                        print(f"Processing {input_file} ...")
                        start = time.time()
                        subprocess.run([
                            "python", "inference_video.py",
                            "--exp=1",
                            f"--video={input_path}",
                            f"--output={output_path}"
                        ], cwd=work_dir)
                        elapsed = time.time() - start
                        log_line = f"{output_file}\tMETHOD=RIFE\tLATENCY={elapsed:.3f}s\n"
                        print(log_line.strip())
                        log_file.write(log_line)
                    else:
                        print(f"Skipping {input_file}, file not found.")

if __name__ == "__main__":
    run_rife_inference(f"{RESULTS_DIR}/rife_interp/rife_latency_log.txt")
    print("All RIFE interpolation completed.")
