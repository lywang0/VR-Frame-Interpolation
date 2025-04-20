import cv2
import numpy as np

def interpolate_by_mean(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        frames.append(frame)
    cap.release()

    out_frames = []
    for i in range(len(frames) - 1):
        out_frames.append(frames[i])
        mean_frame = ((frames[i].astype(np.float32) + frames[i+1].astype(np.float32)) / 2).astype(np.uint8)
        out_frames.append(mean_frame)
    out_frames.append(frames[-1])

    save_video(out_frames, output_path, fps=60)

def save_video(frames, output_path, fps=60):
    h, w, _ = frames[0].shape
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    for f in frames:
        writer.write(f)
    writer.release()

def load_video_frames(path):
    cap = cv2.VideoCapture(path)
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        frames.append(frame)
    cap.release()
    return frames
