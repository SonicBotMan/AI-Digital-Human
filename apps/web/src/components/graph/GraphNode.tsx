"use client";

import { memo, useState } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import {
  User,
  Star,
  Sparkles,
  MapPin,
  Zap,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import type { GraphNodeData, EntityType } from "@/lib/graph";
import { ENTITY_COLORS } from "@/lib/graph";

const ENTITY_ICONS: Record<
  EntityType,
  React.ComponentType<{ className?: string; style?: React.CSSProperties }>
> = {
  Person: User,
  Preference: Star,
  Trait: Sparkles,
  Location: MapPin,
  Activity: Zap,
};

const ENTITY_BADGES: Record<EntityType, string> = {
  Person: "P",
  Preference: "★",
  Trait: "✦",
  Location: "◎",
  Activity: "⚡",
};

function GraphNodeComponent({ data }: NodeProps) {
  const nodeData = data as GraphNodeData;
  const { label, entityType, attributes, isActive } = nodeData;
  const [expanded, setExpanded] = useState(false);
  const colors = ENTITY_COLORS[entityType];
  const Icon = ENTITY_ICONS[entityType];
  const hasAttributes = attributes && Object.keys(attributes).length > 0;

  return (
    <>
      <Handle
        type="target"
        position={Position.Top}
        id="top"
        style={{
          background: colors.border,
          width: 6,
          height: 6,
          border: "none",
        }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="bottom"
        style={{
          background: colors.border,
          width: 6,
          height: 6,
          border: "none",
        }}
      />
      <Handle
        type="target"
        position={Position.Left}
        id="left"
        style={{
          background: colors.border,
          width: 6,
          height: 6,
          border: "none",
        }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="right"
        style={{
          background: colors.border,
          width: 6,
          height: 6,
          border: "none",
        }}
      />

      <div
        style={{
          borderColor: colors.border,
          backgroundColor: isActive ? colors.bg : "hsl(var(--card))",
          boxShadow: isActive
            ? `0 0 12px ${colors.glow}, 0 0 32px ${colors.glow}, inset 0 0 12px ${colors.bg}`
            : `0 1px 3px hsla(var(--foreground) / 0.06)`,
          animation: isActive
            ? "graph-node-pulse 1.5s ease-in-out infinite, graph-glow-breathe 2s ease-in-out infinite"
            : "none",
        }}
        className={[
          "min-w-[140px] max-w-[240px] rounded-xl border-2 backdrop-blur-sm",
          "transition-all duration-300 ease-out cursor-pointer select-none",
          "hover:brightness-110",
        ].join(" ")}
        onClick={() => hasAttributes && setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2.5 px-3.5 py-2.5">
          <div
            className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md"
            style={{ backgroundColor: colors.bg, color: colors.text }}
          >
            <Icon className="h-3.5 w-3.5" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="truncate text-xs font-semibold leading-tight text-foreground">
              {label}
            </div>
            <div
              className="mt-0.5 text-[10px] font-medium uppercase tracking-wider opacity-60"
              style={{ color: colors.text }}
            >
              {entityType}
            </div>
          </div>
          {hasAttributes && (
            <div className="shrink-0 text-muted-foreground">
              {expanded ? (
                <ChevronDown className="h-3 w-3" />
              ) : (
                <ChevronRight className="h-3 w-3" />
              )}
            </div>
          )}
        </div>

        {expanded && hasAttributes && (
          <div
            className="border-t px-3.5 py-2 space-y-1"
            style={{ borderColor: colors.bg }}
          >
            {Object.entries(attributes!).map(([key, value]) => (
              <div
                key={key}
                className="flex items-start gap-1.5 text-[10px] leading-snug"
              >
                <span className="shrink-0 text-muted-foreground">{key}</span>
                <span className="text-muted-foreground">·</span>
                <span
                  className="text-foreground"
                  style={{ color: colors.text }}
                >
                  {value}
                </span>
              </div>
            ))}
          </div>
        )}

        {isActive && (
          <div
            className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full text-[8px] font-bold"
            style={{
              backgroundColor: colors.border,
              color: "hsl(var(--card))",
            }}
          >
            {ENTITY_BADGES[entityType]}
          </div>
        )}
      </div>
    </>
  );
}

export const GraphNodeComponentMemo = memo(GraphNodeComponent);
