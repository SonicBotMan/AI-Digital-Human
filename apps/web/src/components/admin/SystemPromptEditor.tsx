"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Plus,
  Pencil,
  Trash2,
  Star,
  Loader2,
  AlertCircle,
  FileText,
} from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

type SystemPrompt = {
  id: string;
  name: string;
  content: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
};

type FormData = {
  name: string;
  content: string;
};

const emptyForm: FormData = { name: "", content: "" };

export function SystemPromptEditor() {
  const [prompts, setPrompts] = useState<SystemPrompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<FormData>(emptyForm);
  const [formErrors, setFormErrors] = useState<Partial<FormData>>({});

  const [deleteTarget, setDeleteTarget] = useState<SystemPrompt | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchPrompts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.get<SystemPrompt[]>("/admin/prompts");
      setPrompts(data);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to load prompts",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPrompts();
  }, [fetchPrompts]);

  function openCreate() {
    setEditingId(null);
    setForm(emptyForm);
    setFormErrors({});
    setFormOpen(true);
  }

  function openEdit(prompt: SystemPrompt) {
    setEditingId(prompt.id);
    setForm({ name: prompt.name, content: prompt.content });
    setFormErrors({});
    setFormOpen(true);
  }

  function validate(): boolean {
    const errors: Partial<FormData> = {};
    if (!form.name.trim()) errors.name = "Name is required";
    if (!form.content.trim()) errors.content = "Content is required";
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSave() {
    if (!validate()) return;

    try {
      setSaving(true);
      if (editingId) {
        await api.put(`/admin/prompts/${editingId}`, form);
      } else {
        await api.post("/admin/prompts", form);
      }
      setFormOpen(false);
      fetchPrompts();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to save prompt");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    try {
      setDeleting(true);
      await api.delete(`/admin/prompts/${deleteTarget.id}`);
      setDeleteTarget(null);
      fetchPrompts();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to delete prompt",
      );
    } finally {
      setDeleting(false);
    }
  }

  async function handleSetDefault(prompt: SystemPrompt) {
    try {
      await api.put(`/admin/prompts/${prompt.id}`, { is_default: true });
      fetchPrompts();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to set default");
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="pb-3">
              <div className="h-5 w-40 rounded bg-muted" />
              <div className="h-4 w-24 rounded bg-muted" />
            </CardHeader>
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

      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">System Prompts</h3>
          <p className="text-sm text-muted-foreground">
            Manage the system prompts that shape AI behavior and personality.
          </p>
        </div>
        <Button onClick={openCreate}>
          <Plus className="mr-2 h-4 w-4" />
          New Prompt
        </Button>
      </div>

      {prompts.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="h-10 w-10 text-muted-foreground/50" />
            <p className="mt-3 text-sm font-medium text-muted-foreground">
              No system prompts yet
            </p>
            <p className="text-xs text-muted-foreground/70">
              Create your first prompt to get started.
            </p>
            <Button variant="outline" className="mt-4" onClick={openCreate}>
              <Plus className="mr-2 h-4 w-4" />
              Create Prompt
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {prompts.map((prompt) => (
            <Card
              key={prompt.id}
              className="group transition-shadow hover:shadow-md"
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-base">{prompt.name}</CardTitle>
                    {prompt.is_default && (
                      <Badge variant="secondary" className="text-xs">
                        <Star className="mr-1 h-3 w-3" />
                        Default
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                    {!prompt.is_default && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleSetDefault(prompt)}
                        title="Set as default"
                      >
                        <Star className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openEdit(prompt)}
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-destructive hover:text-destructive"
                      onClick={() => setDeleteTarget(prompt)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <CardDescription className="line-clamp-2 text-xs">
                  {prompt.content}
                </CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>
              {editingId ? "Edit System Prompt" : "Create System Prompt"}
            </DialogTitle>
            <DialogDescription>
              {editingId
                ? "Modify the prompt name and content."
                : "Define a new system prompt for the AI."}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label htmlFor="prompt-name">Name</Label>
              <Input
                id="prompt-name"
                placeholder="e.g. Customer Support Agent"
                value={form.name}
                onChange={(e) =>
                  setForm((f) => ({ ...f, name: e.target.value }))
                }
                aria-invalid={!!formErrors.name}
              />
              {formErrors.name && (
                <p className="text-xs text-destructive">{formErrors.name}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="prompt-content">Content</Label>
              <Textarea
                id="prompt-content"
                placeholder="You are a helpful assistant that..."
                value={form.content}
                onChange={(e) =>
                  setForm((f) => ({ ...f, content: e.target.value }))
                }
                className="min-h-[200px] font-mono text-sm"
                aria-invalid={!!formErrors.content}
              />
              {formErrors.content && (
                <p className="text-xs text-destructive">{formErrors.content}</p>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setFormOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {editingId ? "Save Changes" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
      >
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Delete Prompt</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete &ldquo;{deleteTarget?.name}
              &rdquo;? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleting}
            >
              {deleting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
