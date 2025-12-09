/**
 * WebSocket Client for Glass Box Streaming
 * =========================================
 * Connects to backend WebSocket for real-time agent state updates.
 * Replaces SSE EventSource with bidirectional WebSocket.
 */

import { useMissionStore, type StreamEvent, type AgentId, type AgentStatus, type AgentNode } from '@/stores/mission-store';
import type { Edge } from '@xyflow/react';

// Backend WebSocket base URL
const WS_BASE_URL = typeof window !== 'undefined'
    ? (process.env.NEXT_PUBLIC_API_URL?.replace('http', 'ws') || 'ws://localhost:8000')
    : 'ws://localhost:8000';

export interface WebSocketEvent {
    event: string;
    data: Record<string, unknown>;
    timestamp: string;
}

export interface WebSocketClientOptions {
    onConnect?: () => void;
    onDisconnect?: () => void;
    onError?: (error: Error) => void;
}

export class WebSocketClient {
    private socket: WebSocket | null = null;
    private missionId: string | null = null;
    private options: WebSocketClientOptions;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 3;

    constructor(options: WebSocketClientOptions = {}) {
        this.options = options;
    }

    /**
     * Connect to the chat WebSocket endpoint.
     * This is the main endpoint for sending messages and receiving agent updates.
     */
    connectChat(): void {
        if (this.socket?.readyState === WebSocket.OPEN) {
            this.disconnect();
        }

        const url = `${WS_BASE_URL}/api/v1/ws/chat`;
        this.socket = new WebSocket(url);
        this.setupEventListeners();
    }

    /**
     * Connect to a specific mission WebSocket endpoint.
     */
    connectMission(missionId: string, task?: string): void {
        if (this.socket?.readyState === WebSocket.OPEN) {
            this.disconnect();
        }

        this.missionId = missionId;
        let url = `${WS_BASE_URL}/api/v1/ws/mission/${missionId}`;
        if (task) {
            url += `?task=${encodeURIComponent(task)}`;
        }

        this.socket = new WebSocket(url);
        this.setupEventListeners();
    }

    /**
     * Setup WebSocket event listeners
     */
    private setupEventListeners(): void {
        if (!this.socket) return;

        const store = useMissionStore.getState();

        this.socket.onopen = () => {
            console.log('[WebSocketClient] Connected');
            this.reconnectAttempts = 0;
            this.options.onConnect?.();
        };

        this.socket.onclose = (event) => {
            console.log('[WebSocketClient] Disconnected', event.code, event.reason);
            this.options.onDisconnect?.();

            // Auto-reconnect for unexpected disconnects
            if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                setTimeout(() => {
                    if (this.missionId) {
                        this.connectMission(this.missionId);
                    }
                }, 1000 * this.reconnectAttempts);
            }
        };

        this.socket.onerror = (event) => {
            console.error('[WebSocketClient] Error:', event);
            this.options.onError?.(new Error('WebSocket connection error'));
        };

        this.socket.onmessage = (event) => {
            try {
                const wsEvent: WebSocketEvent = JSON.parse(event.data);
                this.handleEvent(wsEvent, store);
            } catch (e) {
                console.error('[WebSocketClient] Failed to parse message:', e);
            }
        };
    }

    /**
     * Handle incoming WebSocket events
     */
    private handleEvent(
        wsEvent: WebSocketEvent,
        store: ReturnType<typeof useMissionStore.getState>
    ): void {
        const { event, data } = wsEvent;

        switch (event) {
            case 'connected':
                console.log('[WebSocketClient] Mission connected:', data);
                break;

            case 'agent_status':
                store.processStreamEvent({
                    type: 'agent_status',
                    agentId: data.agentId as AgentId,
                    status: data.status as AgentStatus,
                    action: data.action as string | undefined,
                });
                break;

            case 'agent_thinking':
                store.processStreamEvent({
                    type: 'agent_thinking',
                    agentId: data.agentId as AgentId,
                    thought: data.thought as string,
                });
                break;

            case 'workflow_update':
                store.processStreamEvent({
                    type: 'workflow_update',
                    nodes: data.nodes as AgentNode[],
                    edges: data.edges as Edge[],
                });
                break;

            case 'message':
                store.processStreamEvent({
                    type: 'message',
                    content: data.content as string,
                    agentId: data.agentId as AgentId | undefined,
                });
                break;

            case 'ui_component':
                store.processStreamEvent({
                    type: 'ui_component',
                    componentName: data.componentName as string,
                    props: data.props as Record<string, unknown>,
                });
                break;

            case 'mission_complete':
                console.log('[WebSocketClient] Mission complete');
                store.processStreamEvent({ type: 'mission_complete' });
                break;

            case 'error':
                console.error('[WebSocketClient] Server error:', data.message);
                this.options.onError?.(new Error(data.message as string));
                break;

            default:
                console.log('[WebSocketClient] Unknown event:', event);
        }
    }

    /**
     * Send a message through the WebSocket
     */
    sendMessage(message: string, context?: Record<string, unknown>): void {
        if (this.socket?.readyState !== WebSocket.OPEN) {
            console.error('[WebSocketClient] Not connected');
            return;
        }

        this.socket.send(JSON.stringify({
            message,
            context: context || {},
        }));
    }

    /**
     * Send feedback for a workflow (RLHF)
     */
    sendFeedback(rating: number, workflowId?: string): void {
        if (this.socket?.readyState !== WebSocket.OPEN) {
            console.error('[WebSocketClient] Not connected');
            return;
        }

        this.socket.send(JSON.stringify({
            action: 'feedback',
            rating,
            workflow_id: workflowId,
        }));
    }

    /**
     * Cancel the current mission
     */
    cancelMission(): void {
        if (this.socket?.readyState !== WebSocket.OPEN) {
            return;
        }

        this.socket.send(JSON.stringify({
            action: 'cancel',
        }));
    }

    /**
     * Disconnect from WebSocket
     */
    disconnect(): void {
        if (this.socket) {
            this.socket.close(1000, 'Client disconnect');
            this.socket = null;
            this.missionId = null;
            console.log('[WebSocketClient] Disconnected');
        }
    }

    /**
     * Check if connected
     */
    isConnected(): boolean {
        return this.socket?.readyState === WebSocket.OPEN;
    }

    /**
     * Get current mission ID
     */
    getMissionId(): string | null {
        return this.missionId;
    }
}

// Singleton instance
let wsClientInstance: WebSocketClient | null = null;

export function getWebSocketClient(options?: WebSocketClientOptions): WebSocketClient {
    if (!wsClientInstance) {
        wsClientInstance = new WebSocketClient(options);
    }
    return wsClientInstance;
}

// React hook for WebSocket client
import { useEffect, useRef, useCallback } from 'react';

export function useWebSocketClient() {
    const clientRef = useRef<WebSocketClient | null>(null);
    const store = useMissionStore();

    useEffect(() => {
        clientRef.current = getWebSocketClient({
            onConnect: () => console.log('WebSocket connected'),
            onDisconnect: () => console.log('WebSocket disconnected'),
            onError: (error) => console.error('WebSocket error:', error),
        });

        // Connect to chat endpoint
        clientRef.current.connectChat();

        return () => {
            clientRef.current?.disconnect();
        };
    }, []);

    const sendMessage = useCallback(async (message: string, context?: Record<string, unknown>) => {
        if (!clientRef.current) return;

        // Ensure connected
        if (!clientRef.current.isConnected()) {
            clientRef.current.connectChat();
            // Wait for connection
            await new Promise(resolve => setTimeout(resolve, 500));
        }

        // Initialize store
        store.startMission(message);

        // Send message
        clientRef.current.sendMessage(message, context);
    }, [store]);

    const sendFeedback = useCallback((rating: number, workflowId?: string) => {
        clientRef.current?.sendFeedback(rating, workflowId);
    }, []);

    const disconnect = useCallback(() => {
        clientRef.current?.disconnect();
    }, []);

    return {
        sendMessage,
        sendFeedback,
        disconnect,
        isConnected: clientRef.current?.isConnected() ?? false,
    };
}
