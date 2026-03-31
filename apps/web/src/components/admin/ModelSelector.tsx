"use client";

import { useState, useEffect, useCallback } from "react";
import { Save, Loader2, AlertCircle, Cpu } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type ModelConfig = {
  llm_model: string;
  vision_model: string;
  stt_model: string;
  temperature: number;
  max_tokens: number;
};

const LLM_MODELS = [
  { value: "gpt-4o", label: "GPT-4o" },
  { value: "gpt-4o-mini", label: "GPT-4o Mini" },
  { value: "gpt-4-turbo", label: "GPT-4 Turbo" },
  { value: "gpt-3.5-turbo", label: "GPT-3.5 Turbo" },
  { value: "claude-3-opus", label: "Claude 3 Opus" },
  { value: "claude-3-sonnet", label: "Claude 3 Sonnet" },
  { value: "claude-3-haiku", label: "Claude 3 Haiku" },
];

const VISION_MODELS = [
  { value: "gpt-4o", label: "GPT-4o" },
  { value: "gpt-4-vision-preview", label: "GPT-4 Vision" },
  { value: "claude-3-opus", label: "Claude 3 Opus" },
  { value: "claude-3-sonnet", label: "Claude 3 Sonnet" },
];

const STT_MODELS = [
  { value: "whisper-1", label: "Whisper v1" },
  { value: "whisper-large-v3", label: "Whisper Large v3" },
  { value: "deepgram-nova-2", label: "Deepgram Nova 2" },
];

export function ModelSelector() {
  const [config, setConfig] = useState<ModelConfig>({
    llm_model: "gpt-4o",
    vision_model: "gpt-4o",
    stt_model: "whisper-1",
    temperature: 0.7,
    max_tokens: 2048,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const fetchConfig = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.get<ModelConfig>("/admin/models");
      setConfig(data);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to load model config",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  async function handleSave() {
    try {
      setSaving(true);
      setError(null);
      setSuccess(false);
      await api.put("/admin/models", config);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to save configuration",
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        {[1, 2].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-5 w-40 rounded bg-muted" />
              <div className="h-4 w-64 rounded bg-muted" />
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="h-10 w-full rounded bg-muted" />
              <div className="h-10 w-full rounded bg-muted" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
          <Button
            variant="ghost"
            size="sm"
            className="ml-auto"
            onClick={() => setError(null)}
          >
            Dismiss
          </Button>
        </div>
      )}

      {success && (
        <div className="rounded-lg border border-green-500/50 bg-green-500/10 p-3 text-sm text-green-700 dark:text-green-400">
          Configuration saved successfully.
        </div>
      )}

      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Model Configuration</h3>
          <p className="text-sm text-muted-foreground">
            Select and configure the AI models used across the system.
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">LLM Model</CardTitle>
            <CardDescription className="text-xs">
              Primary language model for text generation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Select
              value={config.llm_model}
              onValueChange={(v) => setConfig((c) => ({ ...c, llm_model: v }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select LLM model" />
              </SelectTrigger>
              <SelectContent>
                {LLM_MODELS.map((m) => (
                  <SelectItem key={m.value} value={m.value}>
                    {m.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Vision Model</CardTitle>
            <CardDescription className="text-xs">
              Model for image understanding and analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Select
              value={config.vision_model}
              onValueChange={(v) =>
                setConfig((c) => ({ ...c, vision_model: v }))
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Select vision model" />
              </SelectTrigger>
              <SelectContent>
                {VISION_MODELS.map((m) => (
                  <SelectItem key={m.value} value={m.value}>
                    {m.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">
              Speech-to-Text Model
            </CardTitle>
            <CardDescription className="text-xs">
              Model for audio transcription
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Select
              value={config.stt_model}
              onValueChange={(v) => setConfig((c) => ({ ...c, stt_model: v }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select STT model" />
              </SelectTrigger>
              <SelectContent>
                {STT_MODELS.map((m) => (
                  <SelectItem key={m.value} value={m.value}>
                    {m.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
            <Cpu className="h-5 w-5 text-primary" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium">Active Configuration</p>
            <p className="truncate text-xs text-muted-foreground">
              LLM: {config.llm_model} · Vision: {config.vision_model} · STT:{" "}
              {config.stt_model}
            </p>
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Generation Parameters
          </CardTitle>
          <CardDescription className="text-xs">
            Fine-tune the model&apos;s response behavior.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>Temperature</Label>
              <span className="text-sm font-mono text-muted-foreground">
                {config.temperature.toFixed(2)}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="2"
              step="0.05"
              value={config.temperature}
              onChange={(e) =>
                setConfig((c) => ({
                  ...c,
                  temperature: parseFloat(e.target.value),
                }))
              }
              className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-secondary accent-primary"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Precise (0)</span>
              <span>Balanced (1)</span>
              <span>Creative (2)</span>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>Max Tokens</Label>
              <span className="text-sm font-mono text-muted-foreground">
                {config.max_tokens.toLocaleString()}
              </span>
            </div>
            <input
              type="range"
              min="256"
              max="8192"
              step="256"
              value={config.max_tokens}
              onChange={(e) =>
                setConfig((c) => ({
                  ...c,
                  max_tokens: parseInt(e.target.value, 10),
                }))
              }
              className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-secondary accent-primary"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Short (256)</span>
              <span>Medium (2048)</span>
              <span>Long (8192)</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button
          onClick={handleSave}
          disabled={saving}
          className="min-w-[140px]"
        >
          {saving ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Save className="mr-2 h-4 w-4" />
          )}
          Save Configuration
        </Button>
      </div>
    </div>
  );
}
