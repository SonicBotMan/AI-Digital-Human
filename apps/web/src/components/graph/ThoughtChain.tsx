"use client";

import { useEffect, useRef, useCallback } from "react";
import { Panel } from "@xyflow/react";
import { Brain, Zap, GitBranch, Pause } from "lucide-react";

export type ThoughtPhase = "idle" | "input" | "propagate" | "settle";

export interface ThoughtChainState {
  phase: ThoughtPhase;
  activeNodeId: string | null;
  activeEdgeIds: string[];
  visitedNodeIds: string[];
}

interface ThoughtChainProps {
  nodeIds: string[];
  edgeConnections: Array<{ id: string; source: string; target: string }>;
  onStateChange: (state: ThoughtChainState) => void;
  enabled?: boolean;
}

const PHASE_CONFIG = {
  idle: { duration: 2500, label: "Observing" },
  input: { duration: 900, label: "Receiving" },
  propagate: { duration: 450, label: "Reasoning" },
  settle: { duration: 1100, label: "Settling" },
} as const;

const PHASE_ICONS: Record<
  ThoughtPhase,
  React.ComponentType<{ className?: string }>
> = {
  idle: Pause,
  input: Zap,
  propagate: GitBranch,
  settle: Brain,
};

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function getConnectedEdges(
  nodeId: string,
  edges: Array<{ id: string; source: string; target: string }>,
) {
  return edges.filter((e) => e.source === nodeId || e.target === nodeId);
}

export function ThoughtChain({
  nodeIds,
  edgeConnections,
  onStateChange,
  enabled = true,
}: ThoughtChainProps) {
  const stateRef = useRef<ThoughtChainState>({
    phase: "idle",
    activeNodeId: null,
    activeEdgeIds: [],
    visitedNodeIds: [],
  });
  const phaseRef = useRef<ThoughtPhase>("idle");

  const emit = useCallback(
    (partial: Partial<ThoughtChainState>) => {
      const next = { ...stateRef.current, ...partial };
      stateRef.current = next;
      phaseRef.current = next.phase;
      onStateChange(next);
    },
    [onStateChange],
  );

  useEffect(() => {
    if (!enabled || nodeIds.length === 0) return;

    let cancelled = false;
    let cycleIndex = 0;

    const runCycle = async () => {
      while (!cancelled) {
        const sourceIdx = cycleIndex % nodeIds.length;
        cycleIndex++;
        const sourceId = nodeIds[sourceIdx];

        emit({
          phase: "idle",
          activeNodeId: null,
          activeEdgeIds: [],
          visitedNodeIds: [],
        });
        await sleep(PHASE_CONFIG.idle.duration);
        if (cancelled) break;

        emit({
          phase: "input",
          activeNodeId: sourceId,
          activeEdgeIds: [],
          visitedNodeIds: [sourceId],
        });
        await sleep(PHASE_CONFIG.input.duration);
        if (cancelled) break;

        const connected = getConnectedEdges(sourceId, edgeConnections);
        emit({
          phase: "propagate",
          activeNodeId: sourceId,
          activeEdgeIds: connected.map((e) => e.id),
          visitedNodeIds: [sourceId],
        });

        const visitedIds: string[] = [sourceId];
        for (const edge of connected) {
          if (cancelled) break;
          const neighborId =
            edge.source === sourceId ? edge.target : edge.source;
          if (!visitedIds.includes(neighborId)) {
            visitedIds.push(neighborId);
            emit({
              phase: "propagate",
              activeNodeId: neighborId,
              activeEdgeIds: connected.map((e) => e.id),
              visitedNodeIds: [...visitedIds],
            });
          }
          await sleep(PHASE_CONFIG.propagate.duration);
        }
        if (cancelled) break;

        emit({
          phase: "settle",
          activeNodeId: null,
          activeEdgeIds: [],
          visitedNodeIds: visitedIds,
        });
        await sleep(PHASE_CONFIG.settle.duration);
      }
    };

    runCycle();

    return () => {
      cancelled = true;
    };
  }, [nodeIds, edgeConnections, enabled, emit]);

  const CurrentIcon = PHASE_ICONS[phaseRef.current];
  const phaseLabel = PHASE_CONFIG[phaseRef.current].label;

  return (
    <Panel position="top-right" className="!m-3">
      <div className="flex items-center gap-2.5 rounded-lg border bg-card/90 px-3 py-2 backdrop-blur-md shadow-lg">
        <div
          className="flex h-6 w-6 items-center justify-center rounded-md bg-primary/10"
          style={{
            animation:
              phaseRef.current !== "idle"
                ? "graph-glow-breathe 1s ease-in-out infinite"
                : "none",
          }}
        >
          <CurrentIcon className="h-3.5 w-3.5 text-primary" />
        </div>
        <div className="flex flex-col">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-primary">
            Thought Chain
          </span>
          <span className="text-[10px] text-muted-foreground">
            {phaseLabel}
          </span>
        </div>
        {phaseRef.current !== "idle" && (
          <div className="ml-1 h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
        )}
      </div>
    </Panel>
  );
}
