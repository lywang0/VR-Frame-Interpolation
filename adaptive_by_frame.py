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
    对每对原始帧计算 SSIM, 根据阈值从 mean/rife 插帧中选择对应帧进行拼接输出，
    """
    original = load_video_frames(input_path)  # 30 帧
    mean_f   = load_video_frames(mean_path)   # 60 帧
    rife_f   = load_video_frames(rife_path)   # 59 帧

    # 补齐 RIFE 到 60 帧
    if len(rife_f) == 2 * len(original) - 1:
        rife_f.append(original[-1])

    adaptive = []
    psnr_values = []

    # 逐帧决策与 PSNR 计算
    for i in range(len(original) - 1):
        f1, f2 = original[i], original[i+1]
        adaptive.append(f1)

        score = compute_ssim(f1, f2)
        if score > threshold:
            interp = mean_f[2*i + 1]
        else:
            interp = rife_f[2*i + 1]

        adaptive.append(interp)
        # PSNR 相对于 RIFE参考帧
        ref = rife_f[2*i + 1]
        psnr_values.append(cv2.PSNR(ref, interp))

    adaptive.append(original[-1])
    # 最后一帧 PSNR
    last_psnr = cv2.PSNR(rife_f[-1], original[-1])
    psnr_values.append(last_psnr)

    # 写视频
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rgb = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in adaptive]
    clip = ImageSequenceClip(rgb, fps=60)
    clip.write_videofile(
        output_path, codec="libx264", audio=False,
        verbose=False, logger=None, ffmpeg_params=["-crf","18"]
    )

    # 计算平均 PSNR 并返回
    avg_psnr = sum(psnr_values) / len(psnr_values)
    return avg_psnr

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--threshold", type=float, default=0.98,
                        help="SSIM 阈值")
    args = parser.parse_args()

    block_psnrs = []
    for sec in range(1, 6):
        for x in range(6):
            for y in range(4):
                name = f"{sec}_{x}_{y}"
                ip = os.path.join(DATA_DIR, f"{name}_out.mp4")
                mp = os.path.join(RESULTS_DIR, "mean_interp", f"{name}_mean.mp4")
                rp = os.path.join(RESULTS_DIR, "rife_interp", f"{name}_rife.mp4")
                op = os.path.join(
                    RESULTS_DIR,
                    f"adaptive_interp_by_frame_{args.threshold}",
                    f"{name}_adaptive.mp4"
                )
                if os.path.exists(ip) and os.path.exists(mp) and os.path.exists(rp):
                    avg = adaptive_interpolate_by_frame(ip, mp, rp, op, threshold=args.threshold)
                    print(f"{name}: Avg PSNR = {avg:.2f} dB")
                    block_psnrs.append(avg)
                else:
                    print(f"Skip missing: {name}")

    # 计算所有块的整体平均 PSNR
    if block_psnrs:
        global_avg = sum(block_psnrs) / len(block_psnrs)
        summary_path = os.path.join(RESULTS_DIR, "adaptive_interp_by_frame_summary.txt")
        with open(summary_path, "w") as sf:
            sf.write(f"Overall Average PSNR = {global_avg:.2f} dB\n")
        print(f"Overall Average PSNR: {global_avg:.2f} dB (saved to {summary_path})")
    else:
        print("No blocks processed, no summary generated.")
