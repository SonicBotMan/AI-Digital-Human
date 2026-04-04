import { useCallback, useEffect, useRef, useState } from "react";

export type CameraStatus = "idle" | "requesting" | "active" | "error";

export interface UseCameraReturn {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  status: CameraStatus;
  error: string | null;
  isActive: boolean;
  lastCaptureTime: Date | null;
  startCamera: () => Promise<void>;
  stopCamera: () => void;
  toggleCamera: () => Promise<void>;
  captureFrame: () => string | null;
}

const CAPTURE_INTERVAL = 5000; // 5 seconds
const JPEG_QUALITY = 0.8;
const MAX_WIDTH = 1280;
const MAX_HEIGHT = 720;

export function useCamera(): UseCameraReturn {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const [status, setStatus] = useState<CameraStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [lastCaptureTime, setLastCaptureTime] = useState<Date | null>(null);

  const isActive = status === "active";

  const stopCamera = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setStatus("idle");
    setError(null);
  }, []);

  const startCamera = useCallback(async () => {
    setStatus("requesting");
    setError(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: MAX_WIDTH },
          height: { ideal: MAX_HEIGHT },
          facingMode: "user",
        },
        audio: false,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setStatus("active");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to access camera";

      if (
        errorMessage.includes("Permission denied") ||
        errorMessage.includes("NotAllowedError")
      ) {
        setError("Camera permission denied. Please allow camera access.");
      } else if (
        errorMessage.includes("NotFoundError") ||
        errorMessage.includes("DevicesNotFoundError")
      ) {
        setError("No camera found. Please connect a camera.");
      } else {
        setError(`Camera error: ${errorMessage}`);
      }

      setStatus("error");
      stopCamera();
    }
  }, [stopCamera]);

  const captureFrame = useCallback((): string | null => {
    if (!videoRef.current || !isActive) {
      return null;
    }

    if (!canvasRef.current) {
      canvasRef.current = document.createElement("canvas");
    }

    const canvas = canvasRef.current;
    const video = videoRef.current;

    // Calculate dimensions maintaining aspect ratio
    const aspectRatio = video.videoWidth / video.videoHeight;
    let width = Math.min(video.videoWidth, MAX_WIDTH);
    let height = width / aspectRatio;

    if (height > MAX_HEIGHT) {
      height = MAX_HEIGHT;
      width = height * aspectRatio;
    }

    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext("2d");
    if (!ctx) return null;

    // Draw video frame (no mirror for accurate capture)
    ctx.drawImage(video, 0, 0, width, height);

    // Convert to JPEG base64
    const dataUrl = canvas.toDataURL("image/jpeg", JPEG_QUALITY);

    // Remove data:image/jpeg;base64, prefix to get raw base64
    const base64 = dataUrl.split(",")[1];

    setLastCaptureTime(new Date());

    return base64;
  }, [isActive]);

  const toggleCamera = useCallback(async () => {
    if (isActive) {
      stopCamera();
    } else {
      await startCamera();
    }
  }, [isActive, startCamera, stopCamera]);

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  return {
    videoRef,
    status,
    error,
    isActive,
    lastCaptureTime,
    startCamera,
    stopCamera,
    toggleCamera,
    captureFrame,
  };
}