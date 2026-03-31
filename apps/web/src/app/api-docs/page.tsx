"use client";

import { useState } from "react";
import {
  BookOpen,
  Code2,
  ExternalLink,
  Copy,
  Check,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const SWAGGER_URL = "http://localhost:8000/docs";

type Endpoint = {
  method: "GET" | "POST" | "PUT" | "DELETE";
  path: string;
  description: string;
  request?: string;
  response?: string;
};

const endpoints: Endpoint[] = [
  {
    method: "GET",
    path: "/admin/prompts",
    description: "List all system prompts",
    response: `[
  {
    "id": "prompt-1",
    "name": "Default Assistant",
    "content": "You are a helpful assistant...",
    "is_default": true,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z"
  }
]`,
  },
  {
    method: "POST",
    path: "/admin/prompts",
    description: "Create a new system prompt",
    request: `{
  "name": "Custom Prompt",
  "content": "You are a specialized assistant..."
}`,
    response: `{
  "id": "prompt-2",
  "name": "Custom Prompt",
  "content": "You are a specialized assistant...",
  "is_default": false,
  "created_at": "2025-01-15T11:00:00Z",
  "updated_at": "2025-01-15T11:00:00Z"
}`,
  },
  {
    method: "PUT",
    path: "/admin/prompts/{id}",
    description: "Update a system prompt",
    request: `{
  "name": "Updated Prompt",
  "content": "You are an updated assistant...",
  "is_default": true
}`,
  },
  {
    method: "DELETE",
    path: "/admin/prompts/{id}",
    description: "Delete a system prompt",
  },
  {
    method: "GET",
    path: "/admin/styles",
    description: "List all speaking styles",
    response: `[
  {
    "id": "style-1",
    "name": "Professional",
    "description": "Formal and precise communication",
    "config": { "tone": "formal", "pace": "measured" },
    "is_default": true,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z"
  }
]`,
  },
  {
    method: "POST",
    path: "/admin/styles",
    description: "Create a new speaking style",
    request: `{
  "name": "Casual",
  "description": "Friendly and relaxed tone",
  "config": { "tone": "casual", "pace": "fast" }
}`,
  },
  {
    method: "PUT",
    path: "/admin/styles/{id}",
    description: "Update a speaking style",
    request: `{
  "name": "Updated Style",
  "description": "Modified style description",
  "config": { "tone": "balanced" }
}`,
  },
  {
    method: "DELETE",
    path: "/admin/styles/{id}",
    description: "Delete a speaking style",
  },
  {
    method: "GET",
    path: "/admin/models",
    description: "Get current model configuration",
    response: `{
  "llm_model": "gpt-4o",
  "vision_model": "gpt-4o",
  "stt_model": "whisper-1",
  "temperature": 0.7,
  "max_tokens": 2048
}`,
  },
  {
    method: "PUT",
    path: "/admin/models",
    description: "Update model configuration",
    request: `{
  "llm_model": "gpt-4o",
  "vision_model": "gpt-4o",
  "stt_model": "whisper-1",
  "temperature": 0.7,
  "max_tokens": 2048
}`,
  },
];

const methodColors: Record<string, string> = {
  GET: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400",
  POST: "bg-blue-500/15 text-blue-700 dark:text-blue-400",
  PUT: "bg-amber-500/15 text-amber-700 dark:text-amber-400",
  DELETE: "bg-red-500/15 text-red-700 dark:text-red-400",
};

function CodeBlock({ code, title }: { code: string; title?: string }) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="group relative rounded-lg border bg-muted/50">
      {title && (
        <div className="flex items-center justify-between border-b px-3 py-1.5">
          <span className="text-xs font-medium text-muted-foreground">
            {title}
          </span>
          <Button
            variant="ghost"
            size="sm"
            className="h-6 px-2 opacity-0 transition-opacity group-hover:opacity-100"
            onClick={handleCopy}
          >
            {copied ? (
              <Check className="h-3 w-3" />
            ) : (
              <Copy className="h-3 w-3" />
            )}
          </Button>
        </div>
      )}
      <pre className="overflow-x-auto p-3">
        <code className="text-xs leading-relaxed">{code}</code>
      </pre>
    </div>
  );
}

function EndpointCard({ endpoint }: { endpoint: Endpoint }) {
  const [expanded, setExpanded] = useState(false);
  const hasExamples = endpoint.request || endpoint.response;

  return (
    <Card
      className="cursor-pointer transition-colors hover:border-primary/30"
      onClick={() => hasExamples && setExpanded(!expanded)}
    >
      <CardHeader className="p-4">
        <div className="flex items-center gap-3">
          <span
            className={`shrink-0 rounded px-2 py-0.5 text-xs font-bold ${methodColors[endpoint.method]}`}
          >
            {endpoint.method}
          </span>
          <code className="font-mono text-sm">{endpoint.path}</code>
          <span className="hidden text-sm text-muted-foreground sm:inline">
            {endpoint.description}
          </span>
          {hasExamples && (
            <ChevronRight
              className={`ml-auto h-4 w-4 shrink-0 text-muted-foreground transition-transform ${expanded ? "rotate-90" : ""}`}
            />
          )}
        </div>
      </CardHeader>
      {expanded && hasExamples && (
        <CardContent className="space-y-3 px-4 pb-4 pt-0">
          {endpoint.request && (
            <CodeBlock code={endpoint.request} title="Request Body" />
          )}
          {endpoint.response && (
            <CodeBlock code={endpoint.response} title="Response" />
          )}
        </CardContent>
      )}
    </Card>
  );
}

export default function ApiDocsPage() {
  return (
    <div className="flex h-full flex-col">
      <div className="border-b p-8 pb-6">
        <div className="flex items-center gap-3">
          <BookOpen className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              API Documentation
            </h1>
            <p className="mt-1 text-muted-foreground">
              Interactive API reference and endpoint documentation.
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-8 pt-6">
        <Tabs defaultValue="reference" className="w-full">
          <TabsList>
            <TabsTrigger value="reference" className="gap-2">
              <Code2 className="h-4 w-4" />
              Endpoint Reference
            </TabsTrigger>
            <TabsTrigger value="swagger" className="gap-2">
              <ExternalLink className="h-4 w-4" />
              Swagger UI
            </TabsTrigger>
            <TabsTrigger value="guide" className="gap-2">
              <BookOpen className="h-4 w-4" />
              Quick Guide
            </TabsTrigger>
          </TabsList>

          <TabsContent value="reference" className="mt-6 space-y-6">
            <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
              <div className="space-y-3">
                {endpoints.map((ep) => (
                  <EndpointCard key={`${ep.method}-${ep.path}`} endpoint={ep} />
                ))}
              </div>

              <div className="space-y-4">
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Base URL</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <code className="rounded bg-muted px-2 py-1 text-xs">
                      http://localhost:8000
                    </code>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Authentication</CardTitle>
                    <CardDescription className="text-xs">
                      Not required for local development
                    </CardDescription>
                  </CardHeader>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Content Type</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <code className="rounded bg-muted px-2 py-1 text-xs">
                      application/json
                    </code>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Swagger Docs</CardTitle>
                    <CardDescription className="text-xs">
                      Interactive API explorer
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <a
                      href={SWAGGER_URL}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Button variant="outline" size="sm" className="w-full">
                        <ExternalLink className="mr-2 h-3 w-3" />
                        Open Swagger UI
                      </Button>
                    </a>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="swagger" className="mt-6">
            <Card className="overflow-hidden">
              <CardHeader className="border-b p-4">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">Swagger UI</CardTitle>
                  <a
                    href={SWAGGER_URL}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <Button variant="outline" size="sm">
                      <ExternalLink className="mr-2 h-3 w-3" />
                      Open in new tab
                    </Button>
                  </a>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <iframe
                  src={SWAGGER_URL}
                  className="h-[calc(100vh-280px)] w-full border-0"
                  title="Swagger UI"
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="guide" className="mt-6">
            <div className="mx-auto max-w-3xl space-y-8">
              <Card>
                <CardHeader>
                  <CardTitle>Getting Started</CardTitle>
                  <CardDescription>
                    How to interact with the AI Digital Human API.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 text-sm">
                  <p>
                    The API follows REST conventions. All request and response
                    bodies use JSON. The base URL for local development is{" "}
                    <code className="rounded bg-muted px-1.5 py-0.5 text-xs">
                      http://localhost:8000
                    </code>
                    .
                  </p>
                  <p>
                    The admin endpoints allow you to manage system prompts,
                    speaking styles, and model configuration. Changes take
                    effect immediately.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Managing System Prompts</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-sm">
                  <p>
                    System prompts define the AI&apos;s personality and
                    behavior. You can create multiple prompts and set one as the
                    default that the AI uses.
                  </p>
                  <CodeBlock
                    title="Create a prompt"
                    code={`curl -X POST http://localhost:8000/admin/prompts \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Support Agent",
    "content": "You are a helpful customer support agent..."
  }'`}
                  />
                  <CodeBlock
                    title="Set as default"
                    code={`curl -X PUT http://localhost:8000/admin/prompts/{id} \\
  -H "Content-Type: application/json" \\
  -d '{"is_default": true}'`}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Configuring Speaking Styles</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-sm">
                  <p>
                    Speaking styles control the tone, pace, and formality of the
                    AI&apos;s responses. Each style has a JSON configuration
                    object.
                  </p>
                  <CodeBlock
                    title="Create a style"
                    code={`curl -X POST http://localhost:8000/admin/styles \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Casual",
    "description": "Friendly and relaxed tone",
    "config": {
      "tone": "casual",
      "pace": "fast",
      "formality": "low"
    }
  }'`}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Model Configuration</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-sm">
                  <p>
                    The model configuration endpoint lets you switch between
                    different LLM, vision, and speech-to-text models, as well as
                    adjust generation parameters.
                  </p>
                  <CodeBlock
                    title="Update model config"
                    code={`curl -X PUT http://localhost:8000/admin/models \\
  -H "Content-Type: application/json" \\
  -d '{
    "llm_model": "gpt-4o",
    "vision_model": "gpt-4o",
    "stt_model": "whisper-1",
    "temperature": 0.7,
    "max_tokens": 2048
  }'`}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Error Handling</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-sm">
                  <p>
                    The API returns standard HTTP status codes. Error responses
                    include a detail message:
                  </p>
                  <CodeBlock
                    title="Error response"
                    code={`{
  "detail": "Prompt not found"
}`}
                  />
                  <div className="space-y-1">
                    <p className="font-medium">Common status codes:</p>
                    <ul className="list-inside list-disc space-y-1 text-muted-foreground">
                      <li>200 — Success</li>
                      <li>201 — Created</li>
                      <li>400 — Bad Request (validation error)</li>
                      <li>404 — Not Found</li>
                      <li>422 — Unprocessable Entity</li>
                      <li>500 — Internal Server Error</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
