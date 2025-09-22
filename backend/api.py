# app_fastapi.py
import os
import numpy as np
import cv2
import mediapipe as mp
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sklearn.neighbors import KNeighborsClassifier
from pydantic import BaseModel

from descriptions import describe


# --- Setup ---
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust to your frontend origin for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Paths ---
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
IN_NPZ = os.path.join(_PROJECT_ROOT, "features", "normalized_features.npz")

# MediaPipe indices
ANCHOR_IDX = [0, 5, 17, 1]

class UrlRequest(BaseModel):
    url: str

# --- Normalization Helpers ---
def canonical_anchor_points():
    return np.array([
        [0.0, 0.0, 0.0],   # wrist
        [0.05, 0.0, 0.0],  # index base
        [-0.05, 0.0, 0.0], # pinky base
        [0.0, 0.05, 0.0],  # thumb base
    ], dtype=np.float32)

def umeyama_similarity_transform(src, dst):
    mu_src, mu_dst = src.mean(0), dst.mean(0)
    src_c, dst_c = src - mu_src, dst - mu_dst
    cov = (dst_c.T @ src_c) / src.shape[0]
    u, _s, vt = np.linalg.svd(cov)
    r = u @ vt
    if np.linalg.det(r) < 0:
        vt[-1, :] *= -1
        r = u @ vt
    var_src = (src_c**2).sum() / src.shape[0]
    s = _s.sum() / var_src
    t = mu_dst - s * (r @ mu_src)
    return s, r, t

def normalize_pts(pts21):
    anchors_src = pts21[ANCHOR_IDX]
    anchors_dst = canonical_anchor_points()
    s, R, t = umeyama_similarity_transform(anchors_src, anchors_dst)
    pts_norm = (s * (R @ pts21.T).T) + t
    return pts_norm.astype(np.float32)

# --- Globals ---
knn = None
mp_hands = None

def load_model():
    global knn, mp_hands
    try:
        data = np.load(IN_NPZ, allow_pickle=True)
        X = data["X"].astype(np.float32)
        y = data["y"].astype(str)

        knn = KNeighborsClassifier(n_neighbors=1, metric="euclidean")
        knn.fit(X, y)
        print("KNN model trained successfully.")
    except FileNotFoundError:
        print(f"Error: Feature file not found at {IN_NPZ}. Please run the feature generation scripts.")
        return

    mp_hands = mp.solutions.hands
    print("MediaPipe Hands initialized.")

# --- API Endpoint ---
@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    if not file:
        return {"error": "No file uploaded"}, 400
    if file.filename == '':
        return {"error": "No selected file"}, 400

    if file and knn is not None:
        # Reading image file in memory
        file_str = await file.read()
        np_img = np.frombuffer(file_str, np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        # Initialize a hand detector
        with mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=1,
                min_detection_confidence=0.5
        ) as hands:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            if not result.multi_hand_landmarks:
                return {"result": "No hand detected"}

            # Get landmarks
            lm = result.multi_hand_landmarks[0].landmark
            h, w = frame.shape[:2]
            pts = np.array([[p.x * w, p.y * h, p.z * w] for p in lm], dtype=np.float32)

            # Normalization and prediction
            pts_norm = normalize_pts(pts).reshape(1, -1)
            prediction = knn.predict(pts_norm)[0]
            distance = knn.kneighbors(pts_norm, n_neighbors=1, return_distance=True)[0][0][0]
            description = describe(prediction)

            return {"prediction": prediction, "distance": distance, 'description': description}

    return {"error": "Model not loaded or file error"}, 500

# --- Startup Event ---
@app.on_event("startup")
def startup_event():
    load_model()
