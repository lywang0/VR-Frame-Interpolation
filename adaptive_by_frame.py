import os
import cv2
import numpy as np
from utils.configuration import DATA_DIR, RESULTS_DIR
from skimage.metrics import structural_similarity as ssim
from moviepy.editor import ImageSequenceClip
from utils.metric_utils import compute_ssim
from utils.video_utils import load_video_frames

def adaptive_interpolate_by_frame(input_path, mean_path, rife_path, output_path, threshold=0.98):
    """
    对每对原始帧计算 SSIM, 根据阈值从 mean/rife 插帧中选择对应帧进行拼接输出。
    """
    original_frames = load_video_frames(input_path)  # 原始 30帧
    mean_frames = load_video_frames(mean_path)       # 60帧
    rife_frames = load_video_frames(rife_path)       # 59帧

    assert len(mean_frames) == 2 * len(original_frames) 
    assert len(rife_frames) == 2 * len(original_frames) - 1


    adaptive_frames = []
    decision_log = []

    for i in range(len(original_frames) - 1):
        f1 = original_frames[i]
        f2 = original_frames[i + 1]
        adaptive_frames.append(f1)  # 加入原始帧

        # 计算 SSIM
        ssim_score = compute_ssim(f1, f2)

        interp_frame = (
            mean_frames[2 * i + 1]
            if ssim_score > threshold
            else rife_frames[i]
        )
        source = "MEAN" if ssim_score > threshold else "RIFE"
        adaptive_frames.append(interp_frame)

        decision_log.append(f"frame_{i}-{i+1} SSIM={ssim_score:.4f} METHOD={source}")

    adaptive_frames.append(original_frames[-1])  # 加入最后一帧

    # 写视频
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rgb_frames = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in adaptive_frames]
    clip = ImageSequenceClip(rgb_frames, fps=60)
    clip.write_videofile(output_path, codec="libx264", audio=False, verbose=False, logger=None)

    # 写日志
    log_path = os.path.join(os.path.dirname(output_path), "adaptive_interp_by_frame_latency_log.txt")
    with open(log_path, "a") as f:
        for line in decision_log:
            f.write(os.path.basename(output_path) + "\t" + line + "\n")

    print(f"Done: {os.path.basename(output_path)}")



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=0.98,
        help="平均 SSIM 阈值(默认: 0.98)"
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
                    f"adaptive_interp_by_frame_{args.threshold}",
                    f"{name}_adaptive.mp4"
                )

                if os.path.exists(input_path):
                    adaptive_interpolate_by_frame(
                        input_path,
                        mean_path,
                        rife_path,
                        output_path,
                        threshold=args.threshold,
                    )
                    print(f"Completed {name} (threshold={args.threshold})")
                else:
                    print(f"Skip missing block: {name}")
