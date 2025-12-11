"use client";

import { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  type Connection,
  type Edge,
  type Node,
  BackgroundVariant,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { useMissionStore, AGENTS, type AgentId } from '@/stores/mission-store';
import { AgentNode, type AgentNodeData } from './agent-node';
import { cn } from '@/lib/utils';

// Custom node types
const nodeTypes = {
  agent: AgentNode,
};

// Default edge options
const defaultEdgeOptions = {
  animated: true,
  style: { stroke: '#475569', strokeWidth: 2 },
  markerEnd: {
    type: MarkerType.ArrowClosed,
    color: '#475569',
  },
};

// Generate initial layout for all agents
function generateInitialLayout(): { nodes: Node[]; edges: Edge[] } {
  const agentIds = Object.keys(AGENTS) as AgentId[];

  // Position agents in squads
  const squadPositions = {
    orchestrator: { x: 50, y: 50 },
    risk: { x: 400, y: 50 },
    growth: { x: 750, y: 50 },
  };

  const nodes: Node[] = [];
  const squadCounts: Record<string, number> = { orchestrator: 0, risk: 0, growth: 0 };

  agentIds.forEach((agentId) => {
    const agent = AGENTS[agentId];
    const squad = agent.squad;
    const position = squadPositions[squad as keyof typeof squadPositions];
    const index = squadCounts[squad];
    squadCounts[squad]++;

    nodes.push({
      id: agentId,
      type: 'agent',
      position: {
        x: position.x,
        y: position.y + (index * 140),
      },
      data: {
        agentId,
        status: 'idle',
      },
    });
  });

  // Start with empty edges - backend provides real connections via SSE
  const edges: Edge[] = [];

  return { nodes, edges };
}

interface VisualizerProps {
  className?: string;
  minimal?: boolean;
}

export function Visualizer({ className, minimal = false }: VisualizerProps) {
  const { nodes: storeNodes, edges: storeEdges, selectAgent } = useMissionStore();

  // Use store nodes if available, otherwise generate initial layout
  const initialLayout = useMemo(() => generateInitialLayout(), []);

  const displayNodes = storeNodes.length > 0 ? storeNodes : initialLayout.nodes;
  const displayEdges = storeEdges.length > 0 ? storeEdges : initialLayout.edges;

  const [nodes, setNodes, onNodesChange] = useNodesState(displayNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(displayEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      selectAgent(node.id as AgentId);
    },
    [selectAgent]
  );

  return (
    <div className={cn('h-full w-full bg-slate-950', className)}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        defaultEdgeOptions={defaultEdgeOptions}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.3}
        maxZoom={1.5}
        proOptions={{ hideAttribution: true }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="#334155"
        />
        {!minimal && (
          <>
            <Controls
              className="!bg-slate-900/90 !border-slate-600 !shadow-xl [&>button]:!bg-slate-800 [&>button]:!border-slate-600 [&>button]:!text-white [&>button:hover]:!bg-slate-700 [&>button>svg]:!fill-white"
              showInteractive={false}
            />
            <MiniMap
              className="!bg-slate-900 !border-slate-700"
              nodeColor={(node) => {
                const data = node.data as unknown as AgentNodeData | undefined;
                if (data?.status === 'working') return '#3b82f6';
                if (data?.status === 'thinking') return '#eab308';
                if (data?.status === 'done') return '#22c55e';
                if (data?.status === 'error') return '#ef4444';
                return '#64748b';
              }}
              maskColor="rgba(15, 23, 42, 0.8)"
            />
          </>
        )}
      </ReactFlow>
    </div>
  );
}
