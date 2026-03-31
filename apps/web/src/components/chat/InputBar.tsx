"use client";

import { useCallback, useRef, useState, type KeyboardEvent } from "react";
import { Send, Paperclip } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FileUploader } from "./FileUploader";
import type { Attachment } from "@/hooks/useChat";

interface InputBarProps {
  onSend: (text: string, attachments: Attachment[]) => void;
  disabled?: boolean;
}

export function InputBar({ onSend, disabled = false }: InputBarProps) {
  const [text, setText] = useState("");
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [showUploader, setShowUploader] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = useCallback(() => {
    const trimmed = text.trim();
    if (!trimmed && attachments.length === 0) return;
    if (disabled) return;

    onSend(trimmed, attachments);
    setText("");
    setAttachments([]);
    setShowUploader(false);

    requestAnimationFrame(() => {
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    });
  }, [text, attachments, disabled, onSend]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend],
  );

  const handleTextChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setText(e.target.value);
      const el = e.target;
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
    },
    [],
  );

  const hasContent = text.trim().length > 0 || attachments.length > 0;

  return (
    <div className="border-t bg-card px-4 py-3">
      <div className="mx-auto max-w-3xl">
        {showUploader && (
          <div className="mb-2">
            <FileUploader
              attachments={attachments}
              onAttachmentsChange={setAttachments}
            />
          </div>
        )}

        <div className="flex items-end gap-2">
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="shrink-0"
            onClick={() => setShowUploader((v) => !v)}
            disabled={disabled}
            title="Attach files"
          >
            <Paperclip className="h-4 w-4" />
          </Button>

          <div className="relative flex-1">
            <textarea
              ref={textareaRef}
              value={text}
              onChange={handleTextChange}
              onKeyDown={handleKeyDown}
              placeholder={
                disabled ? "Waiting for response..." : "Type a message..."
              }
              disabled={disabled}
              rows={1}
              className="flex max-h-40 min-h-[40px] w-full resize-none rounded-lg border border-input bg-background px-4 py-2.5 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>

          <Button
            type="button"
            size="icon"
            className="shrink-0"
            onClick={handleSend}
            disabled={disabled || !hasContent}
            title="Send message"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
