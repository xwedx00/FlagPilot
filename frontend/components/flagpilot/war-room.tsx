'use client';

import * as React from 'react';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { GitBranch, FileText, Globe, Zap } from 'lucide-react';
import { ChatInterface, type ChatMessage } from './chat-interface';
import { MissionGraph, type WorkflowData } from './mission-graph';

interface WarRoomProps {
  missionId: string;
  missionName: string;
  messages: ChatMessage[];
  workflowData?: WorkflowData;
  isAgentThinking?: boolean;
  raceMode?: {
    active: boolean;
    agentCount: number;
  };
  onSendMessage: (message: string, attachments?: File[]) => void;
  className?: string;
}

/**
 * RaceModeBanner - Displayed when multiple agents are racing
 */
function RaceModeBanner({ agentCount }: { agentCount: number }) {
  return (
    <div className="fp-race-banner flex items-center gap-2">
      <Zap className="w-4 h-4 text-amber-400" />
      <span className="text-amber-200">
        Race Mode Active: <strong>{agentCount} Agents</strong> Running
      </span>
    </div>
  );
}

/**
 * WarRoom - The main mission interface with split-panel layout
 * 
 * Panel A (35%): Chat Stream (The Strategist)
 * Panel B (65%): Workspace with tabs:
 *   - Workflow: React Flow DAG visualizer
 *   - Document: File editor/viewer
 *   - Browser: Research results view
 * 
 * @example
 * <WarRoom
 *   missionId="123"
 *   missionName="Alpha Corp Negotiation"
 *   messages={messages}
 *   workflowData={workflow}
 *   onSendMessage={handleSend}
 * />
 */
export function WarRoom({
  missionId,
  missionName,
  messages,
  workflowData,
  isAgentThinking = false,
  raceMode,
  onSendMessage,
  className,
}: WarRoomProps) {
  const [activeTab, setActiveTab] = useState('workflow');

  return (
    <div className={cn('h-full flex flex-col', className)}>
      {/* Race Mode Banner */}
      {raceMode?.active && <RaceModeBanner agentCount={raceMode.agentCount} />}

      <ResizablePanelGroup direction="horizontal" className="flex-1">
        {/* Panel A: The Strategist (Chat Stream) */}
        <ResizablePanel
          defaultSize={35}
          minSize={25}
          maxSize={50}
          className="flex flex-col"
        >
          <div className="h-12 flex items-center px-4 border-b border-zinc-800">
            <h2 className="text-sm font-medium text-zinc-300">Chat</h2>
            {isAgentThinking && (
              <Badge variant="secondary" className="ml-2 text-xs bg-purple-500/20 text-purple-400">
                Thinking...
              </Badge>
            )}
          </div>
          <ChatInterface
            messages={messages}
            onSend={onSendMessage}
            isLoading={isAgentThinking}
            className="flex-1"
          />
        </ResizablePanel>

        <ResizableHandle className="w-px bg-zinc-800 hover:bg-purple-500 transition-colors" />

        {/* Panel B: The Workspace */}
        <ResizablePanel defaultSize={65} minSize={40}>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
            <div className="h-12 flex items-center px-4 border-b border-zinc-800">
              <TabsList className="bg-transparent border-none h-auto p-0 gap-1">
                <TabsTrigger
                  value="workflow"
                  className={cn(
                    'px-3 py-1.5 text-sm rounded-md border border-transparent',
                    'data-[state=active]:bg-zinc-800 data-[state=active]:border-zinc-700',
                    'data-[state=inactive]:text-zinc-500 data-[state=inactive]:hover:text-zinc-300'
                  )}
                >
                  <GitBranch className="w-3.5 h-3.5 mr-1.5" />
                  Workflow
                </TabsTrigger>
                <TabsTrigger
                  value="document"
                  className={cn(
                    'px-3 py-1.5 text-sm rounded-md border border-transparent',
                    'data-[state=active]:bg-zinc-800 data-[state=active]:border-zinc-700',
                    'data-[state=inactive]:text-zinc-500 data-[state=inactive]:hover:text-zinc-300'
                  )}
                >
                  <FileText className="w-3.5 h-3.5 mr-1.5" />
                  Document
                </TabsTrigger>
                <TabsTrigger
                  value="browser"
                  className={cn(
                    'px-3 py-1.5 text-sm rounded-md border border-transparent',
                    'data-[state=active]:bg-zinc-800 data-[state=active]:border-zinc-700',
                    'data-[state=inactive]:text-zinc-500 data-[state=inactive]:hover:text-zinc-300'
                  )}
                >
                  <Globe className="w-3.5 h-3.5 mr-1.5" />
                  Browser
                </TabsTrigger>
              </TabsList>
            </div>

            {/* Workflow Tab */}
            <TabsContent value="workflow" className="flex-1 m-0 p-0">
              {workflowData && workflowData.nodes.length > 0 ? (
                <MissionGraph workflowData={workflowData} className="h-full" />
              ) : (
                <div className="h-full fp-dot-pattern flex flex-col items-center justify-center text-center p-8">
                  <GitBranch className="w-12 h-12 text-zinc-600 mb-4" />
                  <h3 className="text-lg font-medium text-zinc-400 mb-2">
                    No Active Workflow
                  </h3>
                  <p className="text-sm text-zinc-500 max-w-sm">
                    Start a conversation to generate a workflow. The execution
                    plan will appear here.
                  </p>
                </div>
              )}
            </TabsContent>

            {/* Document Tab */}
            <TabsContent value="document" className="flex-1 m-0 p-0">
              <div className="h-full fp-dot-pattern flex flex-col items-center justify-center text-center p-8">
                <FileText className="w-12 h-12 text-zinc-600 mb-4" />
                <h3 className="text-lg font-medium text-zinc-400 mb-2">
                  Document Editor
                </h3>
                <p className="text-sm text-zinc-500 max-w-sm">
                  When an agent works on a document, it will appear here with
                  redline markup for proposed changes.
                </p>
              </div>
            </TabsContent>

            {/* Browser Tab */}
            <TabsContent value="browser" className="flex-1 m-0 p-0">
              <div className="h-full fp-dot-pattern flex flex-col items-center justify-center text-center p-8">
                <Globe className="w-12 h-12 text-zinc-600 mb-4" />
                <h3 className="text-lg font-medium text-zinc-400 mb-2">
                  Research Browser
                </h3>
                <p className="text-sm text-zinc-500 max-w-sm">
                  When Iris performs web research, the live results will stream
                  here.
                </p>
              </div>
            </TabsContent>
          </Tabs>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}

export type { WarRoomProps };
