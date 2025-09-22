# src/extract_landmarks.py
import os, glob
import numpy as np
import cv2
import mediapipe as mp
from tqdm import tqdm

RAW_DIR = os.path.join("data", "raw")
OUT_NPZ = os.path.join("features", "raw_landmarks.npz")

mp_hands = mp.solutions.hands

def iter_images_by_class(root):
    classes = sorted([d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))])
    for cls in classes:
        cls_dir = os.path.join(root, cls)
        for fp in glob.glob(os.path.join(cls_dir, "*")):
            if fp.lower().endswith((".jpg", ".jpeg", ".png")):
                yield fp, cls

def extract_hand_landmarks(image_bgr, hands):
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    result = hands.process(image_rgb)
    if not result.multi_hand_landmarks:
        return None
    lm = result.multi_hand_landmarks[0].landmark
    h, w = image_bgr.shape[:2]
    pts = np.array([[p.x*w, p.y*h, p.z*w] for p in lm], dtype=np.float32)  # (21,3)
    return pts

def main():
    os.makedirs(os.path.dirname(OUT_NPZ), exist_ok=True)
    X_list, y_list, kept = [], [], []
    fail = 0

    with mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5) as hands:
        items = list(iter_images_by_class(RAW_DIR))
        for fp, cls in tqdm(items, desc="Extracting landmarks"):
            img = cv2.imread(fp)
            if img is None:
                fail += 1
                continue
            pts = extract_hand_landmarks(img, hands)
            if pts is None:
                fail += 1
                continue
            X_list.append(pts.reshape(-1))   # 63-d
            y_list.append(cls)
            kept.append(fp)

    if not X_list:
        print("No landmarks extracted. Check images/lighting/hand size.")
        return

    X = np.vstack(X_list).astype(np.float32)
    y = np.array(y_list)
    kept_paths = np.array(kept)
    np.savez_compressed(OUT_NPZ, X=X, y=y, kept_paths=kept_paths)
    print(f"Saved {X.shape[0]} samples to {OUT_NPZ}. Failed images: {fail}")

if __name__ == "__main__":
    main()
