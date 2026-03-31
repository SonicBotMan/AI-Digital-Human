"use client";

import { useMemo, useEffect, useCallback, useState } from "react";
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  useReactFlow,
  BackgroundVariant,
  type NodeTypes,
  type EdgeTypes,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { GraphNodeComponentMemo } from "./GraphNode";
import { GraphEdgeComponentMemo } from "./GraphEdge";
import { ThoughtChain, type ThoughtChainState } from "./ThoughtChain";
import type {
  GraphNodeType,
  GraphEdgeType,
  GraphNodeData,
  GraphEdgeData,
} from "@/lib/graph";
import { ENTITY_COLORS } from "@/lib/graph";

const nodeTypes: NodeTypes = {
  graphNode: GraphNodeComponentMemo,
};

const edgeTypes: EdgeTypes = {
  graphEdge: GraphEdgeComponentMemo,
};

interface KnowledgeGraphProps {
  initialNodes: GraphNodeType[];
  initialEdges: GraphEdgeType[];
}

const defaultEdgeOptions = {
  type: "graphEdge" as const,
  animated: false,
};

function KnowledgeGraphInner({
  initialNodes,
  initialEdges,
}: KnowledgeGraphProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const { fitView } = useReactFlow();

  const [thoughtState, setThoughtState] = useState<ThoughtChainState>({
    phase: "idle",
    activeNodeId: null,
    activeEdgeIds: [],
    visitedNodeIds: [],
  });

  const stableNodeIds = useMemo(
    () => initialNodes.map((n) => n.id),
    [initialNodes],
  );

  const stableEdgeConnections = useMemo(
    () =>
      initialEdges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
      })),
    [initialEdges],
  );

  const handleThoughtStateChange = useCallback((state: ThoughtChainState) => {
    setThoughtState(state);
  }, []);

  useEffect(() => {
    const activeId = thoughtState.activeNodeId;
    const visited = thoughtState.visitedNodeIds;

    setNodes((nds) =>
      nds.map((node) => {
        const data = node.data as GraphNodeData;
        const isActive = node.id === activeId;
        const isVisited = visited.includes(node.id) && !isActive;
        return {
          ...node,
          data: {
            ...data,
            isActive,
            expanded:
              isVisited &&
              !!data.attributes &&
              Object.keys(data.attributes).length > 0,
          },
        };
      }),
    );
  }, [thoughtState.activeNodeId, thoughtState.visitedNodeIds, setNodes]);

  useEffect(() => {
    const activeIds = thoughtState.activeEdgeIds;
    setEdges((eds) =>
      eds.map((edge) => {
        const prev = edge.data as GraphEdgeData;
        const next: GraphEdgeData = {
          label: prev.label,
          relationshipType: prev.relationshipType,
          isActive: activeIds.includes(edge.id),
        };
        return { ...edge, data: next };
      }),
    );
  }, [thoughtState.activeEdgeIds, setEdges]);

  useEffect(() => {
    if (initialNodes.length > 0) {
      const timer = setTimeout(() => {
        fitView({ padding: 0.25, duration: 600 });
      }, 150);
      return () => clearTimeout(timer);
    }
  }, [initialNodes, fitView]);

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        defaultEdgeOptions={defaultEdgeOptions}
        fitView
        fitViewOptions={{ padding: 0.25 }}
        minZoom={0.2}
        maxZoom={2}
        proOptions={{ hideAttribution: true }}
        style={{ backgroundColor: "hsl(var(--background))" }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="hsl(var(--border))"
        />
        <Controls
          className="!rounded-lg !border !bg-card/90 !shadow-lg !backdrop-blur-md"
          showInteractive={false}
        />
        <MiniMap
          nodeColor={(node) => {
            const data = node.data as GraphNodeData;
            return (
              ENTITY_COLORS[data.entityType]?.border ??
              "hsl(var(--muted-foreground))"
            );
          }}
          maskColor="hsla(var(--background) / 0.8)"
          className="!rounded-lg !border !bg-card/90 !shadow-lg !backdrop-blur-md"
          pannable
          zoomable
        />
        <ThoughtChain
          nodeIds={stableNodeIds}
          edgeConnections={stableEdgeConnections}
          onStateChange={handleThoughtStateChange}
          enabled={initialNodes.length > 0}
        />
      </ReactFlow>
    </div>
  );
}

export function KnowledgeGraph(props: KnowledgeGraphProps) {
  return (
    <ReactFlowProvider>
      <KnowledgeGraphInner {...props} />
    </ReactFlowProvider>
  );
}
