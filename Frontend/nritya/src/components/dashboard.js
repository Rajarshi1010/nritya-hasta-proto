// Dashboard.jsx
import { motion } from "framer-motion";
import React, { useEffect, useRef, useState } from "react";
import { detect } from "./api";

export default function Dashboard() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const snapshotIntervalRef = useRef(null);

  const [recording, setRecording] = useState(false);
  const [result, setResult] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  // Start/stop camera
  useEffect(() => {
    if (recording) {
      navigator.mediaDevices
        .getUserMedia({ video: true, audio: false })
        .then((stream) => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            videoRef.current.play();
          }
        })
        .catch((err) => {
          console.error("Error accessing camera:", err);
          setResult({ success: false, error: err.message });
        });
    } else {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
      }
    }
  }, [recording]);

  // Capture snapshot every 5s
  useEffect(() => {
    if (recording) {
      snapshotIntervalRef.current = setInterval(() => {
        captureSnapshot();
      }, 2000);
    } else if (snapshotIntervalRef.current) {
      clearInterval(snapshotIntervalRef.current);
      snapshotIntervalRef.current = null;
    }

    return () => {
      if (snapshotIntervalRef.current) {
        clearInterval(snapshotIntervalRef.current);
        snapshotIntervalRef.current = null;
      }
    };
  }, [recording]);

  const captureSnapshot = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
      if (blob) {
        const formData = new FormData();
        formData.append("file", blob, "snapshot.jpg");

        const res = await detect(formData);
        setResult(res);
      }
    }, "image/jpeg", 0.95);
  };

  const handleFileSubmit = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await detect(formData);
    setResult(res);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSubmit(e.dataTransfer.files[0]);
      e.dataTransfer.clearData();
    }
  };

  return (
    <div className="dashboard-container">
      <div style={{ marginLeft: "5vw" }}>
        <div className="media-container">
          {/* Video */}
          {recording && (
            <video ref={videoRef} autoPlay muted playsInline className="video-container" />
          )}

          {/* Drag-and-drop box */}
          {!recording && (
            <div
              className="drag-drop"
              onDrop={handleDrop}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onClick={() => fileInputRef.current.click()}
              style={{
                backgroundColor: dragOver ? "#f9741689" : "#111827",
                cursor: "pointer",
                padding: "2rem",
                color: "white",
                textAlign: "center",
              }}
            >
              {dragOver ? "Drop your image here" : "Drag & Drop an image or click to upload"}
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: "none" }}
                onChange={(e) => e.target.files[0] && handleFileSubmit(e.target.files[0])}
              />
            </div>
          )}

          <canvas ref={canvasRef} style={{ display: "none" }} />
        </div>
        <hr style={{ margin: "4vh" }} />
        <p style={{ color: "white", position: "absolute", margin: "-5.3vh", padding: "0 1vw", backgroundColor: "#000", justifySelf: "center" }}>
          OR
        </p>
        <button
          className="record"
          style={{ backgroundColor: recording ? "#4caf50" : "#888" }}
          onClick={() => setRecording(!recording)}
        >
          {recording ? "Stop Recording" : "Start Recording"}
        </button>
      </div>

      <div className="result" style={{ textAlign: "left", marginLeft:"2vw" }}>
        {result ? (
          result.success ? (
            <>
              <p style={{ color: "#f97316", fontFamily: "Yatra One, system-ui", fontSize: "50px", marginBottom: "10px" }}>
                <strong>{result.prediction}</strong>
              </p>
              {result.distance && (
                <p style={{ color: "grey", fontFamily: "Alan Sans, sans-serif", fontSize:"small" }}>Distance: {result.distance.toFixed(3)}</p>
              )}
              <p style={{ color: "white", fontFamily: "Alan Sans, sans-serif", marginBottom:"10vh" }}>{result.description}</p>
            </>
          ) : (
            <p style={{ color: "red" }}>❌ {result.error}</p>
          )
        ) : (
          <p style={{ color: "white", fontFamily: "Yatra One, system-ui" }}>No result yet</p>
        )}
      </div>

      <motion.footer
        className="welcome-footer"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.9, duration: 0.8 }}
        style={{ color: "#aaa", marginTop: "20px" }}
      />
      © {new Date().getFullYear()} NrityaLens • Preserve tradition with AI
    </div>
  );
}
