"use client";

import { useState, useEffect, useCallback } from "react";
import { Save, Loader2, AlertCircle, Cpu } from "lucide-react";
import { adminApi, ApiError } from "@/lib/adminApi";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
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

type VendorConfig = {
  api_key?: string;
  base_url?: string;
  group_id?: string;
};

type ModelConfig = {
  llm_model: string;
  vision_model: string;
  stt_model: string;
  temperature: number;
  max_tokens: number;
  vendor_configs: Record<string, VendorConfig>;
};

const LLM_MODELS = [
  // GLM Models
  { value: "glm-4-flash", label: "GLM-4 Flash (快速, 推荐)" },
  { value: "glm-4", label: "GLM-4 (高性能)" },
  { value: "glm-4-plus", label: "GLM-4 Plus" },
  { value: "glm-3-5-turbo", label: "GLM-3.5 Turbo" },
  // MiniMax Models
  { value: "MiniMax-Text-01", label: "MiniMax Text-01 (海螺AI)" },
  // OpenAI Models (kept for compatibility)
  { value: "gpt-4o", label: "GPT-4o" },
  { value: "gpt-4o-mini", label: "GPT-4o Mini" },
  { value: "gpt-4-turbo", label: "GPT-4 Turbo" },
];

const VISION_MODELS = [
  // GLM Vision Models
  { value: "glm-4v-flash", label: "GLM-4V Flash (快速, 推荐)" },
  { value: "glm-4v-plus", label: "GLM-4V Plus" },
  // OpenAI Vision Models (kept for compatibility)
  { value: "gpt-4o", label: "GPT-4o" },
  { value: "gpt-4-vision-preview", label: "GPT-4 Vision" },
];

const STT_MODELS = [
  // Whisper models (CPU-friendly)
  { value: "turbo", label: "Whisper Turbo (推荐)" },
  { value: "base", label: "Whisper Base" },
  { value: "small", label: "Whisper Small" },
  { value: "medium", label: "Whisper Medium" },
];

export function ModelSelector() {
  const [config, setConfig] = useState<ModelConfig>({
    llm_model: "glm-4-flash",
    vision_model: "glm-4v-flash",
    stt_model: "turbo",
    temperature: 0.7,
    max_tokens: 2048,
    vendor_configs: {},
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const fetchConfig = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await adminApi.get<ModelConfig>("/admin/models");
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
      await adminApi.put("/admin/models", config);
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
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  value={config.max_tokens}
                  onChange={(e) =>
                    setConfig((c) => ({
                      ...c,
                      max_tokens: parseInt(e.target.value, 10) || 0,
                    }))
                  }
                  className="h-8 w-24 font-mono text-xs"
                  min={256}
                  max={32768}
                />
                <span className="text-xs text-muted-foreground">tokens</span>
              </div>
            </div>
            <input
              type="range"
              min="256"
              max="16384"
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
              <span>Long (16384+)</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Provider Credentials</CardTitle>
          <CardDescription className="text-xs">
            Configure API keys and Base URLs for LLM providers. These will override environment variables.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* GLM Config */}
          <div className="space-y-4 rounded-lg border p-4">
            <h4 className="text-sm font-semibold text-primary">智谱AI (GLM)</h4>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="glm-api-key">API Key</Label>
                <Input
                  id="glm-api-key"
                  type="password"
                  placeholder="Leave empty to use .env"
                  value={config.vendor_configs.glm?.api_key || ""}
                  onChange={(e) =>
                    setConfig((c) => ({
                      ...c,
                      vendor_configs: {
                        ...c.vendor_configs,
                        glm: { ...c.vendor_configs.glm, api_key: e.target.value },
                      },
                    }))
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="glm-base-url">Base URL</Label>
                <Input
                  id="glm-base-url"
                  placeholder="https://open.bigmodel.cn/api/paas/v4"
                  value={config.vendor_configs.glm?.base_url || ""}
                  onChange={(e) =>
                    setConfig((c) => ({
                      ...c,
                      vendor_configs: {
                        ...c.vendor_configs,
                        glm: { ...c.vendor_configs.glm, base_url: e.target.value },
                      },
                    }))
                  }
                />
              </div>
            </div>
          </div>

          {/* OpenAI Config */}
          <div className="space-y-4 rounded-lg border p-4">
            <h4 className="text-sm font-semibold text-primary">OpenAI</h4>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="openai-api-key">API Key</Label>
                <Input
                  id="openai-api-key"
                  type="password"
                  placeholder="sk-..."
                  value={config.vendor_configs.openai?.api_key || ""}
                  onChange={(e) =>
                    setConfig((c) => ({
                      ...c,
                      vendor_configs: {
                        ...c.vendor_configs,
                        openai: { ...c.vendor_configs.openai, api_key: e.target.value },
                      },
                    }))
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="openai-base-url">Base URL</Label>
                <Input
                  id="openai-base-url"
                  placeholder="https://api.openai.com/v1"
                  value={config.vendor_configs.openai?.base_url || ""}
                  onChange={(e) =>
                    setConfig((c) => ({
                      ...c,
                      vendor_configs: {
                        ...c.vendor_configs,
                        openai: { ...c.vendor_configs.openai, base_url: e.target.value },
                      },
                    }))
                  }
                />
              </div>
            </div>
          </div>

          {/* MiniMax Config */}
          <div className="space-y-4 rounded-lg border p-4">
            <h4 className="text-sm font-semibold text-primary">MiniMax</h4>
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="minimax-api-key">API Key</Label>
                <Input
                  id="minimax-api-key"
                  type="password"
                  value={config.vendor_configs.minimax?.api_key || ""}
                  onChange={(e) =>
                    setConfig((c) => ({
                      ...c,
                      vendor_configs: {
                        ...c.vendor_configs,
                        minimax: { ...c.vendor_configs.minimax, api_key: e.target.value },
                      },
                    }))
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="minimax-group-id">Group ID</Label>
                <Input
                  id="minimax-group-id"
                  value={config.vendor_configs.minimax?.group_id || ""}
                  onChange={(e) =>
                    setConfig((c) => ({
                      ...c,
                      vendor_configs: {
                        ...c.vendor_configs,
                        minimax: { ...c.vendor_configs.minimax, group_id: e.target.value },
                      },
                    }))
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="minimax-base-url">Base URL</Label>
                <Input
                  id="minimax-base-url"
                  placeholder="https://api.minimax.chat/v1"
                  value={config.vendor_configs.minimax?.base_url || ""}
                  onChange={(e) =>
                    setConfig((c) => ({
                      ...c,
                      vendor_configs: {
                        ...c.vendor_configs,
                        minimax: { ...c.vendor_configs.minimax, base_url: e.target.value },
                      },
                    }))
                  }
                />
              </div>
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
