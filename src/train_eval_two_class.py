# src/train_eval_two_class.py
import os
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

IN_NPZ = os.path.join("features", "normalized_features.npz")

def main():
    data = np.load(IN_NPZ, allow_pickle=True)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(str)

    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    idx_train, idx_test = next(sss.split(X, y))

    Xtr, Xte = X[idx_train], X[idx_test]
    ytr, yte = y[idx_train], y[idx_test]

    knn = KNeighborsClassifier(n_neighbors=1, metric="euclidean")
    knn.fit(Xtr, ytr)
    ypred = knn.predict(Xte)

    acc = accuracy_score(yte, ypred)
    cm = confusion_matrix(yte, ypred, labels=np.unique(y))
    print("Accuracy:", acc)
    print("Labels order:", np.unique(y))
    print("Confusion matrix:\n", cm)
    print(classification_report(yte, ypred))

if __name__ == "__main__":
    main()
