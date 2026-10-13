#  Using calibration, we found out that bundle width of 30 is an optimal choice for trade-off between time and quality.
# This ablation study is to check the same using metrics
# Thus, this study is to check if calibration holds or not
import cv2
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

def get_frame(video_path, frame_idx):
    cap = cv2.VideoCapture(video_path)

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()

    frame = frames[frame_idx]
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_gray = np.float32(frame_gray)
    return frame, frame_gray


def get_corners(img, thresh_ratio=0.02):
    blockSize = 2
    ksize = 3
    k = 0.04
    dst = cv2.cornerHarris(img, blockSize, ksize, k)
    dst = cv2.dilate(dst, None)

    threshold = thresh_ratio * dst.max()
    corner_mask = dst > threshold
    num_points = corner_mask.sum()

    return dst, num_points

def evaluate_video(original_video, retargeted_video):

    original_video_num_points = []
    retargeted_video_num_points = []  

    for frame_idx in range(60):    # We keep 60 as max frame
        original_frame, original_frame_gray = get_frame(original_video, frame_idx)
        retargeted_frame, retargeted_frame_gray = get_frame(retargeted_video, frame_idx)

        original_frame_dst, original_frame_num_points = get_corners(original_frame_gray)
        retargeted_frame_dst, retargeted_frame_num_points = get_corners(retargeted_frame_gray)

        original_video_num_points.append(original_frame_num_points)
        retargeted_video_num_points.append(retargeted_frame_num_points)
    
    # Normalizing all the values
    K = max(original_video_num_points)
    original_norm = original_video_num_points / (K*1.0)
    retargeted_norm = retargeted_video_num_points / (K*1.0)

    # Computing MSE
    mse_original_retargeted = np.mean((original_norm - retargeted_norm) ** 2)

    return mse_original_retargeted

def plot_results(values, title, save_path):
    plt.figure(figsize=(12,8))
    plt.plot(values, marker='o', label="MSE")
    plt.scatter(2, values[2], color='red', s=120, zorder=5, label="Highlighted")
    for i, v in enumerate(values):
        plt.text(i, v, f"{v:.4f}", fontsize=9, ha='center', va='bottom')
    plt.xlabel("Experiment Index")
    plt.ylabel("MSE")
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.show()

experiments = [
                "../assets/output/ablation_studies/naive_stream_carving_output_ratatouille1_suboptimal_10.mp4",
               "../assets/output/ablation_studies/naive_stream_carving_output_ratatouille1_suboptimal_20.mp4",
               "../assets/output/ablation_studies/naive_stream_carving_output_ratatouille1_optimal_30.mp4",
               "../assets/output/ablation_studies/naive_stream_carving_output_ratatouille1_suboptimal_40.mp4",
               "../assets/output/ablation_studies/naive_stream_carving_output_ratatouille1_suboptimal_50.mp4",
               ]

original_video = "../assets/input/ratatouille1.mov"

mse_results = []
for experiment in tqdm(experiments):
    mse_result = evaluate_video(original_video, experiment)
    mse_results.append(mse_result)

print(mse_results)

plot_results(mse_results, "Harris Corner MSE Across Experiments", "../assets/output/ablation_studies/ablation_harris.png")