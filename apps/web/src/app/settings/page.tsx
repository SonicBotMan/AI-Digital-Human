"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Loader2, KeyRound } from "lucide-react";
import { api } from "@/lib/api";

type SettingsData = {
  LLM_PROVIDER: string;
  GLM_API_KEY: string;
  OPENAI_API_KEY: string;
  MINIMAX_API_KEY: string;
};

export default function SettingsPage() {
  const [data, setData] = useState<SettingsData>({
    LLM_PROVIDER: "glm",
    GLM_API_KEY: "",
    OPENAI_API_KEY: "",
    MINIMAX_API_KEY: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    api.get<SettingsData>("/api/settings")
      .then((res) => {
        setData(res);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setSuccess(false);
    setData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccess(false);
    try {
      await api.put("/api/settings", data);
      setSuccess(true);
    } catch (err) {
      alert("Failed to save settings: " + (err as Error).message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl p-6 md:p-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Model Settings</h1>
        <p className="mt-2 text-muted-foreground">
          Configure your AI providers and API keys to connect the digital human to your preferred intelligence core.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-8 rounded-xl border bg-card p-6 shadow-sm">
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Default Large Language Model</label>
            <select
              name="LLM_PROVIDER"
              value={data.LLM_PROVIDER || "glm"}
              onChange={handleChange}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="glm">GLM (ZhipuAI / ChatGLM)</option>
              <option value="openai">OpenAI (GPT Entities)</option>
              <option value="minimax">MiniMax</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <KeyRound className="h-4 w-4" /> GLM API Key
            </label>
            <input
              type="text"
              name="GLM_API_KEY"
              value={data.GLM_API_KEY}
              onChange={handleChange}
              placeholder="Your GLM API Key"
              className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <KeyRound className="h-4 w-4" /> OpenAI API Key
            </label>
            <input
              type="text"
              name="OPENAI_API_KEY"
              value={data.OPENAI_API_KEY}
              onChange={handleChange}
              placeholder="sk-..."
              className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <KeyRound className="h-4 w-4" /> MiniMax API Key
            </label>
            <input
              type="text"
              name="MINIMAX_API_KEY"
              value={data.MINIMAX_API_KEY}
              onChange={handleChange}
              placeholder="Your MiniMax Key"
              className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
          <Button type="submit" disabled={saving} className="bg-primary hover:bg-primary/90 text-primary-foreground min-w-[120px]">
            {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Save configurations"}
          </Button>
          {success && <span className="text-sm text-green-500 font-medium">Saved Successfully!</span>}
        </div>
      </form>
    </div>
  );
}
