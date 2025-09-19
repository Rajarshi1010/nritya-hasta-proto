# app.py
import os
import numpy as np
import cv2
import mediapipe as mp
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.neighbors import KNeighborsClassifier


app = Flask(__name__)
CORS(app)


# --- Paths ---
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
IN_NPZ = os.path.join(_PROJECT_ROOT, "features", "normalized_features.npz")

# MediaPipe indices
ANCHOR_IDX = [0, 5, 17, 1]

# --- Normalization Helpers (copied from your project) ---
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
    U, S, Vt = np.linalg.svd(cov)
    R = U @ Vt
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = U @ Vt
    var_src = (src_c**2).sum() / src.shape[0]
    s = S.sum() / var_src
    t = mu_dst - s * (R @ mu_src)
    return s, R, t

def normalize_pts(pts21):
    anchors_src = pts21[ANCHOR_IDX]
    anchors_dst = canonical_anchor_points()
    s, R, t = umeyama_similarity_transform(anchors_src, anchors_dst)
    pts_norm = (s * (R @ pts21.T).T) + t
    return pts_norm.astype(np.float32)


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

    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    print("MediaPipe Hands initialized.")

#api endpoint for predictions
@app.route("/predict", methods=["POST"])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and knn is not None:
        # Reading image file in memory
        filestr = file.read()
        npimg = np.frombuffer(filestr, np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        # Initialize a hand detector
        with mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.5
        ) as hands:
            # Landmark extraction
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            if not result.multi_hand_landmarks:
                return jsonify({"prediction": "No hand detected"})

            # Get landmarks
            lm = result.multi_hand_landmarks[0].landmark
            h, w = frame.shape[:2]

            pts = np.array([[p.x * w, p.y * h, p.z * w] for p in lm], dtype=np.float32)

            #normalization and prediction
            pts_norm = normalize_pts(pts).reshape(1, -1)
            prediction = knn.predict(pts_norm)[0]
            distance = knn.kneighbors(pts_norm, n_neighbors=1, return_distance=True)[0][0][0]

            return jsonify({
                "prediction": prediction,
                "distance": f"{distance:.4f}"
            })

    return jsonify({"error": "Model not loaded or file error"}), 500

if __name__ == "__main__":
    load_model()
    app.run(host="0.0.0.0", port=5000, debug=True)
