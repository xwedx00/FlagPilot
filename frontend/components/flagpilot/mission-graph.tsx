'use client';

import * as React from 'react';
import { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Position,
  Handle,
  NodeProps,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { cn } from '@/lib/utils';
import { AgentAvatar, getAgentDisplayName, type AgentStatus } from './agent-avatar';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';

export type NodeStatus = 'planning' | 'working' | 'done' | 'blocked' | 'pending';

export interface WorkflowNode {
  id: string;
  agentId: string;
  task: string;
  status: NodeStatus;
  dependencies?: string[];
  result?: string;
  memory?: Record<string, unknown>;
}

export interface WorkflowData {
  nodes: WorkflowNode[];
}

interface MissionGraphProps {
  workflowData: WorkflowData;
  onNodeClick?: (node: WorkflowNode) => void;
  className?: string;
}

const STATUS_BORDER_CLASSES: Record<NodeStatus, string> = {
  planning: 'border-blue-500',
  working: 'border-amber-500 animate-pulse',
  done: 'border-emerald-500',
  blocked: 'border-rose-500',
  pending: 'border-zinc-600',
};

const STATUS_TO_AGENT_STATUS: Record<NodeStatus, AgentStatus> = {
  planning: 'thinking',
  working: 'working',
  done: 'complete',
  blocked: 'error',
  pending: 'idle',
};

/**
 * Custom Agent Node for React Flow
 */
function AgentNodeComponent({ data }: NodeProps<WorkflowNode>) {
  const agentName = getAgentDisplayName(data.agentId);
  const status = data.status as NodeStatus;
  
  return (
    <>
      <Handle type="target" position={Position.Top} className="!bg-zinc-600" />
      
      <div
        className={cn(
          'bg-zinc-900/90 backdrop-blur-sm rounded-md p-3 min-w-[180px]',
          'border-2 transition-all duration-200',
          STATUS_BORDER_CLASSES[status]
        )}
      >
        <div className="flex items-center gap-2 mb-2">
          <AgentAvatar
            agentId={data.agentId}
            status={STATUS_TO_AGENT_STATUS[status]}
            size="sm"
            showStatus={true}
          />
          <span className="text-sm font-medium text-zinc-200">{agentName}</span>
        </div>
        
        <p className="text-xs text-zinc-400 line-clamp-2">{data.task}</p>
        
        {data.status === 'done' && data.result && (
          <p className="text-xs text-emerald-400 mt-2 truncate">
            ✓ {data.result}
          </p>
        )}
        
        {data.status === 'blocked' && (
          <p className="text-xs text-rose-400 mt-2">
            ⚠ Blocked
          </p>
        )}
      </div>
      
      <Handle type="source" position={Position.Bottom} className="!bg-zinc-600" />
    </>
  );
}

const nodeTypes = {
  agentNode: AgentNodeComponent,
};

/**
 * Convert workflow data to React Flow nodes and edges
 */
function convertToFlowElements(
  workflowData: WorkflowData
): { nodes: Node<WorkflowNode>[]; edges: Edge[] } {
  const nodeWidth = 200;
  const nodeHeight = 100;
  const horizontalSpacing = 250;
  const verticalSpacing = 150;

  // Build dependency graph
  const dependencyMap = new Map<string, string[]>();
  const reverseDependencyMap = new Map<string, string[]>();
  
  workflowData.nodes.forEach((node) => {
    dependencyMap.set(node.id, node.dependencies || []);
    node.dependencies?.forEach((depId) => {
      if (!reverseDependencyMap.has(depId)) {
        reverseDependencyMap.set(depId, []);
      }
      reverseDependencyMap.get(depId)!.push(node.id);
    });
  });

  // Calculate levels using topological sort
  const levels = new Map<string, number>();
  const visited = new Set<string>();
  
  function calculateLevel(nodeId: string): number {
    if (levels.has(nodeId)) return levels.get(nodeId)!;
    
    const node = workflowData.nodes.find((n) => n.id === nodeId);
    if (!node) return 0;
    
    const deps = node.dependencies || [];
    if (deps.length === 0) {
      levels.set(nodeId, 0);
      return 0;
    }
    
    const maxDepLevel = Math.max(...deps.map((d) => calculateLevel(d)));
    const level = maxDepLevel + 1;
    levels.set(nodeId, level);
    return level;
  }
  
  workflowData.nodes.forEach((node) => calculateLevel(node.id));

  // Group nodes by level
  const levelGroups = new Map<number, string[]>();
  workflowData.nodes.forEach((node) => {
    const level = levels.get(node.id) || 0;
    if (!levelGroups.has(level)) {
      levelGroups.set(level, []);
    }
    levelGroups.get(level)!.push(node.id);
  });

  // Position nodes
  const nodes: Node<WorkflowNode>[] = workflowData.nodes.map((node) => {
    const level = levels.get(node.id) || 0;
    const nodesInLevel = levelGroups.get(level) || [];
    const indexInLevel = nodesInLevel.indexOf(node.id);
    const levelWidth = nodesInLevel.length * horizontalSpacing;
    
    return {
      id: node.id,
      type: 'agentNode',
      position: {
        x: indexInLevel * horizontalSpacing - levelWidth / 2 + horizontalSpacing / 2,
        y: level * verticalSpacing,
      },
      data: node,
    };
  });

  // Create edges
  const edges: Edge[] = [];
  workflowData.nodes.forEach((node) => {
    node.dependencies?.forEach((depId) => {
      edges.push({
        id: `${depId}-${node.id}`,
        source: depId,
        target: node.id,
        animated: node.status === 'working',
        style: {
          stroke: node.status === 'working' ? '#f59e0b' : '#52525b',
          strokeWidth: 2,
        },
        className: node.status === 'working' ? 'fp-edge-animated' : '',
      });
    });
  });

  return { nodes, edges };
}

/**
 * MissionGraph - React Flow DAG Workflow Visualizer
 * 
 * Renders the MetaGPT execution plan as an interactive graph.
 * Nodes show agent status with animated edges for active data flow.
 * 
 * @example
 * <MissionGraph
 *   workflowData={{
 *     nodes: [
 *       { id: '1', agentId: 'iris', task: 'Research client', status: 'done' },
 *       { id: '2', agentId: 'legal-eagle', task: 'Review contract', status: 'working', dependencies: ['1'] },
 *     ]
 *   }}
 *   onNodeClick={(node) => openAgentDetails(node)}
 * />
 */
export function MissionGraph({
  workflowData,
  onNodeClick,
  className,
}: MissionGraphProps) {
  const [selectedNode, setSelectedNode] = React.useState<WorkflowNode | null>(null);
  
  const { nodes: initialNodes, edges: initialEdges } = useMemo(
    () => convertToFlowElements(workflowData),
    [workflowData]
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update nodes when workflow data changes
  React.useEffect(() => {
    const { nodes: newNodes, edges: newEdges } = convertToFlowElements(workflowData);
    setNodes(newNodes);
    setEdges(newEdges);
  }, [workflowData, setNodes, setEdges]);

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node<WorkflowNode>) => {
      setSelectedNode(node.data);
      onNodeClick?.(node.data);
    },
    [onNodeClick]
  );

  return (
    <div className={cn('w-full h-full relative', className)}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        proOptions={{ hideAttribution: true }}
        className="bg-zinc-950"
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="rgba(255,255,255,0.1)"
        />
        <Controls className="!bg-zinc-800 !border-zinc-700 !rounded-md" />
        <MiniMap
          className="!bg-zinc-900 !border-zinc-700 !rounded-md"
          nodeColor={(node: Node<WorkflowNode>) => {
            const status = node.data.status;
            switch (status) {
              case 'done':
                return '#10b981';
              case 'working':
                return '#f59e0b';
              case 'blocked':
                return '#f43f5e';
              case 'planning':
                return '#3b82f6';
              default:
                return '#52525b';
            }
          }}
        />
      </ReactFlow>

      {/* Node details sheet */}
      <Sheet open={!!selectedNode} onOpenChange={() => setSelectedNode(null)}>
        <SheetContent className="bg-zinc-900 border-zinc-800">
          {selectedNode && (
            <>
              <SheetHeader>
                <div className="flex items-center gap-3">
                  <AgentAvatar
                    agentId={selectedNode.agentId}
                    status={STATUS_TO_AGENT_STATUS[selectedNode.status]}
                    size="lg"
                  />
                  <div>
                    <SheetTitle className="text-lg">
                      {getAgentDisplayName(selectedNode.agentId)}
                    </SheetTitle>
                    <Badge
                      variant="outline"
                      className={cn(
                        'mt-1',
                        selectedNode.status === 'done' && 'border-emerald-500 text-emerald-400',
                        selectedNode.status === 'working' && 'border-amber-500 text-amber-400',
                        selectedNode.status === 'blocked' && 'border-rose-500 text-rose-400',
                        selectedNode.status === 'planning' && 'border-blue-500 text-blue-400'
                      )}
                    >
                      {selectedNode.status.toUpperCase()}
                    </Badge>
                  </div>
                </div>
              </SheetHeader>

              <ScrollArea className="h-[calc(100vh-150px)] mt-6">
                <div className="space-y-6">
                  <div>
                    <h4 className="text-sm font-medium text-zinc-400 mb-2">Task</h4>
                    <p className="text-sm">{selectedNode.task}</p>
                  </div>

                  {selectedNode.result && (
                    <div>
                      <h4 className="text-sm font-medium text-zinc-400 mb-2">Result</h4>
                      <p className="text-sm text-emerald-400">{selectedNode.result}</p>
                    </div>
                  )}

                  {selectedNode.dependencies && selectedNode.dependencies.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-zinc-400 mb-2">Dependencies</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedNode.dependencies.map((dep) => (
                          <Badge key={dep} variant="secondary" className="font-mono text-xs">
                            {dep}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedNode.memory && Object.keys(selectedNode.memory).length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-zinc-400 mb-2">Memory Context</h4>
                      <pre className="text-xs bg-zinc-950 p-3 rounded-md overflow-auto font-mono">
                        {JSON.stringify(selectedNode.memory, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
