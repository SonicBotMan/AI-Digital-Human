"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { api } from "@/lib/api";
import {
  type GraphData,
  type GraphNodeType,
  type GraphEdgeType,
  transformToReactFlow,
} from "@/lib/graph";

interface UseGraphDataResult {
  nodes: GraphNodeType[];
  edges: GraphEdgeType[];
  metadata: Record<string, unknown>;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useGraphData(userId: string): UseGraphDataResult {
  const [nodes, setNodes] = useState<GraphNodeType[]>([]);
  const [edges, setEdges] = useState<GraphEdgeType[]>([]);
  const [metadata, setMetadata] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const cacheRef = useRef<
    Map<
      string,
      {
        nodes: GraphNodeType[];
        edges: GraphEdgeType[];
        metadata: Record<string, unknown>;
      }
    >
  >(new Map());

  const fetchData = useCallback(async () => {
    const cached = cacheRef.current.get(userId);
    if (cached) {
      setNodes(cached.nodes);
      setEdges(cached.edges);
      setMetadata(cached.metadata);
      setLoading(false);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await api.get<GraphData>(`/knowledge/${userId}/graph`);
      const transformed = transformToReactFlow(result);
      cacheRef.current.set(userId, {
        nodes: transformed.nodes,
        edges: transformed.edges,
        metadata: result.metadata,
      });
      setNodes(transformed.nodes);
      setEdges(transformed.edges);
      setMetadata(result.metadata);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to fetch graph data",
      );
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { nodes, edges, metadata, loading, error, refetch: fetchData };
}
