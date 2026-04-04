"use client";

import React from "react";
import { useCamera } from "@/hooks/useCamera";

interface CameraWindowProps {
  onFrameCapture?: (base64Image: string) => void;
  captureInterval?: number; // in milliseconds, default 5000
  showAnalysis?: boolean;
  analysisResult?: {
    faces_found: number;
    identified: Array<{ name: string; confidence: number }>;
  } | null;
}

export default function CameraWindow({
  onFrameCapture,
  captureInterval = 5000,
  showAnalysis = true,
  analysisResult = null,
}: CameraWindowProps) {
  const {
    videoRef,
    status,
    error,
    isActive,
    lastCaptureTime,
    startCamera,
    stopCamera,
    toggleCamera,
    captureFrame,
  } = useCamera();

  React.useEffect(() => {
    if (!isActive || !onFrameCapture) return;

    const intervalId = setInterval(() => {
      const frame = captureFrame();
      if (frame) {
        onFrameCapture(frame);
      }
    }, captureInterval);

    return () => clearInterval(intervalId);
  }, [isActive, onFrameCapture, captureInterval, captureFrame]);

  return (
    <div className="flex flex-col h-full bg-gray-900 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              status === "active"
                ? "bg-green-500 animate-pulse"
                : status === "requesting"
                ? "bg-yellow-500 animate-pulse"
                : status === "error"
                ? "bg-red-500"
                : "bg-gray-500"
            }`}
          />
          <span className="text-xs text-gray-300">
            {status === "active"
              ? "Camera Active"
              : status === "requesting"
              ? "Starting..."
              : status === "error"
              ? "Error"
              : "Camera Off"}
          </span>
        </div>

        <button
          onClick={toggleCamera}
          className={`px-3 py-1 text-xs rounded-md transition-colors ${
            isActive
              ? "bg-red-600 hover:bg-red-700 text-white"
              : "bg-blue-600 hover:bg-blue-700 text-white"
          }`}
        >
          {isActive ? "Stop" : "Start"}
        </button>
      </div>

      {/* Video Area */}
      <div className="relative flex-1 bg-black flex items-center justify-center">
        {status === "idle" && (
          <div className="text-center text-gray-500 p-4">
            <svg
              className="w-12 h-12 mx-auto mb-2 text-gray-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
            <p className="text-sm">Click "Start" to enable camera</p>
          </div>
        )}

        {status === "requesting" && (
          <div className="text-center text-gray-400">
            <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-2" />
            <p className="text-sm">Requesting camera access...</p>
          </div>
        )}

        {status === "error" && (
          <div className="text-center text-red-400 p-4">
            <svg
              className="w-12 h-12 mx-auto mb-2 text-red-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <p className="text-sm mb-2">{error}</p>
            <button
              onClick={startCamera}
              className="text-xs text-blue-400 hover:text-blue-300"
            >
              Try Again
            </button>
          </div>
        )}

        {isActive && (
          <>
            <video
              ref={videoRef as React.RefObject<HTMLVideoElement>}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
              style={{ transform: "scaleX(-1)" }}
            />

            {/* Capture Flash */}
            <div className="absolute inset-0 bg-white opacity-0 pointer-events-none transition-opacity duration-100 capture-flash" />
          </>
        )}
      </div>

      {/* Analysis Results */}
      {showAnalysis && isActive && analysisResult && (
        <div className="px-3 py-2 bg-gray-800 border-t border-gray-700">
          <div className="text-xs text-gray-400 mb-1">Analysis</div>
          <div className="flex items-center gap-2">
            {analysisResult.identified.length > 0 ? (
              analysisResult.identified.map((face, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 bg-green-600 text-white text-xs rounded-full"
                >
                  {face.name} ({Math.round(face.confidence * 100)}%)
                </span>
              ))
            ) : (
              <span className="text-xs text-gray-500">No faces identified</span>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      {isActive && lastCaptureTime && (
        <div className="px-3 py-1 bg-gray-800 border-t border-gray-700 text-xs text-gray-500">
          Last capture: {lastCaptureTime.toLocaleTimeString()}
        </div>
      )}

      <style jsx>{`
        .capture-flash {
          animation: flash 0.3s ease-out;
        }
        @keyframes flash {
          0% { opacity: 0.5; }
          100% { opacity: 0; }
        }
      `}</style>
    </div>
  );
}