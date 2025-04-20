import os
import time
import numpy as np
from moviepy.editor import VideoFileClip, ImageSequenceClip
from utils.configuration import DATA_DIR, RESULTS_DIR

def interpolate_by_mean(input_path, output_path):
    clip = VideoFileClip(input_path)
    frames = list(clip.iter_frames(fps=clip.fps, dtype="uint8"))

    interpolated_frames = []

    for i in range(len(frames) - 1):
        frame1 = frames[i]
        frame2 = frames[i + 1]
        interpolated_frames.append(frame1)
        mean_frame = ((frame1.astype(np.float32) + frame2.astype(np.float32)) / 2).astype(np.uint8)
        interpolated_frames.append(mean_frame)

    interpolated_frames.append(frames[-1])
    new_fps = clip.fps * 2
    new_clip = ImageSequenceClip(interpolated_frames, fps=new_fps)
    new_clip.write_videofile(output_path, codec="libx264", audio=False, verbose=False, logger=None)

def mean_interpolation(log_path):
    os.makedirs(os.path.join(RESULTS_DIR, "mean_interp"), exist_ok=True)
    log_path = os.path.join(RESULTS_DIR, "mean_interp", "mean_latency_log.txt")

    with open(log_path, "w") as log_file:
        for t in range(1, 6):
            for x in range(6):
                for y in range(4):
                    name = f"{t}_{x}_{y}"
                    input_path = os.path.join(DATA_DIR, f"{name}_out.mp4")
                    output_path = os.path.join(RESULTS_DIR, "mean_interp", f"{name}_mean.mp4")

                    if os.path.exists(input_path):
                        start = time.time()
                        interpolate_by_mean(input_path, output_path)
                        elapsed = time.time() - start
                        log_line = f"{name}_mean.mp4\tMETHOD=MEAN\tLATENCY={elapsed:.3f}s\n"
                        print(log_line.strip())
                        log_file.write(log_line)
                    else:
                        print(f"Skipping missing input: {name}")

if __name__ == "__main__":
    mean_interpolation()
    print("Mean interpolation completed.")
