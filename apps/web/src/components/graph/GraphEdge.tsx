"use client";

import { memo } from "react";
import {
  BaseEdge,
  EdgeLabelRenderer,
  getSmoothStepPath,
  type EdgeProps,
} from "@xyflow/react";
import type { GraphEdgeData } from "@/lib/graph";
import { RELATIONSHIP_COLORS } from "@/lib/graph";

const FALLBACK_COLOR = "hsl(var(--muted-foreground))";

function GraphEdgeComponent(props: EdgeProps) {
  const {
    id,
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    data,
    markerEnd,
  } = props;
  const edgeData = data as GraphEdgeData;
  const isActive = edgeData?.isActive ?? false;
  const relType = edgeData?.relationshipType ?? "related_to";
  const color = RELATIONSHIP_COLORS[relType] ?? FALLBACK_COLOR;

  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    borderRadius: 12,
  });

  return (
    <>
      {isActive && (
        <path
          d={edgePath}
          fill="none"
          stroke={color}
          strokeWidth={8}
          strokeOpacity={0.12}
          style={{ filter: `blur(4px)` }}
        />
      )}

      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          stroke: color,
          strokeWidth: isActive ? 2.5 : 1.5,
          opacity: isActive ? 1 : 0.5,
          transition: "stroke-width 0.3s ease, opacity 0.3s ease",
        }}
      />

      {isActive && (
        <path
          d={edgePath}
          fill="none"
          stroke={color}
          strokeWidth={2.5}
          strokeDasharray="4 8"
          strokeOpacity={0.9}
          style={{
            animation: "graph-edge-flow 0.6s linear infinite",
          }}
        />
      )}

      {edgeData?.label && (
        <EdgeLabelRenderer>
          <div
            className="pointer-events-auto nodrag nopan"
            style={{
              position: "absolute",
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              fontSize: 9,
              fontWeight: 600,
              letterSpacing: "0.03em",
              color: isActive ? color : "hsl(var(--muted-foreground))",
              backgroundColor: isActive
                ? `color-mix(in srgb, ${color} 12%, hsl(var(--card)))`
                : "hsl(var(--card))",
              padding: "2px 6px",
              borderRadius: 4,
              border: `1px solid ${isActive ? color : "hsl(var(--border))"}`,
              transition: "all 0.3s ease",
              whiteSpace: "nowrap",
            }}
          >
            {edgeData.label}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}

export const GraphEdgeComponentMemo = memo(GraphEdgeComponent);
