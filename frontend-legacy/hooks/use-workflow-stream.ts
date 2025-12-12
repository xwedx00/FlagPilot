/**
 * Real-time workflow streaming hook
 * 
 * Connects to the backend SSE stream at /api/v1/stream/mission/{id}
 * and processes agent events for live workflow updates.
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { useMissionStore, StreamEvent, AgentId } from '@/stores/mission-store';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Helper function to process stream events by type
 * Used by both standard SSE and Vercel AI SDK format parsers
 */
function processEventByType(
  eventType: string,
  data: Record<string, unknown>,
  processStreamEvent: (event: StreamEvent) => void
) {
  switch (eventType) {
    case 'agent_status':
      processStreamEvent({
        type: 'agent_status',
        agentId: data.agentId as AgentId,
        status: data.status as 'idle' | 'thinking' | 'working' | 'waiting' | 'done' | 'error',
        action: data.action as string | undefined,
      });
      break;
    case 'agent_thinking':
      processStreamEvent({
        type: 'agent_thinking',
        agentId: data.agentId as AgentId,
        thought: data.thought as string,
      });
      break;
    case 'workflow_update':
      processStreamEvent({
        type: 'workflow_update',
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        nodes: data.nodes as any[],
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        edges: data.edges as any[],
      });
      break;
    case 'message':
      processStreamEvent({
        type: 'message',
        content: data.content as string,
        agentId: data.agentId as AgentId,
      });
      break;
    case 'ui_component':
      processStreamEvent({
        type: 'ui_component',
        componentName: data.componentName as string,
        props: data.props as Record<string, unknown>,
      });
      break;
    case 'workflow_complete':
    case 'mission_complete':
      processStreamEvent({ type: 'mission_complete' });
      break;
  }
}

export type TabType = 'visualizer' | 'artifacts' | 'context';

interface UseWorkflowStreamOptions {
  missionId: string | null;
  onTabChange?: (tab: TabType) => void;
  onAgentActivity?: (agentId: AgentId) => void;
  onError?: (error: Error) => void;
}

interface WorkflowStreamState {
  isConnected: boolean;
  isStreaming: boolean;
  lastEvent: StreamEvent | null;
  error: Error | null;
}

export function useWorkflowStream({
  missionId,
  onTabChange,
  onAgentActivity,
  onError,
}: UseWorkflowStreamOptions) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const [state, setState] = useState<WorkflowStreamState>({
    isConnected: false,
    isStreaming: false,
    lastEvent: null,
    error: null,
  });

  // Use refs to store callbacks - prevents infinite re-render loops
  const callbacksRef = useRef({ onTabChange, onAgentActivity, onError });
  callbacksRef.current = { onTabChange, onAgentActivity, onError };

  const { processStreamEvent } = useMissionStore();

  // Process incoming SSE events - stable callback
  const handleEvent = useCallback((event: StreamEvent) => {
    setState(prev => ({ ...prev, lastEvent: event }));

    // Auto-switch tabs based on event type
    const { onTabChange } = callbacksRef.current;
    if (onTabChange) {
      switch (event.type) {
        case 'workflow_update':
          onTabChange('visualizer');
          break;
        case 'artifact':
          onTabChange('artifacts');
          break;
      }
    }

    // Notify about agent activity
    if ('agentId' in event && event.agentId && callbacksRef.current.onAgentActivity) {
      callbacksRef.current.onAgentActivity(event.agentId);
    }

    // Process event in store
    processStreamEvent(event);
  }, [processStreamEvent]);

  // Connect to SSE stream - stable callback
  const connect = useCallback((targetMissionId: string, task?: string) => {
    // Close existing connection
    eventSourceRef.current?.close();

    const taskParam = task ? encodeURIComponent(task) : 'Analyze%20request';
    const eventSource = new EventSource(
      `${API_BASE_URL}/api/v1/stream/mission/${targetMissionId}?task=${taskParam}`,
      { withCredentials: true }
    );

    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      console.log('SSE connected to:', targetMissionId);
      setState(prev => ({ ...prev, isConnected: true, isStreaming: true, error: null }));
    };

    // Agent status updates
    eventSource.addEventListener('agent_status', (e) => {
      try {
        const data = JSON.parse(e.data);
        handleEvent({
          type: 'agent_status',
          agentId: data.agentId,
          status: data.status,
          action: data.action,
        });
      } catch (err) {
        console.error('Failed to parse agent_status event:', err);
      }
    });

    // Agent thinking (chain-of-thought)
    eventSource.addEventListener('agent_thinking', (e) => {
      try {
        const data = JSON.parse(e.data);
        handleEvent({
          type: 'agent_thinking',
          agentId: data.agentId,
          thought: data.thought,
        });
      } catch (err) {
        console.error('Failed to parse agent_thinking event:', err);
      }
    });

    // Workflow DAG updates
    eventSource.addEventListener('workflow_update', (e) => {
      try {
        const data = JSON.parse(e.data);
        handleEvent({
          type: 'workflow_update',
          nodes: data.nodes,
          edges: data.edges,
        });
      } catch (err) {
        console.error('Failed to parse workflow_update event:', err);
      }
    });

    // Chat messages from agents
    eventSource.addEventListener('message', (e) => {
      try {
        const data = JSON.parse(e.data);
        handleEvent({
          type: 'message',
          content: data.content,
          agentId: data.agentId,
        });
      } catch (err) {
        console.error('Failed to parse message event:', err);
      }
    });

    // Generative UI components
    eventSource.addEventListener('ui_component', (e) => {
      try {
        const data = JSON.parse(e.data);
        handleEvent({
          type: 'ui_component',
          componentName: data.componentName,
          props: data.props,
        });
      } catch (err) {
        console.error('Failed to parse ui_component event:', err);
      }
    });

    // Artifacts generated
    eventSource.addEventListener('artifact', (e) => {
      try {
        const data = JSON.parse(e.data);
        handleEvent({
          type: 'artifact',
          artifact: data,
        });
      } catch (err) {
        console.error('Failed to parse artifact event:', err);
      }
    });

    // Connected event
    eventSource.addEventListener('connected', (e) => {
      console.log('SSE connected event received');
    });

    // Mission complete
    eventSource.addEventListener('mission_complete', () => {
      handleEvent({ type: 'mission_complete' });
      setState(prev => ({ ...prev, isStreaming: false }));
      eventSource.close();
    });

    // Error handling
    eventSource.onerror = (err) => {
      console.error('SSE error:', err);
      const error = new Error('SSE connection failed');
      setState(prev => ({ ...prev, isConnected: false, isStreaming: false, error }));
      callbacksRef.current.onError?.(error);
      eventSource.close();
    };

    return eventSource;
  }, [handleEvent]);

  // Disconnect from SSE
  const disconnect = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
    setState(prev => ({ ...prev, isConnected: false, isStreaming: false }));
  }, []);

  // Auto-connect when missionId changes
  useEffect(() => {
    if (missionId) {
      connect(missionId);
    }
    return () => {
      disconnect();
    };
  }, [missionId]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    ...state,
    connect,
    disconnect,
  };
}

/**
 * Hook for starting a new workflow with SSE streaming
 */
export function useStartWorkflow() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const { startMission, processStreamEvent, addMessage } = useMissionStore();

  const start = useCallback(async (
    prompt: string,
    options?: {
      fileIds?: string[];
      privacyMode?: boolean;
    }
  ): Promise<string | null> => {
    setIsLoading(true);
    setError(null);

    try {
      // Generate a client-side mission ID
      const missionId = `mission-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;

      // Start local mission state
      startMission(prompt.slice(0, 50));

      // Use the new /chat endpoint for reliable streaming
      const response = await fetch(`${API_BASE_URL}/api/v1/stream/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          message: prompt,
          context: options?.fileIds ? { fileIds: options.fileIds } : undefined,
        }),
      });

      if (!response.ok) {
        throw new Error(`Stream failed: ${response.status}`);
      }

      // Process SSE stream - supports both standard SSE and Vercel AI SDK format
      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let buffer = '';

      const processStream = async () => {
        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            let currentEvent = '';
            for (const line of lines) {
              // Standard SSE format: "event: xxx"
              if (line.startsWith('event: ')) {
                currentEvent = line.slice(7).trim();
              }
              // Standard SSE format: "data: {...}"
              else if (line.startsWith('data: ') && currentEvent) {
                try {
                  const data = JSON.parse(line.slice(6));
                  processEventByType(currentEvent, data, processStreamEvent);
                } catch (e) {
                  console.warn('Failed to parse SSE data:', e);
                }
                currentEvent = '';
              }
              // Vercel AI SDK format: "2:[{...}]" for custom data
              else if (line.match(/^2:\[.*\]$/)) {
                try {
                  const jsonContent = line.slice(2); // Remove "2:"
                  const dataArray = JSON.parse(jsonContent);
                  for (const data of dataArray) {
                    if (data.type) {
                      processEventByType(data.type, data, processStreamEvent);
                    }
                  }
                } catch (e) {
                  console.warn('Failed to parse Vercel data:', e);
                }
              }
              // Vercel AI SDK format: "0:\"text\"" for text content
              else if (line.match(/^0:".*"$/)) {
                try {
                  const textContent = JSON.parse(line.slice(2));
                  // Process as message event
                  processStreamEvent({
                    type: 'message',
                    content: textContent,
                    agentId: 'flagpilot' as AgentId,
                  });
                } catch (e) {
                  // Ignore text parse errors
                }
              }
              // Vercel AI SDK format: "d:{...}" for finish
              else if (line.startsWith('d:')) {
                try {
                  const finishData = JSON.parse(line.slice(2));
                  if (finishData.finishReason) {
                    processStreamEvent({ type: 'mission_complete' });
                  }
                } catch (e) {
                  // Ignore finish parse errors
                }
              }
            }
          }
        } catch (error) {
          console.error('Stream processing error:', error);
        }
      };

      // Start processing in background
      processStream();

      return missionId;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [startMission, processStreamEvent]);

  const executeSaved = useCallback(async (
    workflowId: string,
    initialMessage: string = "Execute workflow"
  ): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      // Start local mission state
      startMission(`Running Workflow: ${workflowId}`);

      const response = await fetch(`${API_BASE_URL}/api/v1/stream/workflow/${workflowId}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          message: initialMessage,
          user_id: 'user' // Replaced by session middleware on backend usually
        }),
      });

      if (!response.ok) {
        throw new Error(`Execution failed: ${response.status}`);
      }

      // Reuse the same stream processor logic
      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let buffer = '';

      const processStream = async () => {
        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            let currentEvent = '';
            for (const line of lines) {
              if (line.startsWith('event: ')) {
                currentEvent = line.slice(7).trim();
              } else if (line.startsWith('data: ') && currentEvent) {
                try {
                  const data = JSON.parse(line.slice(6));
                  // Map to StreamEvent format and process
                  switch (currentEvent) {
                    case 'agent_status':
                      processStreamEvent({
                        type: 'agent_status',
                        agentId: data.agentId,
                        status: data.status,
                        action: data.action,
                      });
                      break;
                    case 'agent_thinking':
                      processStreamEvent({
                        type: 'agent_thinking',
                        agentId: data.agentId,
                        thought: data.thought,
                      });
                      break;
                    case 'workflow_update':
                      processStreamEvent({
                        type: 'workflow_update',
                        nodes: data.nodes,
                        edges: data.edges,
                      });
                      break;
                    case 'message':
                      processStreamEvent({
                        type: 'message',
                        content: data.content,
                        agentId: data.agentId,
                      });
                      break;
                    case 'ui_component':
                      processStreamEvent({
                        type: 'ui_component',
                        componentName: data.componentName,
                        props: data.props,
                      });
                      break;
                    case 'mission_complete':
                      processStreamEvent({ type: 'mission_complete' });
                      break;
                  }
                } catch (e) {
                  console.warn('Failed to parse SSE data:', e);
                }
                currentEvent = '';
              }
            }
          }
        } catch (error) {
          console.error('Stream processing error:', error);
        }
      };

      processStream();
      return true;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [startMission, processStreamEvent]);

  return { start, executeSaved, isLoading, error };
}

