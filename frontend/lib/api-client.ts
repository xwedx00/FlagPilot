/**
 * FlagPilot API Client
 * 
 * Connects the Next.js frontend to the Python/FastAPI backend.
 * Handles authentication, SSE streaming, and REST endpoints.
 */

import { StreamEvent, useMissionStore, AgentId } from '@/stores/mission-store';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Get authentication headers from Better Auth session
 */
async function getAuthHeaders(): Promise<HeadersInit> {
  // The session token is stored in cookies by Better Auth
  return {
    'Content-Type': 'application/json',
    // Cookie will be sent automatically with credentials: 'include'
  };
}

/**
 * Base fetch wrapper with auth and error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = await getAuthHeaders();

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: { ...headers, ...options.headers },
    credentials: 'include', // Send cookies for session auth
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

// =============================================================================
// Mission API
// =============================================================================

export interface CreateMissionRequest {
  title: string;
  description?: string;
  projectId?: string;
}

export interface Mission {
  id: string;
  title: string;
  description?: string;
  status: 'active' | 'completed' | 'paused' | 'failed';
  createdAt: string;
  updatedAt: string;
}

export const missionApi = {
  /**
   * Create a new mission
   */
  create: async (data: CreateMissionRequest): Promise<Mission> => {
    return apiFetch<Mission>('/api/v1/missions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get all missions for the current user
   */
  list: async (): Promise<Mission[]> => {
    return apiFetch<Mission[]>('/api/v1/missions');
  },

  /**
   * Get a specific mission by ID
   */
  get: async (id: string): Promise<Mission> => {
    return apiFetch<Mission>(`/api/v1/missions/${id}`);
  },

  /**
   * Delete a mission
   */
  delete: async (id: string): Promise<void> => {
    await apiFetch(`/api/v1/missions/${id}`, { method: 'DELETE' });
  },
};

// =============================================================================
// Workflow API with SSE Streaming
// =============================================================================

export interface StartWorkflowRequest {
  missionId: string;
  prompt: string;
  context?: {
    fileIds?: string[];
    privacyMode?: boolean;
  };
}

export const workflowApi = {
  /**
   * Start a workflow and stream events via SSE
   */
  start: async (
    data: StartWorkflowRequest,
    onEvent: (event: StreamEvent) => void,
    onError?: (error: Error) => void
  ): Promise<() => void> => {
    const response = await fetch(`${API_BASE_URL}/api/workflow/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      credentials: 'include',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `Workflow Error: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    // Process SSE stream
    const processStream = async () => {
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const eventData = JSON.parse(line.slice(6));
                onEvent(eventData);
              } catch (e) {
                console.error('Failed to parse SSE event:', e);
              }
            }
          }
        }
      } catch (error) {
        onError?.(error as Error);
      }
    };

    processStream();

    // Return cleanup function
    return () => {
      reader.cancel();
    };
  },

  /**
   * Send a follow-up message to an active workflow
   */
  sendMessage: async (
    missionId: string,
    message: string
  ): Promise<void> => {
    await apiFetch(`/api/workflow/${missionId}/message`, {
      method: 'POST',
      body: JSON.stringify({ content: message }),
    });
  },

  /**
   * Cancel an active workflow
   */
  cancel: async (missionId: string): Promise<void> => {
    await apiFetch(`/api/workflow/${missionId}/cancel`, {
      method: 'POST',
    });
  },
};

// =============================================================================
// Agent API
// =============================================================================

export interface AgentInfo {
  id: string;
  name: string;
  role: string;
  description: string;
  squad: string;
  status: 'idle' | 'busy' | 'offline';
}

export const agentApi = {
  /**
   * Get all available agents
   */
  list: async (): Promise<AgentInfo[]> => {
    return apiFetch<AgentInfo[]>('/api/v1/agents');
  },

  /**
   * Get agent status
   */
  getStatus: async (agentId: string): Promise<{ status: string; currentTask?: string }> => {
    return apiFetch(`/api/v1/agents/${agentId}/status`);
  },
};

// =============================================================================
// Files API (Data Moat)
// =============================================================================

export interface VaultFile {
  id: string;
  filename: string;
  contentType: string;
  sizeBytes: number;
  securityLevel: 'private' | 'public';
  isVectorized: boolean;
  hasPII: boolean;
  createdAt: string;
  presignedUrl?: string;
}

export interface UploadRequest {
  filename: string;
  contentType: string;
}

export interface UploadResponse {
  fileId: string;
  presignedUrl: string;
}

export const filesApi = {
  /**
   * List all files in the user's Data Moat
   */
  list: async (): Promise<VaultFile[]> => {
    return apiFetch<VaultFile[]>('/api/v1/files/list');
  },

  /**
   * Get a presigned URL for uploading a file
   */
  getUploadUrl: async (data: UploadRequest): Promise<UploadResponse> => {
    return apiFetch<UploadResponse>('/api/v1/files/upload-url', {
      method: 'POST',
      body: JSON.stringify({ filename: data.filename, content_type: data.contentType }),
    });
  },

  /**
   * Get a presigned URL for downloading a file
   */
  getDownloadUrl: async (fileId: string): Promise<{ url: string }> => {
    return apiFetch(`/api/v1/files/download-url/${fileId}`);
  },

  /**
   * Delete a file from the Data Moat
   */
  delete: async (fileId: string): Promise<void> => {
    await apiFetch(`/api/v1/files/${fileId}`, { method: 'DELETE' });
  },

  /**
   * Trigger vectorization of a file
   */
  vectorize: async (fileId: string): Promise<void> => {
    await apiFetch(`/api/v1/moat/ingest`, {
      method: 'POST',
      body: JSON.stringify({ file_id: fileId }),
    });
  },
};

// =============================================================================
// Credits API
// =============================================================================

export interface CreditBalance {
  current: number;
  total: number;
  usageThisMonth: number;
}

export interface CreditTransaction {
  id: string;
  amount: number;
  description: string;
  agentId?: string;
  createdAt: string;
}

export const creditsApi = {
  /**
   * Get current credit balance
   */
  getBalance: async (): Promise<CreditBalance> => {
    return apiFetch<CreditBalance>('/api/v1/credits/balance');
  },

  /**
   * Get credit usage history
   */
  getHistory: async (limit = 50): Promise<CreditTransaction[]> => {
    return apiFetch<CreditTransaction[]>(`/api/v1/credits/history?limit=${limit}`);
  },

  /**
   * Initiate credit purchase (returns Polar.sh checkout URL)
   */
  purchase: async (amount: number): Promise<{ checkoutUrl: string }> => {
    return apiFetch('/api/v1/credits/purchase', {
      method: 'POST',
      body: JSON.stringify({ amount }),
    });
  },
};

// =============================================================================
// User API
// =============================================================================

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
  plan: 'free' | 'hobby' | 'pro' | 'agency';
  onboardingCompleted: boolean;
}

export const userApi = {
  /**
   * Get current user profile
   */
  getProfile: async (): Promise<UserProfile> => {
    return apiFetch<UserProfile>('/api/v1/user/profile');
  },

  /**
   * Update user profile
   */
  updateProfile: async (data: Partial<UserProfile>): Promise<UserProfile> => {
    return apiFetch<UserProfile>('/api/v1/user/profile', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * Export user data (GDPR)
   */
  exportData: async (): Promise<{ downloadUrl: string }> => {
    return apiFetch('/api/v1/user/export');
  },

  /**
   * Delete user account (GDPR)
   */
  deleteAccount: async (): Promise<void> => {
    await apiFetch('/api/v1/user', { method: 'DELETE' });
  },
};

// =============================================================================
// Hook for real-time workflow connection
// =============================================================================

/**
 * Connect to a mission's workflow stream and process events
 */
export function connectToWorkflow(
  missionId: string,
  prompt: string,
  options?: {
    fileIds?: string[];
    privacyMode?: boolean;
    onComplete?: () => void;
    onError?: (error: Error) => void;
  }
): () => void {
  const { processStreamEvent } = useMissionStore.getState();

  let cleanup: (() => void) | undefined;

  workflowApi
    .start(
      {
        missionId,
        prompt,
        context: {
          fileIds: options?.fileIds,
          privacyMode: options?.privacyMode,
        },
      },
      (event) => {
        processStreamEvent(event);

        if (event.type === 'mission_complete') {
          options?.onComplete?.();
        }
      },
      options?.onError
    )
    .then((cleanupFn) => {
      cleanup = cleanupFn;
    })
    .catch((error) => {
      options?.onError?.(error);
    });

  return () => {
    cleanup?.();
  };
}
