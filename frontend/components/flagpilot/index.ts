/**
 * FlagPilot UI Component Library
 * ==============================
 * Industrial design system components for the FlagPilot OS
 * 
 * Console-first, High-Density, Utilitarian Dark
 */

// Core Components
export { AgentAvatar, getAgentDisplayName, AGENT_ICONS, AGENT_COLORS } from './agent-avatar';
export type { AgentStatus } from './agent-avatar';

export { StreamableLog, useStreamingLogs } from './streamable-log';
export type { LogEntry } from './streamable-log';

export { CreditBalance, CreditBadge } from './credit-balance';

export { MoatFileCard, MoatDropzone } from './moat-file-card';
export type { MoatFileCardProps, SecurityLevel } from './moat-file-card';

export { ChatInterface } from './chat-interface';
export type { ChatMessage, ChatAttachment, ChatArtifact } from './chat-interface';

export { MissionGraph } from './mission-graph';
export type { WorkflowNode, WorkflowData, NodeStatus } from './mission-graph';

// Layout Components
export { CommandSidebar } from './command-sidebar';
export type { Mission, Agent, CommandSidebarProps } from './command-sidebar';

export { ContextHeader } from './context-header';
export type { ContextBreadcrumbItem, ContextHeaderProps } from './context-header';

// Re-export sidebar primitives for convenience
export { SidebarProvider, SidebarTrigger, SidebarInset } from '@/components/ui/sidebar';

export { WarRoom } from './war-room';
export type { WarRoomProps } from './war-room';

// Feature Components
export { BillingModal } from './billing-modal';
export type { BillingModalProps, PricingTier } from './billing-modal';

export { GDPRCompliance } from './gdpr-compliance';
export type { GDPRComplianceProps } from './gdpr-compliance';

export { AppLayout } from './app-layout';
export type { AppLayoutProps } from './app-layout';
