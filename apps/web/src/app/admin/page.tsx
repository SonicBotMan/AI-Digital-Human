"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { FileText, Sparkles, Cpu, Loader2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { SystemPromptEditor } from "@/components/admin/SystemPromptEditor";
import { StyleConfigurator } from "@/components/admin/StyleConfigurator";
import { ModelSelector } from "@/components/admin/ModelSelector";
import { AccountSettings } from "@/components/admin/AccountSettings";
import { isAdminAuthenticated } from "@/lib/adminAuth";

export default function AdminPage() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    if (!isAdminAuthenticated()) {
      router.replace("/admin/login");
    } else {
      setChecking(false);
    }
  }, [router]);

  if (checking) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Admin Panel</h1>
        <p className="mt-2 text-muted-foreground">
          Manage system prompts, speaking styles, and model configuration.
        </p>
      </div>

      <Tabs defaultValue="prompts" className="w-full">
        <TabsList className="w-full justify-start">
          <TabsTrigger value="prompts" className="gap-2">
            <FileText className="h-4 w-4" />
            Prompts
          </TabsTrigger>
          <TabsTrigger value="styles" className="gap-2">
            <Sparkles className="h-4 w-4" />
            Speaking Styles
          </TabsTrigger>
          <TabsTrigger value="models" className="gap-2">
            <Cpu className="h-4 w-4" />
            Models
          </TabsTrigger>
          <TabsTrigger value="security" className="gap-2">
            <Loader2 className="h-4 w-4" />
            Security
          </TabsTrigger>
        </TabsList>

        <TabsContent value="prompts" className="mt-6">
          <SystemPromptEditor />
        </TabsContent>

        <TabsContent value="styles" className="mt-6">
          <StyleConfigurator />
        </TabsContent>

        <TabsContent value="models" className="mt-6">
          <ModelSelector />
        </TabsContent>

        <TabsContent value="security" className="mt-6">
          <AccountSettings />
        </TabsContent>
      </Tabs>
    </div>
  );
}
