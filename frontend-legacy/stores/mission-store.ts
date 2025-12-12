import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { Node, Edge } from '@xyflow/react';

// Agent definitions matching the 13 FlagPilot agents
export const AGENT_SQUADS = {
  orchestrator: {
    name: 'Orchestrator Squad',
    color: '#6366f1', // indigo
    agents: ['flagpilot', 'scribe', 'connector', 'vault-keeper'],
  },
  risk: {
    name: 'Risk & Legal Squad',
    color: '#ef4444', // red
    agents: ['legal-eagle', 'sentinel', 'adjudicator', 'job-authenticator'],
  },
  growth: {
    name: 'Growth & Finance Squad',
    color: '#22c55e', // green
    agents: ['iris', 'negotiator', 'ledger', 'payment-enforcer', 'coach', 'scope-sentinel'],
  },
} as const;

export const AGENTS = {
  // Orchestrator Squad
  'flagpilot': {
    id: 'flagpilot',
    name: 'FlagPilot',
    icon: '🚀',
    squad: 'orchestrator',
    role: 'Orchestrator / Product Manager',
    description: 'Translates user intents into structured project requirements',
  },
  'scribe': {
    id: 'scribe',
    name: 'The Scribe',
    icon: '📝',
    squad: 'orchestrator',
    role: 'Project Manager / SOP Guardian',
    description: 'Tracks state and ensures long-running workflows are not lost',
  },
  'connector': {
    id: 'connector',
    name: 'The Connector',
    icon: '💬',
    squad: 'orchestrator',
    role: 'Communications Liaison',
    description: 'Drafts emails, messages, and proposal letters',
  },
  'vault-keeper': {
    id: 'vault-keeper',
    name: 'Vault Keeper',
    icon: '🔐',
    squad: 'orchestrator',
    role: 'File & Context Manager',
    description: 'Handles file ingestion, organization, and retrieval',
  },

  // Risk & Legal Squad
  'legal-eagle': {
    id: 'legal-eagle',
    name: 'Legal Eagle',
    icon: '🦅',
    squad: 'risk',
    role: 'Contract Guardian',
    description: 'Analyzes contracts for red flags and unfair terms',
  },
  'sentinel': {
    id: 'sentinel',
    name: 'The Sentinel',
    icon: '🛡️',
    squad: 'risk',
    role: 'Privacy & Security Officer',
    description: 'Scans for PII and protects sensitive data',
  },
  'adjudicator': {
    id: 'adjudicator',
    name: 'The Adjudicator',
    icon: '⚖️',
    squad: 'risk',
    role: 'Dispute Mediator',
    description: 'Prepares for potential litigation or arbitration',
  },
  'job-authenticator': {
    id: 'job-authenticator',
    name: 'Job Authenticator',
    icon: '🔍',
    squad: 'risk',
    role: 'Scam Shield',
    description: 'Validates job posting legitimacy and client identities',
  },

  // Growth & Finance Squad
  'iris': {
    id: 'iris',
    name: 'Iris',
    icon: '👁️',
    squad: 'growth',
    role: 'Deep Research Agent',
    description: 'Autonomous web researcher for client profiling',
  },
  'negotiator': {
    id: 'negotiator',
    name: 'The Negotiator',
    icon: '🎯',
    squad: 'growth',
    role: 'Game Theory Strategist',
    description: 'Optimizes deal terms and simulates negotiation paths',
  },
  'ledger': {
    id: 'ledger',
    name: 'The Ledger',
    icon: '📊',
    squad: 'growth',
    role: 'Finance & Tax Controller',
    description: 'Manages financial health and tax estimation',
  },
  'payment-enforcer': {
    id: 'payment-enforcer',
    name: 'Payment Enforcer',
    icon: '💰',
    squad: 'growth',
    role: 'Collections Agent',
    description: 'Implements escalation ladder for overdue payments',
  },
  'coach': {
    id: 'coach',
    name: 'The Coach',
    icon: '🏆',
    squad: 'growth',
    role: 'Talent Vet & Skill Optimizer',
    description: 'Career development mentor and profile optimizer',
  },
  'scope-sentinel': {
    id: 'scope-sentinel',
    name: 'Scope Sentinel',
    icon: '📏',
    squad: 'growth',
    role: 'Scope Creep Detector',
    description: 'Monitors project boundaries and flags scope changes',
  },
} as const;

export type AgentId = keyof typeof AGENTS;
export type AgentStatus = 'idle' | 'thinking' | 'working' | 'waiting' | 'done' | 'error';

export interface AgentNode extends Node {
  data: {
    agentId: AgentId;
    status: AgentStatus;
    currentAction?: string;
    progress?: number;
    thought?: string;
  };
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  agentId?: AgentId;
  timestamp: Date;
  uiComponent?: UIComponentMessage;
  attachments?: any[]; // Using any[] for now to match UI expectation, should be typed properly
}

export interface UIComponentMessage {
  type: 'ui_component';
  componentName: string;
  props: Record<string, any>;
}

export interface Artifact {
  id: string;
  name: string;
  type: 'pdf' | 'json' | 'text' | 'email';
  createdBy: AgentId;
  createdAt: Date;
  content?: string;
  url?: string;
}

export interface Mission {
  id: string;
  title: string;
  status: 'active' | 'completed' | 'paused' | 'failed';
  createdAt: Date;
  updatedAt: Date;
}

interface MissionState {
  // Current mission
  currentMission: Mission | null;

  // Workflow visualization
  nodes: AgentNode[];
  edges: Edge[];

  // Chat
  messages: ChatMessage[];

  // Agent states
  activeAgents: Set<AgentId>;
  agentStates: Map<AgentId, { status: AgentStatus; action?: string }>;

  // Artifacts
  artifacts: Artifact[];

  // UI state
  selectedAgentId: AgentId | null;
  isPanelCollapsed: boolean;

  // Actions
  startMission: (title: string) => void;
  endMission: () => void;

  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  clearMessages: () => void;

  updateAgentStatus: (agentId: AgentId, status: AgentStatus, action?: string) => void;
  setAgentThought: (agentId: AgentId, thought: string) => void;

  updateWorkflow: (nodes: AgentNode[], edges: Edge[]) => void;

  addArtifact: (artifact: Omit<Artifact, 'id' | 'createdAt'>) => void;

  selectAgent: (agentId: AgentId | null) => void;
  togglePanel: () => void;

  // SSE/WebSocket handling
  processStreamEvent: (event: StreamEvent) => void;
}

export type StreamEvent =
  | { type: 'agent_thinking'; agentId: AgentId; thought: string }
  | { type: 'agent_status'; agentId: AgentId; status: AgentStatus; action?: string }
  | { type: 'workflow_update'; nodes: AgentNode[]; edges: Edge[] }
  | { type: 'message'; content: string; agentId?: AgentId }
  | { type: 'ui_component'; componentName: string; props: Record<string, any> }
  | { type: 'artifact'; artifact: Omit<Artifact, 'id' | 'createdAt'> }
  | { type: 'mission_complete' };

export const useMissionStore = create<MissionState>()(
  devtools(
    (set, get) => ({
      // Initial state
      currentMission: null,
      nodes: [],
      edges: [],
      messages: [],
      activeAgents: new Set(),
      agentStates: new Map(),
      artifacts: [],
      selectedAgentId: null,
      isPanelCollapsed: false,

      // Mission actions
      startMission: (title) => set({
        currentMission: {
          id: `mission-${Date.now()}`,
          title,
          status: 'active',
          createdAt: new Date(),
          updatedAt: new Date(),
        },
        messages: [],
        nodes: [],
        edges: [],
        artifacts: [],
        activeAgents: new Set(),
        agentStates: new Map(),
      }),

      endMission: () => set((state) => ({
        currentMission: state.currentMission
          ? { ...state.currentMission, status: 'completed', updatedAt: new Date() }
          : null,
        activeAgents: new Set(),
      })),

      // Message actions
      addMessage: (message) => set((state) => ({
        messages: [
          ...state.messages,
          {
            ...message,
            id: `msg-${Date.now()}-${Math.random().toString(36).slice(2)}`,
            timestamp: new Date(),
          },
        ],
      })),

      clearMessages: () => set({ messages: [] }),

      // Agent actions
      updateAgentStatus: (agentId, status, action) => set((state) => {
        const newAgentStates = new Map(state.agentStates);
        newAgentStates.set(agentId, { status, action });

        const newActiveAgents = new Set(state.activeAgents);
        if (status === 'thinking' || status === 'working') {
          newActiveAgents.add(agentId);
        } else if (status === 'done' || status === 'idle' || status === 'error') {
          newActiveAgents.delete(agentId);
        }

        // Update node if it exists
        const newNodes = state.nodes.map((node) => {
          if (node.data.agentId === agentId) {
            return {
              ...node,
              data: { ...node.data, status, currentAction: action },
            };
          }
          return node;
        });

        return {
          agentStates: newAgentStates,
          activeAgents: newActiveAgents,
          nodes: newNodes,
        };
      }),

      setAgentThought: (agentId, thought) => set((state) => ({
        nodes: state.nodes.map((node) => {
          if (node.data.agentId === agentId) {
            return { ...node, data: { ...node.data, thought } };
          }
          return node;
        }),
      })),

      // Workflow actions
      updateWorkflow: (nodes, edges) => set({ nodes, edges }),

      // Artifact actions
      addArtifact: (artifact) => set((state) => ({
        artifacts: [
          ...state.artifacts,
          {
            ...artifact,
            id: `artifact-${Date.now()}`,
            createdAt: new Date(),
          },
        ],
      })),

      // UI actions
      selectAgent: (agentId) => set({ selectedAgentId: agentId }),
      togglePanel: () => set((state) => ({ isPanelCollapsed: !state.isPanelCollapsed })),

      // Stream event processing
      processStreamEvent: (event) => {
        const state = get();

        switch (event.type) {
          case 'agent_thinking':
            state.setAgentThought(event.agentId, event.thought);
            state.updateAgentStatus(event.agentId, 'thinking');
            break;

          case 'agent_status':
            state.updateAgentStatus(event.agentId, event.status, event.action);
            break;

          case 'workflow_update':
            state.updateWorkflow(event.nodes, event.edges);
            break;

          case 'message':
            state.addMessage({
              role: 'assistant',
              content: event.content,
              agentId: event.agentId,
            });
            break;

          case 'ui_component':
            state.addMessage({
              role: 'assistant',
              content: '',
              uiComponent: {
                type: 'ui_component',
                componentName: event.componentName,
                props: event.props,
              },
            });
            break;

          case 'artifact':
            state.addArtifact(event.artifact);
            break;

          case 'mission_complete':
            state.endMission();
            break;
        }
      },
    }),
    { name: 'mission-store' }
  )
);
