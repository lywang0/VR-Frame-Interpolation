from skimage.metrics import structural_similarity as ssim
import cv2

def compute_ssim(frame1, frame2):
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    return ssim(gray1, gray2)


def average_ssim_for_block(frames):
    total_ssim = 0
    count = 0
    for i in range(len(frames) - 1):
        ssim_score = compute_ssim(frames[i], frames[i + 1])
        total_ssim += ssim_score
        count += 1
    return total_ssim / count if count > 0 else 0

