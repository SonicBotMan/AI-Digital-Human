"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Plus,
  Pencil,
  Trash2,
  Star,
  Loader2,
  AlertCircle,
  Sparkles,
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

type SpeakingStyle = {
  id: string;
  name: string;
  description: string;
  config: Record<string, unknown>;
  is_default: boolean;
  created_at: string;
  updated_at: string;
};

type FormData = {
  name: string;
  description: string;
  config: string;
};

const emptyForm: FormData = { name: "", description: "", config: "{}" };

export function StyleConfigurator() {
  const [styles, setStyles] = useState<SpeakingStyle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<FormData>(emptyForm);
  const [formErrors, setFormErrors] = useState<
    Partial<Record<keyof FormData, string>>
  >({});

  const [deleteTarget, setDeleteTarget] = useState<SpeakingStyle | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchStyles = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.get<SpeakingStyle[]>("/admin/styles");
      setStyles(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load styles");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStyles();
  }, [fetchStyles]);

  function openCreate() {
    setEditingId(null);
    setForm(emptyForm);
    setFormErrors({});
    setFormOpen(true);
  }

  function openEdit(style: SpeakingStyle) {
    setEditingId(style.id);
    setForm({
      name: style.name,
      description: style.description,
      config: JSON.stringify(style.config, null, 2),
    });
    setFormErrors({});
    setFormOpen(true);
  }

  function validate(): boolean {
    const errors: Partial<Record<keyof FormData, string>> = {};
    if (!form.name.trim()) errors.name = "Name is required";
    if (!form.description.trim())
      errors.description = "Description is required";
    try {
      JSON.parse(form.config);
    } catch {
      errors.config = "Must be valid JSON";
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSave() {
    if (!validate()) return;

    try {
      setSaving(true);
      const payload = {
        name: form.name,
        description: form.description,
        config: JSON.parse(form.config),
      };
      if (editingId) {
        await api.put(`/admin/styles/${editingId}`, payload);
      } else {
        await api.post("/admin/styles", payload);
      }
      setFormOpen(false);
      fetchStyles();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to save style");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    try {
      setDeleting(true);
      await api.delete(`/admin/styles/${deleteTarget.id}`);
      setDeleteTarget(null);
      fetchStyles();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to delete style",
      );
    } finally {
      setDeleting(false);
    }
  }

  async function handleSetDefault(style: SpeakingStyle) {
    try {
      await api.put(`/admin/styles/${style.id}`, { is_default: true });
      fetchStyles();
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
              <div className="h-5 w-36 rounded bg-muted" />
              <div className="h-4 w-56 rounded bg-muted" />
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
          <h3 className="text-lg font-semibold">Speaking Styles</h3>
          <p className="text-sm text-muted-foreground">
            Configure how the AI communicates — tone, pace, and personality.
          </p>
        </div>
        <Button onClick={openCreate}>
          <Plus className="mr-2 h-4 w-4" />
          New Style
        </Button>
      </div>

      {styles.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Sparkles className="h-10 w-10 text-muted-foreground/50" />
            <p className="mt-3 text-sm font-medium text-muted-foreground">
              No speaking styles yet
            </p>
            <p className="text-xs text-muted-foreground/70">
              Create your first style to define the AI&apos;s voice.
            </p>
            <Button variant="outline" className="mt-4" onClick={openCreate}>
              <Plus className="mr-2 h-4 w-4" />
              Create Style
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {styles.map((style) => (
            <Card
              key={style.id}
              className="group transition-shadow hover:shadow-md"
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-base">{style.name}</CardTitle>
                    {style.is_default && (
                      <Badge variant="secondary" className="text-xs">
                        <Star className="mr-1 h-3 w-3" />
                        Default
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                    {!style.is_default && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleSetDefault(style)}
                        title="Set as default"
                      >
                        <Star className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openEdit(style)}
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-destructive hover:text-destructive"
                      onClick={() => setDeleteTarget(style)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <CardDescription className="line-clamp-2">
                  {style.description}
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
              {editingId ? "Edit Speaking Style" : "Create Speaking Style"}
            </DialogTitle>
            <DialogDescription>
              {editingId
                ? "Modify the style settings."
                : "Define a new speaking style for the AI."}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label htmlFor="style-name">Name</Label>
              <Input
                id="style-name"
                placeholder="e.g. Professional, Casual, Friendly"
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
              <Label htmlFor="style-description">Description</Label>
              <Textarea
                id="style-description"
                placeholder="Describe the speaking style characteristics..."
                value={form.description}
                onChange={(e) =>
                  setForm((f) => ({ ...f, description: e.target.value }))
                }
                className="min-h-[80px]"
                aria-invalid={!!formErrors.description}
              />
              {formErrors.description && (
                <p className="text-xs text-destructive">
                  {formErrors.description}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="style-config">Configuration (JSON)</Label>
              <Textarea
                id="style-config"
                placeholder='{"tone": "professional", "formality": "high"}'
                value={form.config}
                onChange={(e) =>
                  setForm((f) => ({ ...f, config: e.target.value }))
                }
                className="min-h-[120px] font-mono text-sm"
                aria-invalid={!!formErrors.config}
              />
              {formErrors.config && (
                <p className="text-xs text-destructive">{formErrors.config}</p>
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
            <DialogTitle>Delete Style</DialogTitle>
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
