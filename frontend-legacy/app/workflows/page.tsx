"use client";

/**
 * Workflows Page
 * ==============
 * Manage and create custom agent workflows.
 */

import { useState, useEffect } from "react";
import { WorkflowBuilder } from "@/components/workflow-builder";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {
    Plus,
    Workflow as WorkflowIcon,
    Trash2,
    Edit,
    Play,
    Search,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
    listWorkflows,
    createWorkflow,
    deleteWorkflow,
    type Workflow,
    type WorkflowCreate,
} from "@/lib/api";

export default function WorkflowsPage() {
    const [workflows, setWorkflows] = useState<Workflow[]>([]);
    const [loading, setLoading] = useState(true);
    const [showBuilder, setShowBuilder] = useState(false);
    const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
    const [searchQuery, setSearchQuery] = useState("");

    // Fetch workflows on mount
    useEffect(() => {
        fetchWorkflows();
    }, []);

    const fetchWorkflows = async () => {
        try {
            const data = await listWorkflows();
            setWorkflows(data);
        } catch (error) {
            console.error("Failed to fetch workflows:", error);
            // Load from localStorage as fallback
            const stored = localStorage.getItem("flagpilot_workflows");
            if (stored) {
                setWorkflows(JSON.parse(stored));
            }
        } finally {
            setLoading(false);
        }
    };

    const handleSaveWorkflow = async (workflow: {
        nodes: unknown[];
        edges: unknown[];
        name: string;
        description: string;
    }) => {
        try {
            const newWorkflow = await createWorkflow({
                name: workflow.name,
                description: workflow.description,
                definition: {
                    nodes: workflow.nodes as WorkflowCreate["definition"]["nodes"],
                    edges: workflow.edges as WorkflowCreate["definition"]["edges"],
                },
            });
            setWorkflows((prev) => [...prev, newWorkflow]);
            setShowBuilder(false);
        } catch (error) {
            console.error("Failed to save workflow:", error);
            // Save to localStorage as fallback
            const localWorkflow = {
                id: `local-${Date.now()}`,
                name: workflow.name,
                description: workflow.description,
                definition: { nodes: workflow.nodes, edges: workflow.edges },
                is_public: false,
                tags: null,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
            };
            setWorkflows((prev) => [...prev, localWorkflow as Workflow]);
            localStorage.setItem(
                "flagpilot_workflows",
                JSON.stringify([...workflows, localWorkflow])
            );
            setShowBuilder(false);
        }
    };

    const handleDeleteWorkflow = async (workflowId: string) => {
        try {
            await deleteWorkflow(workflowId);
            setWorkflows((prev) => prev.filter((w) => w.id !== workflowId));
        } catch (error) {
            console.error("Failed to delete workflow:", error);
            // Delete from localStorage as fallback
            const updated = workflows.filter((w) => w.id !== workflowId);
            setWorkflows(updated);
            localStorage.setItem("flagpilot_workflows", JSON.stringify(updated));
        }
    };

    const handleRunWorkflow = (workflow: Workflow) => {
        // Navigate to Mission page with workflow ID
        window.location.href = `/mission?workflowId=${workflow.id}`;
    };

    const filteredWorkflows = workflows.filter((w) =>
        w.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    if (showBuilder) {
        return (
            <div className="h-screen flex flex-col">
                <div className="p-4 border-b flex items-center justify-between">
                    <h1 className="text-xl font-bold">
                        {selectedWorkflow ? `Edit: ${selectedWorkflow.name}` : "New Workflow"}
                    </h1>
                    <Button variant="outline" onClick={() => setShowBuilder(false)}>
                        Back to List
                    </Button>
                </div>
                <div className="flex-1">
                    <WorkflowBuilder
                        onSave={handleSaveWorkflow}
                        onRun={(wf) => console.log("Run preview:", wf)}
                        initialWorkflow={
                            selectedWorkflow
                                ? {
                                    nodes: selectedWorkflow.definition.nodes as any,
                                    edges: selectedWorkflow.definition.edges as any,
                                    name: selectedWorkflow.name,
                                    description: selectedWorkflow.description || "",
                                }
                                : undefined
                        }
                    />
                </div>
            </div>
        );
    }

    return (
        <div className="container mx-auto p-6 max-w-6xl">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold">Custom Workflows</h1>
                    <p className="text-muted-foreground">
                        Create and manage your agent workflows
                    </p>
                </div>
                <Button onClick={() => { setSelectedWorkflow(null); setShowBuilder(true); }}>
                    <Plus className="h-4 w-4 mr-2" />
                    New Workflow
                </Button>
            </div>

            {/* Search */}
            <div className="relative mb-6">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                    placeholder="Search workflows..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                />
            </div>

            {/* Workflows Grid */}
            {loading ? (
                <div className="text-center py-12 text-muted-foreground">
                    Loading workflows...
                </div>
            ) : filteredWorkflows.length === 0 ? (
                <Card className="border-dashed">
                    <CardContent className="flex flex-col items-center justify-center py-12">
                        <WorkflowIcon className="h-12 w-12 text-muted-foreground mb-4" />
                        <h3 className="font-semibold mb-2">No workflows yet</h3>
                        <p className="text-muted-foreground text-sm mb-4">
                            Create your first custom agent workflow
                        </p>
                        <Button onClick={() => setShowBuilder(true)}>
                            <Plus className="h-4 w-4 mr-2" />
                            Create Workflow
                        </Button>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {filteredWorkflows.map((workflow) => (
                        <Card key={workflow.id} className="group hover:border-primary/50 transition-colors">
                            <CardHeader className="pb-3">
                                <div className="flex items-start justify-between">
                                    <div>
                                        <CardTitle className="text-lg">{workflow.name}</CardTitle>
                                        <CardDescription className="line-clamp-2">
                                            {workflow.description || "No description"}
                                        </CardDescription>
                                    </div>
                                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <Button
                                            size="icon"
                                            variant="ghost"
                                            onClick={() => { setSelectedWorkflow(workflow); setShowBuilder(true); }}
                                        >
                                            <Edit className="h-4 w-4" />
                                        </Button>
                                        <Button
                                            size="icon"
                                            variant="ghost"
                                            onClick={() => handleDeleteWorkflow(workflow.id)}
                                        >
                                            <Trash2 className="h-4 w-4 text-destructive" />
                                        </Button>
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <div className="flex items-center justify-between text-sm text-muted-foreground">
                                    <span>
                                        {workflow.definition.nodes?.length || 0} agents •{" "}
                                        {workflow.definition.edges?.length || 0} connections
                                    </span>
                                    <Button
                                        size="sm"
                                        onClick={() => handleRunWorkflow(workflow)}
                                    >
                                        <Play className="h-3 w-3 mr-1" />
                                        Run
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
