"use client";

import { useEffect, useRef } from "react";
import { Bot, User, Loader2, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ChatMessage } from "@/hooks/useChat";

interface ChatPanelProps {
  messages: ChatMessage[];
}

export function ChatPanel({ messages }: ChatPanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center px-6">
        <div className="mx-auto max-w-md text-center">
          <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-primary/10">
            <Bot className="h-10 w-10 text-primary" />
          </div>
          <h3 className="text-xl font-semibold tracking-tight">
            Start a conversation
          </h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Send a message or upload an image for face recognition analysis.
            Supports images, audio, and video files.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="mx-auto max-w-3xl space-y-6">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  const isStreaming = message.streaming;

  return (
    <div className={cn("flex gap-3", isUser ? "flex-row-reverse" : "flex-row")}>
      <Avatar role={message.role} />

      <div
        className={cn(
          "flex max-w-[75%] flex-col gap-1.5",
          isUser ? "items-end" : "items-start",
        )}
      >
        {message.attachments && message.attachments.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {message.attachments.map((att, i) => (
              <AttachmentPreview key={i} attachment={att} />
            ))}
          </div>
        )}

        {message.content && (
          <div
            className={cn(
              "rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
              isUser
                ? "rounded-tr-sm bg-primary text-primary-foreground"
                : "rounded-tl-sm bg-muted text-foreground",
            )}
          >
            {message.content}
            {isStreaming && (
              <span className="ml-1 inline-block h-4 w-1 animate-pulse bg-foreground/50" />
            )}
          </div>
        )}

        {isStreaming && !message.content && (
          <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm bg-muted px-4 py-3 text-sm text-muted-foreground">
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
            Thinking...
          </div>
        )}

        {message.faceRecognition && (
          <div className="flex items-center gap-1.5 rounded-lg border border-primary/20 bg-primary/5 px-3 py-1.5 text-xs text-primary">
            <ShieldCheck className="h-3.5 w-3.5" />
            Recognized: {message.faceRecognition.name} (
            {(message.faceRecognition.confidence * 100).toFixed(1)}%)
          </div>
        )}

        <span className="px-1 text-[10px] text-muted-foreground/60">
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
}

function Avatar({ role }: { role: ChatMessage["role"] }) {
  const isUser = role === "user";

  return (
    <div
      className={cn(
        "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
        isUser ? "bg-primary/10" : "bg-muted",
      )}
    >
      {isUser ? (
        <User className="h-4 w-4 text-primary" />
      ) : (
        <Bot className="h-4 w-4 text-muted-foreground" />
      )}
    </div>
  );
}

function AttachmentPreview({
  attachment,
}: {
  attachment: NonNullable<ChatMessage["attachments"]>[number];
}) {
  if (attachment.type === "image" && attachment.url) {
    return (
      <img
        src={attachment.url}
        alt={attachment.name}
        className="h-40 max-w-[280px] rounded-lg border object-cover"
      />
    );
  }

  return (
    <div className="flex items-center gap-2 rounded-lg border bg-card px-3 py-2 text-xs">
      <FileIcon type={attachment.type} />
      <span className="max-w-[140px] truncate">{attachment.name}</span>
    </div>
  );
}

function FileIcon({ type }: { type: string }) {
  const base = "h-4 w-4 text-muted-foreground";
  switch (type) {
    case "image":
      return (
        <svg
          className={base}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <polyline points="21 15 16 10 5 21" />
        </svg>
      );
    case "audio":
      return (
        <svg
          className={base}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M9 18V5l12-2v13" />
          <circle cx="6" cy="18" r="3" />
          <circle cx="18" cy="16" r="3" />
        </svg>
      );
    default:
      return (
        <svg
          className={base}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
          <polyline points="14 2 14 8 20 8" />
        </svg>
      );
  }
}

function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}
