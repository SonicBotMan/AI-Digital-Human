"use client";

import { useEffect, useMemo } from "react";
import {
  Wifi,
  WifiOff,
  Loader2,
  RotateCcw,
  Trash2,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { InputBar } from "@/components/chat/InputBar";
import { useChat, type ConnectionState } from "@/hooks/useChat";
import { cn } from "@/lib/utils";

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

  useEffect(() => {
    connect();
  }, [connect]);

  const isStreaming = useMemo(
    () => messages.some((m) => m.streaming),
    [messages],
  );

  const isConnected = connectionState === "connected";

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b px-4 py-2">
        <ConnectionStatus state={connectionState} />
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

      {error && (
        <div className="flex items-center gap-2 border-b bg-destructive/10 px-4 py-2 text-xs text-destructive">
          <AlertCircle className="h-3.5 w-3.5 shrink-0" />
          {error}
        </div>
      )}

      <ChatPanel messages={messages} />

      <InputBar onSend={sendMessage} disabled={isStreaming || !isConnected} />
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
