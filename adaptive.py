from utils.metric_utils import average_ssim_for_block
from utils.video_utils import load_video_frames
from utils.video_utils import interpolate_by_mean
from utils.configuration import DATA_DIR, RESULTS_DIR, RIFE_DIR
import os, subprocess
import time

def run_rife_live(input_path, output_path, work_dir=RIFE_DIR, exp=1):
    cmd = [
        "python", "inference_video.py",
        f"--exp={exp}",
        f"--video={input_path}",
        f"--output={output_path}"
    ]
    subprocess.run(cmd, cwd=work_dir, check=True)


def adaptive_interpolate(input_path, mean_path, rife_path, output_path, threshold=0.98, mode='copy'):
    """
    根据帧间平均 SSIM 决定使用哪种插帧方式，并记录日志。
    copy mode: 直接拷贝已有的mean/rife结果(速度较快)
    evaluate mode: 现场插帧并测延时(如需测量插帧延时选择evaluate)
    """
    if mode == 'copy':
        frames = load_video_frames(input_path)
        avg_ssim = average_ssim_for_block(frames)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 决策
        if avg_ssim > threshold:
            method = "MEAN"
            os.system(f"cp {mean_path} {output_path}")
        else:
            method = "RIFE"
            os.system(f"cp {rife_path} {output_path}")

        # 打印信息
        block_name = os.path.basename(output_path)
        print(f"Used {method} for {block_name} | avg SSIM = {avg_ssim:.4f}")
        log_path = os.path.join(os.path.dirname(output_path), "decision_log.txt")
        with open(log_path, "a") as f:
            f.write(f"{block_name}\tSSIM={avg_ssim:.4f}\tMETHOD={method}\n")


    elif mode == 'evaluate':
        start = time.time()
        frames = load_video_frames(input_path)
        avg_ssim = average_ssim_for_block(frames)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # 决策
        if avg_ssim > threshold:
            method = "MEAN"
            interpolate_by_mean(input_path, output_path)
        else:
            method = "RIFE"
            run_rife_live(input_path, output_path)
        end = time.time()

        # 计算延迟
        elapsed = end - start
        # 打印信息（包含延迟）
        block_name = os.path.basename(output_path)
        print(f"[evaluate] {block_name} | SSIM={avg_ssim:.4f} | "
            f"{method} | Latency={elapsed:.3f}s")
        with open(f"{block_name}/adaptive_latency_log.txt", "a") as f:
            f.write(f"{block_name}\tSSIM={avg_ssim:.4f}\tMETHOD={method}\tLATENCY={elapsed:.3f}s\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=0.98,
        help="平均 SSIM 阈值(默认: 0.98)"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["copy", "evaluate"],
        default="copy",
        help="处理模式: copy(拷贝结果)、evaluate(现场插帧并测延时)"
    )
    args = parser.parse_args()

    # 直接拿 args.threshold、args.mode 用即可
    for t in range(1, 6):
        for x in range(6):
            for y in range(4):
                name = f"{t}_{x}_{y}"
                input_path = os.path.join(DATA_DIR, f"{name}_out.mp4")
                mean_path  = os.path.join(RESULTS_DIR, "mean_interp", f"{name}_mean.mp4")
                rife_path  = os.path.join(RESULTS_DIR, "rife_interp", f"{name}_rife.mp4")
                output_path = os.path.join(
                                            RESULTS_DIR,
                                            f"adaptive_interp_{args.threshold}",
                                            f"{name}_adaptive.mp4")

                if os.path.exists(input_path):
                    adaptive_interpolate(
                        input_path,
                        mean_path,
                        rife_path,
                        output_path,
                        threshold=args.threshold,
                        mode=args.mode
                    )
                    print(f"[{args.mode}] Completed {name} (threshold={args.threshold})")
                else:
                    print(f"Skip missing block: {name}")
