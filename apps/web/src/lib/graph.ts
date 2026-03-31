import type { Node, Edge } from "@xyflow/react";

export type EntityType =
  | "Person"
  | "Preference"
  | "Trait"
  | "Location"
  | "Activity";
export type RelationshipType =
  | "likes"
  | "has_trait"
  | "knows"
  | "visited"
  | "participates_in"
  | "related_to";

export interface ApiGraphNode {
  id: string;
  label: string;
  type: EntityType;
  attributes?: Record<string, string>;
}

export interface ApiGraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  type: RelationshipType;
}

export interface GraphData {
  nodes: ApiGraphNode[];
  edges: ApiGraphEdge[];
  metadata: Record<string, unknown>;
}

export interface GraphNodeData extends Record<string, unknown> {
  label: string;
  entityType: EntityType;
  attributes?: Record<string, string>;
  isActive?: boolean;
  expanded?: boolean;
}

export interface GraphEdgeData extends Record<string, unknown> {
  label: string;
  relationshipType: RelationshipType;
  isActive?: boolean;
}

export type GraphNodeType = Node<GraphNodeData, "graphNode">;
export type GraphEdgeType = Edge<GraphEdgeData, "graphEdge">;

export const ENTITY_COLORS: Record<
  EntityType,
  { border: string; bg: string; glow: string; text: string }
> = {
  Person: {
    border: "hsl(var(--graph-person))",
    bg: "hsla(var(--graph-person) / 0.08)",
    glow: "hsla(var(--graph-person) / 0.4)",
    text: "hsl(var(--graph-person))",
  },
  Preference: {
    border: "hsl(var(--graph-preference))",
    bg: "hsla(var(--graph-preference) / 0.08)",
    glow: "hsla(var(--graph-preference) / 0.4)",
    text: "hsl(var(--graph-preference))",
  },
  Trait: {
    border: "hsl(var(--graph-trait))",
    bg: "hsla(var(--graph-trait) / 0.08)",
    glow: "hsla(var(--graph-trait) / 0.4)",
    text: "hsl(var(--graph-trait))",
  },
  Location: {
    border: "hsl(var(--graph-location))",
    bg: "hsla(var(--graph-location) / 0.08)",
    glow: "hsla(var(--graph-location) / 0.4)",
    text: "hsl(var(--graph-location))",
  },
  Activity: {
    border: "hsl(var(--graph-activity))",
    bg: "hsla(var(--graph-activity) / 0.08)",
    glow: "hsla(var(--graph-activity) / 0.4)",
    text: "hsl(var(--graph-activity))",
  },
};

export const RELATIONSHIP_COLORS: Record<string, string> = {
  likes: "hsl(var(--graph-preference))",
  has_trait: "hsl(var(--graph-trait))",
  knows: "hsl(var(--graph-person))",
  visited: "hsl(var(--graph-location))",
  participates_in: "hsl(var(--graph-activity))",
  related_to: "hsl(var(--muted-foreground))",
};

export function computeForceLayout(
  nodeIds: string[],
  edges: Array<{ source: string; target: string }>,
  width = 900,
  height = 700,
  iterations = 200,
): Map<string, { x: number; y: number }> {
  const positions = new Map<
    string,
    { x: number; y: number; vx: number; vy: number }
  >();
  const cx = width / 2;
  const cy = height / 2;

  const radius = Math.min(width, height) * 0.35;
  nodeIds.forEach((id, i) => {
    const angle = (2 * Math.PI * i) / Math.max(nodeIds.length, 1);
    positions.set(id, {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
      vx: 0,
      vy: 0,
    });
  });

  const repulsion = 8000;
  const attraction = 0.008;
  const damping = 0.85;
  const centerPull = 0.009;

  for (let iter = 0; iter < iterations; iter++) {
    const alpha = 1 - iter / iterations;
    const arr = Array.from(positions.values());

    for (let i = 0; i < arr.length; i++) {
      for (let j = i + 1; j < arr.length; j++) {
        const a = arr[i];
        const b = arr[j];
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
        const force = (repulsion * alpha) / (dist * dist);
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        a.vx -= fx;
        a.vy -= fy;
        b.vx += fx;
        b.vy += fy;
      }
    }

    for (const edge of edges) {
      const s = positions.get(edge.source);
      const t = positions.get(edge.target);
      if (!s || !t) continue;
      const dx = t.x - s.x;
      const dy = t.y - s.y;
      const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
      const force = dist * attraction * alpha;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      s.vx += fx;
      s.vy += fy;
      t.vx -= fx;
      t.vy -= fy;
    }

    for (const node of arr) {
      node.vx += (cx - node.x) * centerPull * alpha;
      node.vy += (cy - node.y) * centerPull * alpha;
      node.vx *= damping;
      node.vy *= damping;
      node.x += node.vx;
      node.y += node.vy;
    }
  }

  const result = new Map<string, { x: number; y: number }>();
  positions.forEach((pos, id) => {
    result.set(id, { x: pos.x, y: pos.y });
  });
  return result;
}

export function transformToReactFlow(data: GraphData): {
  nodes: GraphNodeType[];
  edges: GraphEdgeType[];
} {
  const layout = computeForceLayout(
    data.nodes.map((n) => n.id),
    data.edges.map((e) => ({ source: e.source, target: e.target })),
  );

  const nodes: GraphNodeType[] = data.nodes.map((node) => ({
    id: node.id,
    type: "graphNode" as const,
    position: layout.get(node.id) ?? { x: 0, y: 0 },
    data: {
      label: node.label,
      entityType: node.type,
      attributes: node.attributes,
      isActive: false,
      expanded: false,
    },
  }));

  const edges: GraphEdgeType[] = data.edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    type: "graphEdge" as const,
    data: {
      label: edge.label,
      relationshipType: edge.type,
      isActive: false,
    },
  }));

  return { nodes, edges };
}
