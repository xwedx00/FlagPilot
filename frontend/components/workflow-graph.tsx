"use client";

/**
 * WorkflowGraph - ReactFlow DAG Visualization
 * ============================================
 * Real-time visualization of agent workflow execution.
 * Shows node status, thinking states, and flow connections.
 */

import { useCallback, useMemo } from "react";
import {
    ReactFlow,
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState,
    type Node,
    type Edge,
    Handle,
    Position,
    MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { cn } from "@/lib/utils";
import { useMissionStore, AGENTS, type AgentId, type AgentStatus } from "@/stores/mission-store";

// Agent status colors
const STATUS_COLORS: Record<AgentStatus, { bg: string; border: string; pulse: boolean }> = {
    idle: { bg: "bg-muted", border: "border-muted-foreground/20", pulse: false },
    thinking: { bg: "bg-blue-500/20", border: "border-blue-500", pulse: true },
    working: { bg: "bg-amber-500/20", border: "border-amber-500", pulse: true },
    waiting: { bg: "bg-purple-500/20", border: "border-purple-500", pulse: false },
    done: { bg: "bg-green-500/20", border: "border-green-500", pulse: false },
    error: { bg: "bg-red-500/20", border: "border-red-500", pulse: false },
};

// Squad colors
const SQUAD_COLORS = {
    orchestrator: "#6366f1",
    risk: "#ef4444",
    growth: "#22c55e",
};

interface AgentNodeData {
    agentId: AgentId;
    status: AgentStatus;
    currentAction?: string;
    thought?: string;
}

// Custom Agent Node Component
function AgentNode({ data }: { data: AgentNodeData }) {
    const agent = AGENTS[data.agentId];
    const statusStyle = STATUS_COLORS[data.status];
    const squadColor = SQUAD_COLORS[agent?.squad as keyof typeof SQUAD_COLORS] || "#6366f1";

    if (!agent) {
        return (
            <div className="px-4 py-2 rounded-lg bg-muted border text-sm">
                Unknown Agent
            </div>
        );
    }

    return (
        <div
            className={cn(
                "relative min-w-[140px] rounded-xl border-2 shadow-lg transition-all duration-300",
                statusStyle.bg,
                statusStyle.border,
                statusStyle.pulse && "animate-pulse"
            )}
            style={{ borderColor: data.status !== "idle" ? undefined : squadColor }}
        >
            <Handle type="target" position={Position.Top} className="!bg-primary" />

            {/* Header */}
            <div className="px-3 py-2 flex items-center gap-2">
                <span className="text-lg">{agent.icon}</span>
                <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold truncate">{agent.name}</p>
                    <p className="text-xs text-muted-foreground truncate">{agent.role}</p>
                </div>
            </div>

            {/* Status Bar */}
            <div
                className="px-3 py-1.5 text-xs rounded-b-lg"
                style={{ backgroundColor: `${squadColor}15` }}
            >
                {data.status === "thinking" && (
                    <p className="text-blue-600 dark:text-blue-400 truncate">
                        💭 {data.thought || "Thinking..."}
                    </p>
                )}
                {data.status === "working" && (
                    <p className="text-amber-600 dark:text-amber-400 truncate">
                        ⚡ {data.currentAction || "Working..."}
                    </p>
                )}
                {data.status === "done" && (
                    <p className="text-green-600 dark:text-green-400">✓ Complete</p>
                )}
                {data.status === "error" && (
                    <p className="text-red-600 dark:text-red-400">✗ Error</p>
                )}
                {data.status === "waiting" && (
                    <p className="text-purple-600 dark:text-purple-400">⏳ Waiting</p>
                )}
                {data.status === "idle" && (
                    <p className="text-muted-foreground">Ready</p>
                )}
            </div>

            <Handle type="source" position={Position.Bottom} className="!bg-primary" />
        </div>
    );
}

const nodeTypes = {
    agent: AgentNode,
};

interface WorkflowGraphProps {
    className?: string;
}

export function WorkflowGraph({ className }: WorkflowGraphProps) {
    const { nodes: storeNodes, edges: storeEdges } = useMissionStore();

    // Convert store nodes to ReactFlow nodes
    const nodes = useMemo(() => {
        if (storeNodes.length === 0) {
            // Default layout when no workflow
            return [
                {
                    id: "flagpilot",
                    type: "agent",
                    position: { x: 300, y: 50 },
                    data: { agentId: "flagpilot" as AgentId, status: "idle" as AgentStatus },
                },
            ];
        }
        return storeNodes;
    }, [storeNodes]);

    const edges = useMemo(() => {
        return storeEdges.map((edge) => ({
            ...edge,
            markerEnd: { type: MarkerType.ArrowClosed },
            style: { strokeWidth: 2 },
        }));
    }, [storeEdges]);

    const [reactFlowNodes, setNodes, onNodesChange] = useNodesState(nodes);
    const [reactFlowEdges, setEdges, onEdgesChange] = useEdgesState(edges);

    // Update when store changes
    useMemo(() => {
        setNodes(nodes);
        setEdges(edges);
    }, [nodes, edges, setNodes, setEdges]);

    return (
        <div className={cn("w-full h-full min-h-[400px] rounded-xl overflow-hidden border bg-background", className)}>
            <ReactFlow
                nodes={reactFlowNodes}
                edges={reactFlowEdges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodeTypes={nodeTypes}
                fitView
                fitViewOptions={{ padding: 0.3 }}
                proOptions={{ hideAttribution: true }}
                className="bg-muted/20"
            >
                <Background gap={20} size={1} />
                <Controls className="!bg-background !border !shadow-lg" />
                <MiniMap
                    className="!bg-background !border"
                    nodeColor={(node) => {
                        const agentId = node.data?.agentId as AgentId;
                        const agent = AGENTS[agentId];
                        return SQUAD_COLORS[agent?.squad as keyof typeof SQUAD_COLORS] || "#6366f1";
                    }}
                />
            </ReactFlow>
        </div>
    );
}

// Export a simpler inline version for the chat
export function WorkflowMiniGraph() {
    const { nodes, edges, activeAgents } = useMissionStore();

    if (nodes.length === 0 && activeAgents.size === 0) {
        return null;
    }

    return (
        <div className="h-48 rounded-lg overflow-hidden border bg-muted/30">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                nodeTypes={nodeTypes}
                fitView
                fitViewOptions={{ padding: 0.5 }}
                proOptions={{ hideAttribution: true }}
                nodesDraggable={false}
                nodesConnectable={false}
                zoomOnScroll={false}
                panOnScroll={false}
                panOnDrag={false}
            >
                <Background gap={16} size={1} />
            </ReactFlow>
        </div>
    );
}
