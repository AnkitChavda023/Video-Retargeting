import cv2
import numpy as np
import matplotlib.pyplot as plt

# We have 3 energy functions: forward, backward and temporal
# However, forward is not useful for evaluation
def backward_energy(img):
    xgrad = cv2.Sobel(img, cv2.CV_32F, dx=1, dy=0, ksize=3, borderType=cv2.BORDER_DEFAULT)
    ygrad = cv2.Sobel(img, cv2.CV_32F, dx=0, dy=1, ksize=3, borderType=cv2.BORDER_DEFAULT)
    back_energy = np.sqrt(np.sum(xgrad**2, axis=2) + np.sum(ygrad**2, axis=2))
    return back_energy

def temporal_energy(frames):
    temp_energy = np.zeros((frames[0].shape[0], frames[0].shape[1]), dtype=np.float32)
    for t in range(1, len(frames)):
        diff = np.abs(frames[t].astype(np.float32) - frames[t-1].astype(np.float32))
        temp_energy = np.maximum(temp_energy, diff.sum(axis=2))
    return temp_energy

def normalize_image(img):
    return img.astype(np.float32) / 255.0

def normalize_energy(E):
    E = E.astype(np.float32)
    return (E - E.min()) / (E.max() - E.min() + 1e-8)

def resize_spatially(img, target_shape):
    target_h, target_w = target_shape
    return cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_LINEAR)

def compute_video_energy_metrics(videoA_frames, videoB_frames):
    num_frames = min(len(videoA_frames), len(videoB_frames))

    videoA_frames = [normalize_image(f) for f in videoA_frames]
    videoB_frames = [normalize_image(f) for f in videoB_frames]
    
    backward_diffs = []

    for i in range(num_frames):
        frameA = videoA_frames[i]
        frameB = videoB_frames[i]

        if frameA.shape[:2] != frameB.shape[:2]:
            frameB = resize_spatially(frameB, frameA.shape[:2])

        backA = backward_energy(frameA)
        backB = backward_energy(frameB)
        backA = [normalize_energy(f) for f in backA]
        backB = [normalize_energy(f) for f in backB]
        backA = np.array(backA)
        backB = np.array(backB)
        backward_diffs.append(((backA - backB)**2).mean())

    avg_backward_diff = np.mean(backward_diffs)

    tempA = temporal_energy(videoA_frames[:num_frames])
    tempB = temporal_energy(videoB_frames[:num_frames])

    if tempA.shape != tempB.shape:
        tempB = resize_spatially(tempB, tempA.shape)

    tempA = [normalize_energy(f) for f in tempA]
    tempB = [normalize_energy(f) for f in tempB]
    tempA = np.array(tempA)
    tempB = np.array(tempB)
    temporal_diff = ((tempA - tempB)**2).mean()

    return avg_backward_diff, temporal_diff

if __name__ == "__main__":
    # original_video = "../assets/input/golf.mov"    

    # output_videos = [
    #     "../assets/output/seam_carving/naive_approach/naive_seam_carving_output_golf.mp4",   
    #     "../assets/output/seam_carving/static_approach/static_seam_carving_output_golf.mp4",   
    #     "../assets/output/stream_carving/naive_approach/naive_stream_carving_output_golf.mp4" ,  
    #     "../assets/output/stream_carving/static_approach/static_stream_carving_output_golf.mp4" 
    #     ]  

    original_video = "../assets/input/ratatouille1.mov"    

    output_videos = [
        "../assets/output/seam_carving/naive_approach/naive_seam_carving_output_ratatouille1.mp4",   
        "../assets/output/seam_carving/static_approach/static_seam_carving_output_ratatouille1.mp4",   
        "../assets/output/stream_carving/naive_approach/naive_stream_carving_output_ratatouille1.mp4" ,  
        "../assets/output/stream_carving/static_approach/static_stream_carving_output_ratatouille1.mp4" 
        ]  

    for output_video in output_videos:
        print(f"Evaluating: {output_video}")
        cap = cv2.VideoCapture(original_video)
        original_video_frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            original_video_frames.append(frame)
        cap.release()

        cap = cv2.VideoCapture(output_video)
        output_video_frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            output_video_frames.append(frame)
        cap.release()

        avg_backward_diff, temporal_diff = compute_video_energy_metrics(original_video_frames, output_video_frames)

        print(f"Mean Squared Error using Backward Energy: {avg_backward_diff:.4f}")
        print(f"Mean Squared Error using Temporal Energy: {temporal_diff:.4f}")
