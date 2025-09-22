# src/normalize_and_save.py
import os
import numpy as np

IN_NPZ  = os.path.join("features", "raw_landmarks.npz")
OUT_NPZ = os.path.join("features", "normalized_features.npz")

# MediaPipe indices: wrist=0, thumb_cmc=1, index_mcp=5, pinky_mcp=17
ANCHOR_IDX = [0, 5, 17, 1]

def canonical_anchor_points():
    # Simple canonical frame: wrist at origin; index base +x, pinky base -x, thumb base +y
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
    var_src = (src_c**2).sum()/src.shape[0]
    s = S.sum() / var_src
    t = mu_dst - s * (R @ mu_src)
    return s, R, t

def apply_transform(pts, s, R, t):
    return (s * (R @ pts.T).T) + t

def main():
    data = np.load(IN_NPZ, allow_pickle=True)
    X = data["X"]            # (N,63) raw
    y = data["y"]
    kept_paths = data["kept_paths"]

    anchors_dst = canonical_anchor_points()
    Xn = np.zeros_like(X, dtype=np.float32)

    for i in range(X.shape[0]):
        pts = X[i].reshape(21,3)
        anchors_src = pts[ANCHOR_IDX]
        s, R, t = umeyama_similarity_transform(anchors_src, anchors_dst)
        pts_norm = apply_transform(pts, s, R, t)
        Xn[i] = pts_norm.reshape(-1)

    os.makedirs(os.path.dirname(OUT_NPZ), exist_ok=True)
    np.savez_compressed(OUT_NPZ, X=Xn, y=y, kept_paths=kept_paths)
    print(f"Saved normalized features: {OUT_NPZ}, shape={Xn.shape}")

if __name__ == "__main__":
    main()
