"use client";

import { Brain, RefreshCw, Network } from "lucide-react";
import { useGraphData } from "@/hooks/useGraphData";
import { KnowledgeGraph } from "@/components/graph/KnowledgeGraph";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/components/layout/AuthProvider";

function LoadingState() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-6">
      <div className="relative">
        <div className="h-20 w-20 rounded-2xl bg-primary/10 flex items-center justify-center">
          <Brain className="h-10 w-10 text-primary animate-pulse" />
        </div>
        <div
          className="absolute inset-0 rounded-2xl"
          style={{
            boxShadow: "0 0 30px hsla(var(--primary) / 0.2)",
            animation: "graph-glow-breathe 2s ease-in-out infinite",
          }}
        />
      </div>
      <div className="text-center space-y-1">
        <p className="text-sm font-medium text-foreground">
          Loading knowledge graph
        </p>
        <p className="text-xs text-muted-foreground">
          Mapping entities and relationships...
        </p>
      </div>
      <div className="flex gap-1">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="h-1.5 w-1.5 rounded-full bg-primary"
            style={{
              animation: "graph-glow-breathe 1.2s ease-in-out infinite",
              animationDelay: `${i * 0.2}s`,
            }}
          />
        ))}
      </div>
    </div>
  );
}

function EmptyState({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-6 p-8">
      <div className="h-20 w-20 rounded-2xl bg-muted flex items-center justify-center">
        <Network className="h-10 w-10 text-muted-foreground" />
      </div>
      <div className="text-center space-y-2 max-w-sm">
        <p className="text-lg font-semibold text-foreground">
          No graph data yet
        </p>
        <p className="text-sm text-muted-foreground">
          Start interacting with the AI to build your knowledge graph. Entities
          and relationships will appear here as they are discovered.
        </p>
      </div>
      <Button variant="outline" size="sm" onClick={onRetry}>
        <RefreshCw className="mr-2 h-3.5 w-3.5" />
        Check for updates
      </Button>
    </div>
  );
}

function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-6 p-8">
      <div className="h-20 w-20 rounded-2xl bg-destructive/10 flex items-center justify-center">
        <Brain className="h-10 w-10 text-destructive" />
      </div>
      <div className="text-center space-y-2 max-w-sm">
        <p className="text-lg font-semibold text-foreground">
          Failed to load graph
        </p>
        <p className="text-sm text-muted-foreground">{message}</p>
      </div>
      <Button variant="outline" size="sm" onClick={onRetry}>
        <RefreshCw className="mr-2 h-3.5 w-3.5" />
        Try again
      </Button>
    </div>
  );
}

export default function KnowledgePage() {
  const { user, loading: authLoading } = useAuth();
  const { nodes, edges, loading, error, refetch } =
    useGraphData(user?.id ?? "");

  if (authLoading) {
    return (
      <div className="flex h-full">
        <LoadingState />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-6 p-8">
        <div className="h-20 w-20 rounded-2xl bg-muted flex items-center justify-center">
          <Brain className="h-10 w-10 text-muted-foreground" />
        </div>
        <div className="text-center space-y-2 max-w-sm">
          <p className="text-lg font-semibold text-foreground">
            Please log in
          </p>
          <p className="text-sm text-muted-foreground">
            You need to be logged in to view your knowledge graph.
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex h-full">
        <LoadingState />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full">
        <ErrorState message={error} onRetry={refetch} />
      </div>
    );
  }

  if (nodes.length === 0) {
    return (
      <div className="flex h-full">
        <EmptyState onRetry={refetch} />
      </div>
    );
  }

  return (
    <div className="h-full">
      <KnowledgeGraph initialNodes={nodes} initialEdges={edges} />
    </div>
  );
}
