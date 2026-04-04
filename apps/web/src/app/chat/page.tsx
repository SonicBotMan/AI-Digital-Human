"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Wifi,
  WifiOff,
  Loader2,
  RotateCcw,
  Trash2,
  AlertCircle,
  Camera,
  CameraOff,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { InputBar } from "@/components/chat/InputBar";
import { useChat, type ConnectionState } from "@/hooks/useChat";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import dynamic from "next/dynamic";
import { analyzeFrame, type CameraAnalysisResult } from "@/lib/cameraApi";

const CameraWindow = dynamic(
  () => import("@/components/video/CameraWindow").then((mod) => mod.default),
  { ssr: false }
);

export default function ChatPage() {
  const {
    messages,
    connectionState,
    error,
    sendMessage,
    clearHistory,
    connect,
    reconnect,
  } = useChat();

  const [apiKeyMissing, setApiKeyMissing] = useState(false);

  useEffect(() => {
    connect();
    api.get<any>("/settings")
      .then((res) => {
        if (!res.GLM_API_KEY && !res.OPENAI_API_KEY && !res.MINIMAX_API_KEY) {
          setApiKeyMissing(true);
        }
      })
      .catch(() => {
      });
  }, [connect]);

  const isStreaming = useMemo(
    () => messages.some((m) => m.streaming),
    [messages],
  );

  const isConnected = connectionState === "connected";
  const [cameraOpen, setCameraOpen] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<CameraAnalysisResult | null>(null);

  async function handleFrameCapture(base64Image: string) {
    try {
      const result = await analyzeFrame(base64Image);
      if (result) {
        setAnalysisResult(result);
      }
    } catch (_) {
    }
  }

  return (
    <div className="flex h-full">
      <div className="flex flex-1 flex-col">
        <div className="flex items-center justify-between border-b px-4 py-2">
          <div className="flex items-center gap-3">
            <ConnectionStatus state={connectionState} />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setCameraOpen(!cameraOpen)}
              className={cn(
                "h-8 gap-1.5 text-xs",
                cameraOpen ? "text-blue-600 bg-blue-50" : "text-muted-foreground"
              )}
            >
              {cameraOpen ? (
                <CameraOff className="h-3.5 w-3.5" />
              ) : (
                <Camera className="h-3.5 w-3.5" />
              )}
              Camera
            </Button>
          </div>
          <div className="flex items-center gap-1">
            {isConnected && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearHistory}
                className="h-8 gap-1.5 text-xs text-muted-foreground"
              >
                <Trash2 className="h-3.5 w-3.5" />
                Clear
              </Button>
            )}
            {connectionState === "disconnected" && (
              <Button
                variant="ghost"
                size="sm"
                onClick={reconnect}
                className="h-8 gap-1.5 text-xs"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                Reconnect
              </Button>
            )}
          </div>
        </div>

        {apiKeyMissing && (
          <div className="flex items-center gap-2 border-b bg-amber-500/10 px-4 py-3 text-sm font-medium text-amber-600">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>We noticed you haven't configured your AI API Keys. Please click the ⚙️ Settings icon in the header to set them up before chatting.</span>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 border-b bg-destructive/10 px-4 py-2 text-xs text-destructive">
            <AlertCircle className="h-3.5 w-3.5 shrink-0" />
            {error}
          </div>
        )}

        <ChatPanel messages={messages} />

        <InputBar onSend={sendMessage} disabled={isStreaming || !isConnected} />
      </div>

      <div
        className={cn(
          "border-l transition-all duration-300 overflow-hidden",
          cameraOpen ? "w-[280px]" : "w-0"
        )}
      >
        {cameraOpen && (
          <CameraWindow
            onFrameCapture={handleFrameCapture}
            analysisResult={
              analysisResult
                ? {
                    faces_found: analysisResult.face_detection.faces_found,
                    identified: analysisResult.face_detection.identified.map((f) => ({
                      name: f.name,
                      confidence: f.confidence,
                    })),
                  }
                : null
            }
            captureInterval={5000}
          />
        )}
      </div>
    </div>
  );
}

function ConnectionStatus({ state }: { state: ConnectionState }) {
  const config: Record<
    string,
    { icon: typeof Wifi; label: string; className: string }
  > = {
    connected: {
      icon: Wifi,
      label: "Connected",
      className: "text-emerald-600",
    },
    connecting: {
      icon: Loader2,
      label: "Connecting...",
      className: "text-amber-500 animate-spin",
    },
    disconnected: {
      icon: WifiOff,
      label: "Disconnected",
      className: "text-muted-foreground",
    },
    error: {
      icon: WifiOff,
      label: "Connection error",
      className: "text-destructive",
    },
  };

  const { icon: Icon, label, className } = config[state] ?? config.disconnected;

  return (
    <div className="flex items-center gap-1.5 text-xs">
      <Icon className={cn("h-3.5 w-3.5", className)} />
      <span className="text-muted-foreground">{label}</span>
    </div>
  );
}
