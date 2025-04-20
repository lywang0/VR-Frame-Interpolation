import cv2
import numpy as np
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from utils.configuration import DATA_DIR, RESULTS_DIR

def merge_blocks(block_paths, output_path, rows=4, cols=6):
    # block_paths 是 [row][col] 二维列表
    block_videos = [[cv2.VideoCapture(block_paths[r][c]) for c in range(cols)] for r in range(rows)]
    h, w = 480, 640
    fps = 60
    num_frames = int(block_videos[0][0].get(cv2.CAP_PROP_FRAME_COUNT))

    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (cols*w, rows*h))
    for _ in range(num_frames):
        grid = []
        for row in block_videos:
            row_frames = [cap.read()[1] for cap in row]
            grid.append(np.hstack(row_frames))
        frame = np.vstack(grid)
        writer.write(frame)
    writer.release()
    
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--method", choices=["mean", "rife", "adaptive", "adaptive_interp_by_frame"], required=True,
                        help="拼接的视频类型(mean / rife / adaptive/ adaptive_interp_by_frame)")
    parser.add_argument("--threshold", type=float, default=0.98,
                        help="仅用于 adaptive,指定阈值目录名")
    args = parser.parse_args()

    # 拼接目录名
    if args.method == "adaptive":
        base_path = os.path.join(RESULTS_DIR, f"adaptive_interp_{args.threshold}")
    elif args.method == "adaptive_interp_by_frame":
        base_path = os.path.join(RESULTS_DIR, f"adaptive_interp_by_frame_{args.threshold}")
    else:
        base_path = os.path.join(RESULTS_DIR, f"{args.method}_interp")

    output_dir = os.path.join(RESULTS_DIR, "merged_video")
    os.makedirs(output_dir, exist_ok=True)  

    merged_clips = []
    temp_files = []

    for t in range(1, 6):  # 共5秒钟
        block_paths = [[
            os.path.join(base_path, f"{t}_{x}_{y}_{args.method}.mp4")
            for x in range(6)
        ] for y in range(4)] if args.method != "adaptive_interp_by_frame" else [
            [
                os.path.join(base_path, f"{t}_{x}_{y}_adaptive.mp4")
                for x in range(6)
            ] for y in range(4)]
         # y 是行，x 是列

        if all(os.path.exists(p) for row in block_paths for p in row):
            merged_sec_path = os.path.join(output_dir, f"merged_second_{t}.mp4")
            print(f"Merging blocks for second {t}...")
            merge_blocks(block_paths, merged_sec_path)
            merged_clips.append(VideoFileClip(merged_sec_path))
            temp_files.append(merged_sec_path)
        else:
            print(f"Missing blocks for second {t}, skipping.")

    # 合并 5 段拼接视频为完整视频
    if merged_clips:
        final_video = concatenate_videoclips(merged_clips)
        final_path = os.path.join(output_dir, f"{args.method}_final_merged.mp4") if args.method != "adaptive" else os.path.join(output_dir, f"adaptive_{args.threshold}_final_merged.mp4")
        final_video.write_videofile(final_path, codec="libx264", audio=False, fps=60)
        print(f"Final video saved to {final_path}")

        for path in temp_files:
            os.remove(path)
    else:
        print("No video segments to merge.")

