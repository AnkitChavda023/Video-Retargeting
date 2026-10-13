import cv2
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

def get_img(img_path):
    img = cv2.imread(img_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = np.float32(img_gray)
    return img, img_gray 

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

def padding(img, target_h, target_w):
    h, w = img.shape[:2]
    pad_h_total = target_h - h
    pad_w_total = target_w - w
    pad_top = pad_h_total // 2
    pad_bottom = pad_h_total - pad_top
    pad_left = pad_w_total // 2
    pad_right = pad_w_total - pad_left

    padded = cv2.copyMakeBorder(img, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    return padded

def evaluate_video(original_video, retargeted_video):

    original_video_num_points = []
    retargeted_video_num_points = []

    for frame_idx in range(60):
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

    mse_original_retargeted = np.mean((original_norm - retargeted_norm) ** 2)

    return mse_original_retargeted

if __name__ == "__main__":
    # original_video = "../assets/input/golf.mov"    

    # output_videos = [
    #     "../assets/input/scaled_golf.mov",    # scaled video for comparison
    #     "../assets/output/seam_carving/naive_approach/naive_seam_carving_output_golf.mp4",   
    #     "../assets/output/seam_carving/static_approach/static_seam_carving_output_golf.mp4",   
    #     "../assets/output/stream_carving/naive_approach/naive_stream_carving_output_golf.mp4" ,  
    #     "../assets/output/stream_carving/static_approach/static_stream_carving_output_golf.mp4" 
    #     ]  

    original_video = "../assets/input/ratatouille1.mov"    

    output_videos = [
        "../assets/input/scaled_ratatouille1.mov",    # scaled video for comparison
        "../assets/output/seam_carving/naive_approach/naive_seam_carving_output_ratatouille1.mp4",   
        "../assets/output/seam_carving/static_approach/static_seam_carving_output_ratatouille1.mp4",   
        "../assets/output/stream_carving/naive_approach/naive_stream_carving_output_ratatouille1.mp4" ,  
        "../assets/output/stream_carving/static_approach/static_stream_carving_output_ratatouille1.mp4" 
        ]  
    
    for output_video in output_videos:
        print(f"Evaluating: {output_video}")
        mse_harris = evaluate_video(original_video, output_video)
        print(f"Mean Squared Error using Harris Corners: {mse_harris:.4f}")

# original_video = "../assets/input/ratatouille1.mov"    # (83, 240, 320, 3)
# scaled_video = "../assets/input/scaled_ratatouille.mov"    # (83, 200, 200, 3)

# original_video = "../assets/input/golf.mov"    # (83, 240, 320, 3)
# scaled_video = "../assets/input/scaled_golf.mov"    # (83, 200, 200, 3)

# retargeted_video = "../assets/output/naive_seam_carving_output.mp4"    # (60, 200, 200, 3)
# retargeted_video = "../assets/output/static_seam_carving_output.mp4"    # (60, 200, 200, 3)
# retargeted_video = "../assets/output/naive_stream_carving_output.mp4"    # (60, 200, 200, 3)
# retargeted_video = "../assets/output/static_stream_carving_output.mp4"    # (60, 200, 200, 3)

# retargeted_video = "../assets/output/naive_seam_carving_output_ratatouille1.mp4"    # (60, 128, 320, 3)
# retargeted_video = "../assets/output/static_seam_carving_output_ratatouille1.mp4"    # (60, 128, 320, 3)
# retargeted_video = "../assets/output/naive_stream_carving_output_ratatouille1.mp4"    # (60, 128, 320, 3)
# retargeted_video = "../assets/output/static_stream_carving_output_ratatouille1.mp4"    # (60, 128, 320, 3)

# max_frame_idx = 60
# frame_idx = 30

# mse_scaled, mse_retargeted = evaluate_video(original_video, scaled_video, retargeted_video)
# print(f"Evaluating video: {retargeted_video}")
# print(f"MSE for scaled video: {mse_scaled:.4}")
# print(f"MSE for retargeted video: {mse_retargeted:.4}")

# if (frame_idx > max_frame_idx):
#     print("Retargeted video can not support this frame idx.")

# original_frame, original_frame_gray = get_frame(original_video, frame_idx)
# scaled_frame, scaled_frame_gray = get_frame(scaled_video, frame_idx)
# retargeted_frame, retargeted_frame_gray = get_frame(retargeted_video, frame_idx)

# original_frame_dst, original_frame_num_points = get_corners(original_frame_gray)
# original_frame[original_frame_dst > 0.01 * original_frame_dst.max()] = [0, 0, 255] 

# # cv2.imwrite("original_frame_harris.png", original_frame)
# print(f"original_frame_num_points: {original_frame_num_points}")

# scaled_frame_dst, scaled_frame_num_points = get_corners(scaled_frame_gray)
# scaled_frame[scaled_frame_dst > 0.01 * scaled_frame_dst.max()] = [0, 0, 255] 

# # cv2.imwrite("scaled_frame_harris.png", scaled_frame)
# print(f"scaled_frame_num_points: {scaled_frame_num_points}")

# retargeted_frame_dst, retargeted_frame_num_points = get_corners(retargeted_frame_gray)
# retargeted_frame[retargeted_frame_dst > 0.01 * retargeted_frame_dst.max()] = [0, 0, 255] 

# # cv2.imwrite("retargeted_frame_harris.png", retargeted_frame)
# print(f"retargeted_frame_num_points: {retargeted_frame_num_points}")

# max_h = max(original_frame.shape[0], scaled_frame.shape[0], retargeted_frame.shape[0])
# max_w = max(original_frame.shape[1], scaled_frame.shape[1], retargeted_frame.shape[1])

# original_frame_padded = padding(original_frame, max_h, max_w)
# scaled_frame_padded = padding(scaled_frame, max_h, max_w)
# retargeted_frame_padded = padding(retargeted_frame, max_h, max_w)

# cv2.putText(original_frame_padded, f"Original {original_frame_num_points}", (10,15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
# cv2.putText(scaled_frame_padded, f"Scaled {scaled_frame_num_points}", (10,15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
# cv2.putText(retargeted_frame_padded, f"Retargeted {retargeted_frame_num_points}", (10,15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

# combined_vertical = np.hstack([original_frame_padded, scaled_frame_padded, retargeted_frame_padded])

# cv2.imwrite(f"harris_results_for_{frame_idx}.png", combined_vertical)