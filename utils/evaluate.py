from video_utils import load_video_frames
import cv2, sys, os, argparse
from utils.configuration import DATA_DIR, RESULTS_DIR

def psnr(original_path, interp_path):
    ori_frames = load_video_frames(original_path)
    gen_frames = load_video_frames(interp_path)
    psnr_list = [cv2.PSNR(ori, gen) for ori, gen in zip(ori_frames, gen_frames)]
    return sum(psnr_list) / len(psnr_list)

def compare_psnr(gt_dir, result_dir, method_name, log_path="psnr_comparison_log.txt"):
    with open(log_path, "w") as log_file:
        def log(msg):
            print(msg)
            log_file.write(msg + "\n")

        total_psnr, count = 0, 0
        log(f"\nComparing method: {method_name}")
        for t in range(1, 6):
            for x in range(6):
                for y in range(4):
                    name = f"{t}_{x}_{y}"
                    gt_path = f"{gt_dir}/{name}_rife.mp4"  # RIFE 作为参考
                    pred_path = f"{result_dir}/{name}_{method_name}.mp4" 

                    if os.path.exists(gt_path) and os.path.exists(pred_path):
                        score = psnr(gt_path, pred_path)
                        log(f"{name}: PSNR = {score:.2f}")
                        total_psnr += score
                        count += 1
                    else:
                        log(f"{name}: Missing file ({method_name})")

        if count > 0:
            avg = total_psnr / count
            log(f"\nAvg PSNR for {method_name}: {avg:.2f} dB")
        else:
            log("No valid comparisons found.")
        
        log(f"\nSaved log to: {os.path.abspath(log_path)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", choices=["mean", "adaptive"], required=True,
                        help="选择要比较的插帧方法(mean 或 adaptive)")
    parser.add_argument("--threshold", type=float, default=0.98,
                        help="adaptive 方法使用的 SSIM 阈值")
    args = parser.parse_args()

    method = args.method
    if method == "adaptive":
        result_dir = os.path.join(RESULTS_DIR, f"adaptive_interp_{args.threshold}")
        log_path = os.path.join(RESULTS_DIR, "psnr", f"{method}_{args.threshold}.txt")
    else:
        result_dir = os.path.join(RESULTS_DIR, f"{method}_interp")
        log_path = os.path.join(RESULTS_DIR, "psnr", f"{method}.txt")

    gt_dir = os.path.join(RESULTS_DIR, "rife_interp")  # RIFE 是参考基准    

    compare_psnr(gt_dir, result_dir, method_name=method, log_path=log_path)
