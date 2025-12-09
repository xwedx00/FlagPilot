"use client";

import { useState, useRef, useEffect, useCallback } from 'react';
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Markdown } from '@/components/ui/markdown';
import {
  Send,
  Workflow,
  FileText,
  Database,
  Activity,
  Sparkles,
  Zap,
  MessageSquare,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useMissionStore, AGENTS, type AgentId, type ChatMessage } from '@/stores/mission-store';
import { Visualizer } from './visualizer';
import { toast } from 'sonner';
import { useWorkflowStream, useStartWorkflow, TabType } from '@/hooks/use-workflow-stream';
import { FileUpload } from '@/components/file-upload';

interface WarRoomProps {
  className?: string;
}

export function WarRoom({ className }: WarRoomProps) {
  const {
    currentMission,
    messages,
    addMessage,
    activeAgents,
    artifacts,
    startMission,
  } = useMissionStore();

  const [input, setInput] = useState('');
  const [activeTab, setActiveTab] = useState<TabType>('visualizer');
  const [missionMode, setMissionMode] = useState(true);
  const [activeMissionId, setActiveMissionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const lastArtifactCount = useRef(artifacts.length);

  // File upload state
  const [isUploading, setIsUploading] = useState(false);
  const [pendingUploads, setPendingUploads] = useState<any[]>([]);

  // Workflow streaming hook with auto-tab switching
  const { isConnected, isStreaming } = useWorkflowStream({
    missionId: activeMissionId,
    onTabChange: (tab) => setActiveTab(tab),
    onAgentActivity: () => { },
    onError: (error) => toast.error(`Stream error: ${error.message}`),
  });

  // Hook for starting workflows
  const { start: startWorkflow, isLoading } = useStartWorkflow();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-switch to artifacts tab when new artifact is generated
  useEffect(() => {
    if (artifacts.length > lastArtifactCount.current) {
      setActiveTab('artifacts');
      toast.success('New artifact generated!');
    }
    lastArtifactCount.current = artifacts.length;
  }, [artifacts.length]);

  // Handle mission mode with real-time SSE streaming
  const handleMissionStart = useCallback(async (userInput: string) => {
    setActiveTab('visualizer');

    // Include context from pending uploads if any
    const options = pendingUploads.length > 0
      ? { fileIds: pendingUploads.map(f => f.id) }
      : undefined;

    const missionId = await startWorkflow(userInput, options);

    if (missionId) {
      setActiveMissionId(missionId);
      toast.success('Mission started - agents are working...');
      setPendingUploads([]); // Clear pending uploads after start
    }

    return missionId;
  }, [startWorkflow, pendingUploads]);

  // Handle simple chat mode (connected to backend stream)
  const handleChatMessage = useCallback(async (userInput: string) => {
    try {
      // Use the streaming endpoint for chat as well
      // Temporary fallback: direct fetch to stream endpoint for test
      // In reality, should probably use useChat from Vercel AI SDK or similar
      // For now, we simulate a response to prove connectivity
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/stream/test-llm?task=${encodeURIComponent(userInput)}`);

      if (!response.ok) throw new Error('Chat request failed');

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let fullContent = '';

      addMessage({ role: 'assistant', content: '' });

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        // Simple SSE parsing (very basic)
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.token) fullContent += data.token;
            } catch (e) {
              // ignore
            }
          }
        }

        // Update UI logic...
        useMissionStore.setState((state) => ({
          messages: state.messages.map((m, i) =>
            i === state.messages.length - 1 && m.role === 'assistant'
              ? { ...m, content: fullContent || "Streaming response..." } // Fallback for visibility
              : m
          ),
        }));
      }
    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Chat request failed');
    }
  }, [addMessage, messages]);

  const handleSendMessage = async () => {
    if ((!input.trim() && pendingUploads.length === 0) || isLoading) return;

    const userInput = input.trim();
    setInput('');

    if (!currentMission) {
      startMission(userInput.slice(0, 50));
    }

    addMessage({
      role: 'user',
      content: userInput,
      // Add attachments visual
      attachments: pendingUploads
    });

    try {
      if (missionMode) {
        await handleMissionStart(userInput);
      } else {
        await handleChatMessage(userInput);
      }
    } catch (error) {
      toast.error('Request failed');
      console.error(error);
    }
  };

  const getAgentInfo = (agentId?: AgentId) => {
    if (!agentId) return { name: 'FlagPilot', icon: '🚀' };
    const agent = AGENTS[agentId];
    return agent ? { name: agent.name, icon: agent.icon } : { name: 'FlagPilot', icon: '🚀' };
  };

  return (
    <div className={cn('flex flex-col h-full bg-slate-950', className)}>
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-800 bg-slate-900/50">
        <div className="flex items-center gap-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
            <Sparkles className="h-4 w-4 text-primary" />
          </div>
          <div>
            <h2 className="font-semibold text-white text-sm">
              {currentMission?.title || 'Mission Control'}
            </h2>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              {currentMission ? (
                <>
                  <Badge variant="outline" className="h-5 px-1.5 text-[10px]">
                    {currentMission.status}
                  </Badge>
                  <span className="mx-1">•</span>
                  <span>{activeAgents.size} agents active</span>
                  {isStreaming && (
                    <>
                      <span className="mx-1">•</span>
                      <span className="flex items-center gap-1 text-primary">
                        <Activity className="h-3 w-3 animate-pulse" />
                        Streaming
                      </span>
                    </>
                  )}
                </>
              ) : (
                <span>Start a new mission</span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {activeAgents.size > 0 && (
            <div className="flex items-center gap-1">
              {Array.from(activeAgents).slice(0, 5).map((agentId) => {
                const agent = AGENTS[agentId];
                return (
                  <div
                    key={agentId}
                    className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/20 text-xs animate-pulse"
                    title={agent?.name}
                  >
                    {agent?.icon}
                  </div>
                );
              })}
              {activeAgents.size > 5 && (
                <span className="text-xs text-slate-400">+{activeAgents.size - 5}</span>
              )}
            </div>
          )}

          <Button
            variant="ghost"
            size="sm"
            onClick={() => setMissionMode(!missionMode)}
            className={cn(
              'h-8 px-2 gap-1.5',
              missionMode ? 'text-primary' : 'text-slate-400'
            )}
          >
            {missionMode ? (
              <>
                <Zap className="h-3.5 w-3.5" />
                <span className="text-xs">Mission</span>
              </>
            ) : (
              <>
                <MessageSquare className="h-3.5 w-3.5" />
                <span className="text-xs">Chat</span>
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Main content */}
      <ResizablePanelGroup direction="horizontal" className="flex-1">
        {/* Chat Panel */}
        <ResizablePanel defaultSize={40} minSize={30}>
          <div className="flex flex-col h-full">
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4">
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full py-12 text-center">
                    <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/20 to-purple-500/20 mb-4">
                      <Sparkles className="h-8 w-8 text-primary" />
                    </div>
                    <h3 className="font-semibold text-white mb-2">Mission Control Ready</h3>
                    <p className="text-sm text-slate-400 max-w-[280px]">
                      Describe your task and the FlagPilot agent swarm will coordinate to help you.
                    </p>
                  </div>
                ) : (
                  messages.map((message) => {
                    const agentInfo = getAgentInfo(message.agentId);

                    return (
                      <div
                        key={message.id}
                        className={cn(
                          'flex gap-3',
                          message.role === 'user' && 'flex-row-reverse'
                        )}
                      >
                        <Avatar className={cn(
                          'h-8 w-8 border',
                          message.role === 'user'
                            ? 'bg-primary/20 border-primary/30'
                            : 'bg-slate-800 border-slate-700'
                        )}>
                          <AvatarFallback className="text-sm">
                            {message.role === 'user' ? '👤' : agentInfo.icon}
                          </AvatarFallback>
                        </Avatar>
                        <div className={cn(
                          'flex-1 max-w-[80%]',
                          message.role === 'user' && 'flex flex-col items-end'
                        )}>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium text-slate-400">
                              {message.role === 'user' ? 'You' : agentInfo.name}
                            </span>
                          </div>
                          <div className={cn(
                            'rounded-lg px-3 py-2 text-sm',
                            message.role === 'user'
                              ? 'bg-primary text-primary-foreground'
                              : 'bg-slate-800 text-slate-100'
                          )}>
                            <Markdown>{message.content}</Markdown>
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>

            {/* Input */}
            <div className="p-4 border-t border-slate-800 space-y-3">
              <FileUpload
                onUploadComplete={(files) => setPendingUploads(prev => [...prev, ...files])}
                className="w-full"
                maxFiles={3}
              />
              {pendingUploads.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {pendingUploads.map(f => (
                    <Badge key={f.id} variant="secondary" className="text-xs">
                      {f.name}
                    </Badge>
                  ))}
                </div>
              )}
              <div className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Describe your mission..."
                  className="flex-1 bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  disabled={isLoading}
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!input.trim() || isLoading}
                  className="bg-primary hover:bg-primary/90"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </ResizablePanel>

        <ResizableHandle className="w-1 bg-slate-800" />

        {/* Right Panel - Visualizer/Artifacts */}
        <ResizablePanel defaultSize={60} minSize={40}>
          <div className="h-full flex flex-col">
            <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as TabType)} className="flex-1 flex flex-col">
              <div className="px-4 pt-3 border-b border-slate-800">
                <TabsList className="bg-slate-900">
                  <TabsTrigger value="visualizer" className="gap-1.5">
                    <Workflow className="h-3.5 w-3.5" />
                    Visualizer
                  </TabsTrigger>
                  <TabsTrigger value="artifacts" className="gap-1.5">
                    <FileText className="h-3.5 w-3.5" />
                    Artifacts
                  </TabsTrigger>
                  <TabsTrigger value="context" className="gap-1.5">
                    <Database className="h-3.5 w-3.5" />
                    Data Moat
                  </TabsTrigger>
                </TabsList>
              </div>

              <TabsContent value="visualizer" className="flex-1 m-0">
                <Visualizer />
              </TabsContent>

              <TabsContent value="artifacts" className="flex-1 m-0 p-4 overflow-auto">
                {artifacts.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center">
                    <FileText className="h-12 w-12 text-slate-600 mb-4" />
                    <p className="text-sm text-slate-400">
                      Artifacts will appear here as agents complete their work.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {artifacts.map((artifact) => (
                      <div key={artifact.id} className="p-4 rounded-lg bg-slate-900 border border-slate-800">
                        <h4 className="font-medium text-white mb-2">{artifact.name}</h4>
                        <p className="text-sm text-slate-400">{artifact.type}</p>
                      </div>
                    ))}
                  </div>
                )}
              </TabsContent>

              <TabsContent value="context" className="flex-1 m-0 p-4 overflow-auto">
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <Database className="h-12 w-12 text-slate-600 mb-4" />
                  <p className="text-sm text-slate-400">
                    Your uploaded files and context will be available here.
                  </p>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}
