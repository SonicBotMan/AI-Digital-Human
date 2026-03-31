"use client";

import { FileText, Sparkles, Cpu } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { SystemPromptEditor } from "@/components/admin/SystemPromptEditor";
import { StyleConfigurator } from "@/components/admin/StyleConfigurator";
import { ModelSelector } from "@/components/admin/ModelSelector";

export default function AdminPage() {
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
      </Tabs>
    </div>
  );
}
