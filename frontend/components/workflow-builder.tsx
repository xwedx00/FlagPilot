"use client";

/**
 * WorkflowBuilder - Visual DAG Editor
 * ====================================
 * Drag-and-drop workflow creation using ReactFlow.
 * Allows users to create custom agent workflows.
 */

import { useCallback, useState, useMemo, useRef } from "react";
import {
    ReactFlow,
    Background,
    Controls,
    MiniMap,
    Panel,
    useNodesState,
    useEdgesState,
    addEdge,
    type Node,
    type Edge,
    type Connection,
    Handle,
    Position,
    MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
    Save,
    Play,
    Plus,
    Trash2,
    Download,
    Upload,
    MoreVertical,
    Bot,
    Sparkles,
    Shield,
    TrendingUp,
    FileText,
    Search,
    Code,
    MessageSquare,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { AGENTS, type AgentId } from "@/stores/mission-store";

// Agent node types for the workflow
const AGENT_TYPES = [
    { id: "flagpilot", name: "FlagPilot", icon: Sparkles, color: "#6366f1" },
    { id: "contract-analyst", name: "Contract Analyst", icon: FileText, color: "#ef4444" },
    { id: "rate-optimizer", name: "Rate Optimizer", icon: TrendingUp, color: "#22c55e" },
    { id: "client-communicator", name: "Client Communicator", icon: MessageSquare, color: "#22c55e" },
    { id: "proposal-writer", name: "Proposal Writer", icon: FileText, color: "#22c55e" },
    { id: "researcher", name: "Researcher", icon: Search, color: "#6366f1" },
    { id: "code-generator", name: "Code Generator", icon: Code, color: "#6366f1" },
];

interface AgentNodeData {
    agentId: string;
    label: string;
    icon: string;
    color: string;
    description?: string;
}

// Custom Agent Node Component
function AgentNode({ data, selected }: { data: AgentNodeData; selected: boolean }) {
    const AgentIcon = AGENT_TYPES.find(a => a.id === data.agentId)?.icon || Bot;

    return (
        <div
            className={cn(
                "min-w-[160px] rounded-xl border-2 shadow-lg bg-card transition-all",
                selected ? "border-primary ring-2 ring-primary/20" : "border-border"
            )}
            style={{ borderColor: selected ? undefined : data.color }}
        >
            <Handle type="target" position={Position.Top} className="!bg-primary !w-3 !h-3" />

            <div className="p-3 flex items-center gap-2">
                <div
                    className="p-2 rounded-lg"
                    style={{ backgroundColor: `${data.color}20` }}
                >
                    <AgentIcon className="h-5 w-5" style={{ color: data.color }} />
                </div>
                <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold truncate">{data.label}</p>
                    {data.description && (
                        <p className="text-xs text-muted-foreground truncate">{data.description}</p>
                    )}
                </div>
            </div>

            <Handle type="source" position={Position.Bottom} className="!bg-primary !w-3 !h-3" />
        </div>
    );
}

const nodeTypes = {
    agent: AgentNode,
};

interface WorkflowBuilderProps {
    onSave?: (workflow: { nodes: Node[]; edges: Edge[]; name: string; description: string }) => void;
    onRun?: (workflow: { nodes: Node[]; edges: Edge[] }) => void;
    initialWorkflow?: { nodes: Node[]; edges: Edge[]; name?: string; description?: string };
    className?: string;
}

export function WorkflowBuilder({
    onSave,
    onRun,
    initialWorkflow,
    className
}: WorkflowBuilderProps) {
    // Initialize with default workflow or provided workflow
    const defaultNodes: Node[] = initialWorkflow?.nodes || [
        {
            id: "start",
            type: "agent",
            position: { x: 250, y: 50 },
            data: {
                agentId: "flagpilot",
                label: "FlagPilot",
                icon: "sparkles",
                color: "#6366f1",
                description: "Main orchestrator"
            },
        },
    ];

    const defaultEdges: Edge[] = initialWorkflow?.edges || [];

    const [nodes, setNodes, onNodesChange] = useNodesState(defaultNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(defaultEdges);
    const [workflowName, setWorkflowName] = useState(initialWorkflow?.name || "New Workflow");
    const [workflowDescription, setWorkflowDescription] = useState(initialWorkflow?.description || "");
    const [showSaveDialog, setShowSaveDialog] = useState(false);
    const [showAddAgentMenu, setShowAddAgentMenu] = useState(false);
    const nodeIdCounter = useRef(nodes.length);

    // Handle edge connections
    const onConnect = useCallback(
        (params: Connection) => {
            setEdges((eds) =>
                addEdge({
                    ...params,
                    markerEnd: { type: MarkerType.ArrowClosed },
                    style: { strokeWidth: 2 },
                    animated: true,
                }, eds)
            );
        },
        [setEdges]
    );

    // Add a new agent node
    const addAgent = useCallback((agentType: typeof AGENT_TYPES[0]) => {
        nodeIdCounter.current += 1;
        const newNode: Node = {
            id: `agent-${nodeIdCounter.current}`,
            type: "agent",
            position: {
                x: 150 + Math.random() * 200,
                y: 100 + nodes.length * 100
            },
            data: {
                agentId: agentType.id,
                label: agentType.name,
                icon: agentType.icon.name,
                color: agentType.color,
            },
        };
        setNodes((nds) => [...nds, newNode]);
        setShowAddAgentMenu(false);
    }, [nodes.length, setNodes]);

    // Delete selected nodes
    const deleteSelected = useCallback(() => {
        setNodes((nds) => nds.filter((n) => !n.selected));
        setEdges((eds) => eds.filter((e) => !e.selected));
    }, [setNodes, setEdges]);

    // Save workflow
    const handleSave = useCallback(() => {
        if (onSave) {
            onSave({
                nodes,
                edges,
                name: workflowName,
                description: workflowDescription,
            });
        }
        setShowSaveDialog(false);
    }, [nodes, edges, workflowName, workflowDescription, onSave]);

    // Run workflow
    const handleRun = useCallback(() => {
        if (onRun) {
            onRun({ nodes, edges });
        }
    }, [nodes, edges, onRun]);

    // Export workflow as JSON
    const exportWorkflow = useCallback(() => {
        const workflow = {
            name: workflowName,
            description: workflowDescription,
            nodes,
            edges,
            exportedAt: new Date().toISOString(),
        };
        const blob = new Blob([JSON.stringify(workflow, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${workflowName.replace(/\s+/g, "-").toLowerCase()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }, [nodes, edges, workflowName, workflowDescription]);

    // Import workflow from JSON
    const importWorkflow = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const workflow = JSON.parse(e.target?.result as string);
                if (workflow.nodes) setNodes(workflow.nodes);
                if (workflow.edges) setEdges(workflow.edges);
                if (workflow.name) setWorkflowName(workflow.name);
                if (workflow.description) setWorkflowDescription(workflow.description);
            } catch (err) {
                console.error("Failed to import workflow:", err);
            }
        };
        reader.readAsText(file);
    }, [setNodes, setEdges]);

    return (
        <div className={cn("w-full h-full min-h-[600px] rounded-xl overflow-hidden border bg-background", className)}>
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                nodeTypes={nodeTypes}
                fitView
                fitViewOptions={{ padding: 0.3 }}
                proOptions={{ hideAttribution: true }}
                className="bg-muted/20"
                deleteKeyCode={["Backspace", "Delete"]}
            >
                <Background gap={20} size={1} />
                <Controls className="!bg-background !border !shadow-lg" />
                <MiniMap
                    className="!bg-background !border"
                    nodeColor={(node) => node.data?.color || "#6366f1"}
                />

                {/* Toolbar Panel */}
                <Panel position="top-left" className="flex gap-2">
                    {/* Add Agent Button */}
                    <DropdownMenu open={showAddAgentMenu} onOpenChange={setShowAddAgentMenu}>
                        <DropdownMenuTrigger asChild>
                            <Button size="sm" className="gap-2">
                                <Plus className="h-4 w-4" />
                                Add Agent
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="start" className="w-56">
                            {AGENT_TYPES.map((agent) => (
                                <DropdownMenuItem
                                    key={agent.id}
                                    onClick={() => addAgent(agent)}
                                    className="gap-2"
                                >
                                    <agent.icon className="h-4 w-4" style={{ color: agent.color }} />
                                    {agent.name}
                                </DropdownMenuItem>
                            ))}
                        </DropdownMenuContent>
                    </DropdownMenu>

                    <Button size="sm" variant="outline" onClick={deleteSelected}>
                        <Trash2 className="h-4 w-4" />
                    </Button>
                </Panel>

                {/* Actions Panel */}
                <Panel position="top-right" className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={handleRun} className="gap-2">
                        <Play className="h-4 w-4" />
                        Run
                    </Button>

                    <Button size="sm" onClick={() => setShowSaveDialog(true)} className="gap-2">
                        <Save className="h-4 w-4" />
                        Save
                    </Button>

                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button size="sm" variant="ghost">
                                <MoreVertical className="h-4 w-4" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={exportWorkflow}>
                                <Download className="h-4 w-4 mr-2" />
                                Export JSON
                            </DropdownMenuItem>
                            <DropdownMenuItem asChild>
                                <label className="cursor-pointer flex items-center">
                                    <Upload className="h-4 w-4 mr-2" />
                                    Import JSON
                                    <input
                                        type="file"
                                        accept=".json"
                                        onChange={importWorkflow}
                                        className="hidden"
                                    />
                                </label>
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </Panel>

                {/* Workflow Info Panel */}
                <Panel position="bottom-left" className="bg-background/90 backdrop-blur-sm border rounded-lg p-3 max-w-xs">
                    <p className="font-semibold text-sm">{workflowName}</p>
                    <p className="text-xs text-muted-foreground">
                        {nodes.length} agents • {edges.length} connections
                    </p>
                </Panel>
            </ReactFlow>

            {/* Save Dialog */}
            <Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Save Workflow</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label htmlFor="name">Workflow Name</Label>
                            <Input
                                id="name"
                                value={workflowName}
                                onChange={(e) => setWorkflowName(e.target.value)}
                                placeholder="My Custom Workflow"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="description">Description</Label>
                            <Textarea
                                id="description"
                                value={workflowDescription}
                                onChange={(e) => setWorkflowDescription(e.target.value)}
                                placeholder="Describe what this workflow does..."
                                rows={3}
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setShowSaveDialog(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleSave}>
                            <Save className="h-4 w-4 mr-2" />
                            Save Workflow
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}

export default WorkflowBuilder;
