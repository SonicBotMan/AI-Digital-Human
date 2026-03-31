"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { createWebSocket } from "@/lib/api";

export type AttachmentType = "image" | "audio" | "video";

export interface Attachment {
  id: string;
  file: File;
  type: AttachmentType;
  preview?: string;
  base64?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
  attachments?: {
    type: AttachmentType;
    name: string;
    url?: string;
  }[];
  /** True while this assistant message is still streaming. */
  streaming?: boolean;
  /** Recognition result attached by backend when an image contains a face. */
  faceRecognition?: {
    name: string;
    confidence: number;
  };
}

export type ConnectionState =
  | "connecting"
  | "connected"
  | "disconnected"
  | "error";

interface UseChatOptions {
  wsPath?: string;
  maxReconnectAttempts?: number;
}

export function useChat({
  wsPath = "/chat/stream",
  maxReconnectAttempts = 5,
}: UseChatOptions = {}) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [connectionState, setConnectionState] =
    useState<ConnectionState>("disconnected");
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const streamingMessageIdRef = useRef<string | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      wsRef.current?.close();
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
    };
  }, []);

  const connect = useCallback(() => {
    wsRef.current?.close();

    setConnectionState("connecting");
    setError(null);

    const ws = createWebSocket(wsPath);
    wsRef.current = ws;

    ws.onopen = () => {
      if (!mountedRef.current) return;
      setConnectionState("connected");
      reconnectAttemptRef.current = 0;
    };

    ws.onmessage = (event) => {
      if (!mountedRef.current) return;

      try {
        const data = JSON.parse(event.data as string);

        if (data.type === "token" && streamingMessageIdRef.current) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === streamingMessageIdRef.current
                ? { ...m, content: m.content + data.content }
                : m,
            ),
          );
          return;
        }

        if (data.type === "start") {
          const assistantMsg: ChatMessage = {
            id: data.id ?? crypto.randomUUID(),
            role: "assistant",
            content: "",
            timestamp: Date.now(),
            streaming: true,
          };
          streamingMessageIdRef.current = assistantMsg.id;
          setMessages((prev) => [...prev, assistantMsg]);
          return;
        }

        if (data.type === "end" && streamingMessageIdRef.current) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === streamingMessageIdRef.current
                ? {
                    ...m,
                    streaming: false,
                    faceRecognition: data.face_recognition,
                  }
                : m,
            ),
          );
          streamingMessageIdRef.current = null;
          return;
        }

        if (data.type === "message") {
          const msg: ChatMessage = {
            id: data.id ?? crypto.randomUUID(),
            role: data.role ?? "assistant",
            content: data.content,
            timestamp: data.timestamp ?? Date.now(),
            faceRecognition: data.face_recognition,
          };
          setMessages((prev) => [...prev, msg]);
          return;
        }

        if (data.type === "error") {
          setError(data.message ?? "Server error");
        }
      } catch {
        if (streamingMessageIdRef.current) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === streamingMessageIdRef.current
                ? { ...m, content: m.content + (event.data as string) }
                : m,
            ),
          );
        }
      }
    };

    ws.onerror = () => {
      if (!mountedRef.current) return;
      setConnectionState("error");
      setError("WebSocket connection error");
    };

    ws.onclose = () => {
      if (!mountedRef.current) return;
      setConnectionState("disconnected");

      if (reconnectAttemptRef.current < maxReconnectAttempts) {
        const delay = Math.min(1000 * 2 ** reconnectAttemptRef.current, 30_000);
        reconnectAttemptRef.current += 1;
        reconnectTimerRef.current = setTimeout(connect, delay);
      }
    };
  }, [wsPath, maxReconnectAttempts]);

  const sendMessage = useCallback(
    async (text: string, attachments: Attachment[] = []) => {
      const processedAttachments = await Promise.all(
        attachments.map(async (att) => {
          if (!att.base64) {
            att.base64 = await fileToBase64(att.file);
          }
          return {
            type: att.type,
            name: att.file.name,
            data: att.base64,
          };
        }),
      );

      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
        timestamp: Date.now(),
        attachments: attachments.map((a) => ({
          type: a.type,
          name: a.file.name,
          url: a.preview,
        })),
      };

      setMessages((prev) => [...prev, userMsg]);

      const payload = {
        type: "message",
        content: text,
        attachments: processedAttachments,
      };

      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(payload));
      } else {
        setError("Not connected. Attempting to reconnect...");
        connect();
        const trySend = () => {
          if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(payload));
            wsRef.current.removeEventListener("open", trySend);
          }
        };
        wsRef.current?.addEventListener("open", trySend);
      }
    },
    [connect],
  );

  const clearHistory = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const reconnect = useCallback(() => {
    reconnectAttemptRef.current = 0;
    connect();
  }, [connect]);

  return {
    messages,
    connectionState,
    error,
    sendMessage,
    clearHistory,
    connect,
    reconnect,
  };
}

function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve((reader.result as string).split(",")[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

const ALLOWED: Record<AttachmentType, string[]> = {
  image: ["image/jpeg", "image/png", "image/webp"],
  audio: ["audio/wav", "audio/mpeg", "audio/mp4", "audio/x-m4a"],
  video: ["video/mp4", "video/quicktime"],
};

export function classifyFile(file: File): AttachmentType | null {
  for (const [type, mimes] of Object.entries(ALLOWED)) {
    if (mimes.includes(file.type)) return type as AttachmentType;
  }
  const ext = file.name.split(".").pop()?.toLowerCase() ?? "";
  if (["jpg", "jpeg", "png", "webp"].includes(ext)) return "image";
  if (["wav", "mp3", "m4a"].includes(ext)) return "audio";
  if (["mp4", "mov"].includes(ext)) return "video";
  return null;
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / k ** i).toFixed(1))} ${sizes[i]}`;
}
