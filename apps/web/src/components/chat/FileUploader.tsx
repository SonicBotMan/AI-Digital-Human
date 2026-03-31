"use client";

import { useCallback, useRef, useState } from "react";
import { Image, Music, Video, X } from "lucide-react";
import {
  classifyFile,
  formatBytes,
  type Attachment,
  type AttachmentType,
} from "@/hooks/useChat";

interface FileUploaderProps {
  attachments: Attachment[];
  onAttachmentsChange: (files: Attachment[]) => void;
  maxFileSizeMB?: number;
}

const TYPE_ICONS: Record<AttachmentType, typeof Image> = {
  image: Image,
  audio: Music,
  video: Video,
};

export function FileUploader({
  attachments,
  onAttachmentsChange,
  maxFileSizeMB = 25,
}: FileUploaderProps) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const addFiles = useCallback(
    (fileList: FileList | File[]) => {
      const newAttachments: Attachment[] = [];

      Array.from(fileList).forEach((file) => {
        const type = classifyFile(file);
        if (!type) return;
        if (file.size > maxFileSizeMB * 1024 * 1024) return;

        const attachment: Attachment = {
          id: crypto.randomUUID(),
          file,
          type,
        };

        if (type === "image") {
          attachment.preview = URL.createObjectURL(file);
        }

        newAttachments.push(attachment);
      });

      if (newAttachments.length > 0) {
        onAttachmentsChange([...attachments, ...newAttachments]);
      }
    },
    [attachments, onAttachmentsChange, maxFileSizeMB],
  );

  const removeAttachment = useCallback(
    (id: string) => {
      const att = attachments.find((a) => a.id === id);
      if (att?.preview) URL.revokeObjectURL(att.preview);
      onAttachmentsChange(attachments.filter((a) => a.id !== id));
    },
    [attachments, onAttachmentsChange],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (e.dataTransfer.files.length > 0) {
        addFiles(e.dataTransfer.files);
      }
    },
    [addFiles],
  );

  const openPicker = useCallback(
    (acceptType?: AttachmentType) => {
      const input = inputRef.current;
      if (!input) return;

      const acceptMap: Record<AttachmentType, string> = {
        image: "image/jpeg,image/png,image/webp",
        audio: "audio/wav,audio/mpeg,audio/mp4,audio/x-m4a",
        video: "video/mp4,video/quicktime",
      };

      input.accept = acceptType
        ? acceptMap[acceptType]
        : Object.values(acceptMap).join(",");
      input.onchange = () => {
        if (input.files) addFiles(input.files);
        input.value = "";
      };
      input.click();
    },
    [addFiles],
  );

  return (
    <div
      className="relative space-y-2"
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
    >
      <input ref={inputRef} type="file" multiple className="hidden" />

      <div className="flex items-center gap-1">
        <button
          type="button"
          onClick={() => openPicker("image")}
          className="rounded-md p-2 text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
          title="Upload image"
        >
          <Image className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={() => openPicker("audio")}
          className="rounded-md p-2 text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
          title="Upload audio"
        >
          <Music className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={() => openPicker("video")}
          className="rounded-md p-2 text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
          title="Upload video"
        >
          <Video className="h-4 w-4" />
        </button>
      </div>

      {attachments.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {attachments.map((att) => (
            <FilePreview
              key={att.id}
              attachment={att}
              onRemove={removeAttachment}
            />
          ))}
        </div>
      )}

      {dragOver && (
        <div className="absolute inset-0 z-10 flex items-center justify-center rounded-lg border-2 border-dashed border-primary bg-primary/5">
          <p className="text-sm font-medium text-primary">Drop files here</p>
        </div>
      )}
    </div>
  );
}

function FilePreview({
  attachment,
  onRemove,
}: {
  attachment: Attachment;
  onRemove: (id: string) => void;
}) {
  const Icon = TYPE_ICONS[attachment.type] ?? Video;

  return (
    <div className="group relative flex items-center gap-2 rounded-lg border bg-card px-2 py-1.5 pr-8 text-xs">
      {attachment.type === "image" && attachment.preview ? (
        <img
          src={attachment.preview}
          alt={attachment.file.name}
          className="h-8 w-8 rounded object-cover"
        />
      ) : (
        <div className="flex h-8 w-8 items-center justify-center rounded bg-muted">
          <Icon className="h-4 w-4 text-muted-foreground" />
        </div>
      )}
      <div className="flex flex-col">
        <span className="max-w-[120px] truncate font-medium">
          {attachment.file.name}
        </span>
        <span className="text-muted-foreground">
          {formatBytes(attachment.file.size)}
        </span>
      </div>
      <button
        type="button"
        onClick={() => onRemove(attachment.id)}
        className="absolute -right-1 -top-1 rounded-full bg-muted p-0.5 opacity-0 transition-opacity group-hover:opacity-100"
      >
        <X className="h-3 w-3" />
      </button>
    </div>
  );
}
