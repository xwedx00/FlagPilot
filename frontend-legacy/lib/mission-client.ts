import { useMissionStore, type StreamEvent } from '@/stores/mission-store';

// Backend API base URL
const API_BASE_URL = typeof window !== 'undefined'
  ? (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
  : 'http://localhost:8000';

export interface MissionClientOptions {
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
}

export class MissionClient {
  private eventSource: EventSource | null = null;
  private missionId: string | null = null;
  private options: MissionClientOptions;

  constructor(options: MissionClientOptions = {}) {
    this.options = options;
  }

  /**
   * Start a new mission and subscribe to its SSE stream
   */
  async startMission(title: string, description?: string): Promise<string> {
    // Create mission via backend API
    const response = await fetch(`${API_BASE_URL}/api/v1/stream/mission`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description }),
    });

    if (!response.ok) {
      throw new Error('Failed to start mission');
    }

    const data = await response.json();
    const missionId = data.id as string;
    this.missionId = missionId;

    // Subscribe to SSE stream with the task
    this.subscribeWithTask(missionId, title);

    return missionId;
  }

  /**
   * Subscribe to an existing mission's SSE stream with a task
   */
  subscribeWithTask(missionId: string, task: string): void {
    // Close existing connection if any
    this.disconnect();

    this.missionId = missionId;
    const streamUrl = `${API_BASE_URL}/api/v1/stream/mission/${missionId}?task=${encodeURIComponent(task)}`;
    this.eventSource = new EventSource(streamUrl);

    // Handle connection open
    this.eventSource.onopen = () => {
      console.log(`[MissionClient] Connected to mission: ${missionId}`);
      this.options.onConnect?.();
    };

    // Handle errors
    this.eventSource.onerror = (event) => {
      console.error('[MissionClient] SSE Error:', event);
      this.options.onError?.(new Error('SSE connection error'));
    };

    // Handle specific event types
    this.setupEventHandlers();
  }

  /**
   * Subscribe to an existing mission's SSE stream (legacy - uses generic task)
   */
  subscribe(missionId: string): void {
    this.subscribeWithTask(missionId, 'Analyze request');
  }

  /**
   * Setup handlers for different SSE event types
   */
  private setupEventHandlers(): void {
    if (!this.eventSource) return;

    const store = useMissionStore.getState();

    // Connected event
    this.eventSource.addEventListener('connected', (event) => {
      const data = JSON.parse(event.data);
      console.log('[MissionClient] Mission connected:', data);
    });

    // Agent status updates
    this.eventSource.addEventListener('agent_status', (event) => {
      const data = JSON.parse(event.data);
      store.processStreamEvent({
        type: 'agent_status',
        agentId: data.agentId,
        status: data.status,
        action: data.action,
      });
    });

    // Agent thinking
    this.eventSource.addEventListener('agent_thinking', (event) => {
      const data = JSON.parse(event.data);
      store.processStreamEvent({
        type: 'agent_thinking',
        agentId: data.agentId,
        thought: data.thought,
      });
    });

    // Workflow updates (DAG)
    this.eventSource.addEventListener('workflow_update', (event) => {
      const data = JSON.parse(event.data);
      store.processStreamEvent({
        type: 'workflow_update',
        nodes: data.nodes,
        edges: data.edges,
      });
    });

    // Messages
    this.eventSource.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      store.processStreamEvent({
        type: 'message',
        content: data.content,
        agentId: data.agentId,
      });
    });

    // UI Components
    this.eventSource.addEventListener('ui_component', (event) => {
      const data = JSON.parse(event.data);
      store.processStreamEvent({
        type: 'ui_component',
        componentName: data.componentName,
        props: data.props,
      });
    });

    // Artifacts
    this.eventSource.addEventListener('artifact', (event) => {
      const data = JSON.parse(event.data);
      store.processStreamEvent({
        type: 'artifact',
        artifact: data.artifact,
      });
    });

    // Mission complete
    this.eventSource.addEventListener('mission_complete', (event) => {
      console.log('[MissionClient] Mission complete');
      store.processStreamEvent({ type: 'mission_complete' });
      this.disconnect();
    });

    // Error
    this.eventSource.addEventListener('error', (event) => {
      try {
        const data = JSON.parse((event as MessageEvent).data);
        console.error('[MissionClient] Server error:', data.message);
        this.options.onError?.(new Error(data.message));
      } catch {
        // Generic error
      }
    });
  }

  /**
   * Disconnect from SSE stream
   */
  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
      this.missionId = null;
      this.options.onDisconnect?.();
      console.log('[MissionClient] Disconnected');
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.eventSource !== null && this.eventSource.readyState === EventSource.OPEN;
  }

  /**
   * Get current mission ID
   */
  getMissionId(): string | null {
    return this.missionId;
  }
}

// Singleton instance
let missionClientInstance: MissionClient | null = null;

export function getMissionClient(options?: MissionClientOptions): MissionClient {
  if (!missionClientInstance) {
    missionClientInstance = new MissionClient(options);
  }
  return missionClientInstance;
}

// React hook for mission client
import { useEffect, useRef, useCallback } from 'react';

export function useMissionClient() {
  const clientRef = useRef<MissionClient | null>(null);
  const store = useMissionStore();

  useEffect(() => {
    clientRef.current = getMissionClient({
      onConnect: () => console.log('Mission connected'),
      onDisconnect: () => console.log('Mission disconnected'),
      onError: (error) => console.error('Mission error:', error),
    });

    return () => {
      clientRef.current?.disconnect();
    };
  }, []);

  const startMission = useCallback(async (title: string, description?: string) => {
    if (!clientRef.current) return null;

    // Initialize store
    store.startMission(title);

    // Start mission and subscribe
    const missionId = await clientRef.current.startMission(title, description);
    return missionId;
  }, [store]);

  const subscribeMission = useCallback((missionId: string) => {
    clientRef.current?.subscribe(missionId);
  }, []);

  const disconnect = useCallback(() => {
    clientRef.current?.disconnect();
  }, []);

  return {
    startMission,
    subscribeMission,
    disconnect,
    isConnected: clientRef.current?.isConnected() ?? false,
  };
}
