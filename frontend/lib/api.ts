/**
 * FlagPilot API Client
 * Connects frontend to backend API
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types
export interface Agent {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
  status: "active" | "inactive";
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  agent_id?: string;
}

export interface AnalyzeRequest {
  agent_id: string;
  content: string;
  context?: Record<string, unknown>;
  files?: { name: string; content: string; type: string }[];
}

export interface AnalyzeResponse {
  response: string;
  agent_id: string;
  analysis?: Record<string, unknown>;
  suggestions?: string[];
  confidence?: number;
}

export interface TeamRunRequest {
  task: string;
  context?: Record<string, unknown>;
}

export interface TeamRunResponse {
  result: string;
  agents_used: string[];
  steps: { agent: string; action: string; result: string }[];
}

// API Functions
export async function checkHealth(): Promise<{ status: string; version: string }> {
  const res = await fetch(`${API_URL}/health`);
  if (!res.ok) throw new Error("Backend health check failed");
  return res.json();
}

export async function getAgents(): Promise<Agent[]> {
  const res = await fetch(`${API_URL}/api/v1/agents`);
  if (!res.ok) throw new Error("Failed to fetch agents");
  return res.json();
}

export async function getAgent(agentId: string): Promise<Agent> {
  const res = await fetch(`${API_URL}/api/v1/agents/${agentId}`);
  if (!res.ok) throw new Error("Failed to fetch agent");
  return res.json();
}

export async function analyzeWithAgent(
  agentId: string,
  request: AnalyzeRequest
): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_URL}/api/v1/agents/${agentId}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) throw new Error("Analysis failed");
  return res.json();
}

export async function runTeamTask(request: TeamRunRequest): Promise<TeamRunResponse> {
  const res = await fetch(`${API_URL}/api/v1/team/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) throw new Error("Team task failed");
  return res.json();
}

export async function getTeamCapabilities(): Promise<{ capabilities: string[] }> {
  const res = await fetch(`${API_URL}/api/v1/team/capabilities`);
  if (!res.ok) throw new Error("Failed to fetch team capabilities");
  return res.json();
}

// Streaming chat with agent
export async function* streamChatWithAgent(
  agentId: string,
  message: string,
  context?: Record<string, unknown>
): AsyncGenerator<string> {
  const res = await fetch(`${API_URL}/api/v1/agents/${agentId}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, context }),
  });

  if (!res.ok) throw new Error("Chat stream failed");
  if (!res.body) throw new Error("No response body");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      // Handle SSE format
      const lines = chunk.split("\n");
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[DONE]") return;
          try {
            const parsed = JSON.parse(data);
            if (parsed.content) yield parsed.content;
          } catch {
            yield data;
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

// File upload to MinIO
export async function uploadFile(file: File): Promise<{ url: string; key: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_URL}/api/v1/files/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error("File upload failed");
  return res.json();
}

// RAG query
export async function queryRAG(
  query: string,
  options?: { top_k?: number; threshold?: number }
): Promise<{ results: { content: string; score: number; source: string }[] }> {
  const res = await fetch(`${API_URL}/api/v1/rag/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, ...options }),
  });

  if (!res.ok) throw new Error("RAG query failed");
  return res.json();
}

// RAG document upload
export interface DocumentUploadRequest {
  userId: string;
  documentType: string;
  description?: string;
}

export interface DocumentUploadResponse {
  id: string;
  name: string;
  type: string;
  url: string;
  embedding_status: "pending" | "completed" | "failed";
}

export async function uploadDocumentToRAG(
  file: File,
  metadata: DocumentUploadRequest
): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("user_id", metadata.userId);
  formData.append("document_type", metadata.documentType);
  if (metadata.description) {
    formData.append("description", metadata.description);
  }

  const res = await fetch(`${API_URL}/api/v1/rag/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error("Document upload failed");
  return res.json();
}

// ================================
// MinIO Presigned URL Upload Flow
// ================================

export interface PresignedUploadResponse {
  upload_url: string;
  download_url: string;
  object_key: string;
  expires_in: number;
}

/**
 * Get a presigned URL for direct upload to MinIO
 */
export async function getPresignedUploadUrl(
  filename: string,
  contentType: string,
  projectId?: string
): Promise<PresignedUploadResponse> {
  const res = await fetch(`${API_URL}/api/v1/files/upload-url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      filename,
      content_type: contentType,
      project_id: projectId,
    }),
  });

  if (!res.ok) throw new Error("Failed to get upload URL");
  return res.json();
}

/**
 * Upload file directly to MinIO using presigned URL
 * This bypasses the server for efficient uploads
 */
export async function uploadToMinIO(
  file: File,
  uploadUrl: string,
  onProgress?: (percent: number) => void
): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener("progress", (event) => {
      if (event.lengthComputable && onProgress) {
        const percent = Math.round((event.loaded / event.total) * 100);
        onProgress(percent);
      }
    });

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve();
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`));
      }
    });

    xhr.addEventListener("error", () => reject(new Error("Upload failed")));
    xhr.addEventListener("abort", () => reject(new Error("Upload aborted")));

    xhr.open("PUT", uploadUrl);
    xhr.setRequestHeader("Content-Type", file.type);
    xhr.send(file);
  });
}

// ================================
// Vectorization (Personal Vault & Global Wisdom)
// ================================

export type VectorNamespace = "personal_vault" | "global_wisdom";

export interface VectorizeRequest {
  object_key: string;
  filename: string;
  document_type: string;
  description?: string;
  namespace: VectorNamespace;
}

export interface VectorizeResponse {
  success: boolean;
  document_id: string;
  chunks_created: number;
  namespace: VectorNamespace;
}

/**
 * Trigger vectorization of an uploaded file
 * Stores in either Personal Vault (private) or Global Wisdom (shared)
 */
export async function vectorizeDocument(
  request: VectorizeRequest
): Promise<VectorizeResponse> {
  const res = await fetch(`${API_URL}/api/v1/moat/vectorize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!res.ok) throw new Error("Vectorization failed");
  return res.json();
}

/**
 * Complete file upload flow:
 * 1. Get presigned URL from backend
 * 2. Upload directly to MinIO
 * 3. Trigger vectorization
 */
export async function uploadAndVectorize(
  file: File,
  options: {
    documentType: string;
    description?: string;
    namespace?: VectorNamespace;
    onProgress?: (percent: number) => void;
  }
): Promise<{
  objectKey: string;
  downloadUrl: string;
  vectorized: boolean;
  documentId?: string;
}> {
  // Step 1: Get presigned upload URL
  const presigned = await getPresignedUploadUrl(file.name, file.type);

  // Step 2: Upload directly to MinIO
  await uploadToMinIO(file, presigned.upload_url, options.onProgress);

  // Step 3: Trigger vectorization
  let vectorized = false;
  let documentId: string | undefined;

  try {
    const result = await vectorizeDocument({
      object_key: presigned.object_key,
      filename: file.name,
      document_type: options.documentType,
      description: options.description,
      namespace: options.namespace || "personal_vault",
    });
    vectorized = result.success;
    documentId = result.document_id;
  } catch (e) {
    console.warn("Vectorization failed, file uploaded:", e);
  }

  return {
    objectKey: presigned.object_key,
    downloadUrl: presigned.download_url,
    vectorized,
    documentId,
  };
}

// Streaming team task
export async function* streamTeamTask(
  task: string,
  context?: Record<string, unknown>,
  agents?: string[]
): AsyncGenerator<{ type: string; content: string; agent?: string }> {
  const res = await fetch(`${API_URL}/api/v1/team/run/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task, context, agents }),
  });

  if (!res.ok) throw new Error("Team task stream failed");
  if (!res.body) throw new Error("No response body");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split("\n");

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[DONE]") return;
          try {
            const parsed = JSON.parse(data);
            yield parsed;
          } catch {
            yield { type: "text", content: data };
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

// Tools
export async function listTools(): Promise<{ tools: { name: string; description: string }[] }> {
  const res = await fetch(`${API_URL}/api/v1/tools`);
  if (!res.ok) throw new Error("Failed to fetch tools");
  return res.json();
}

export async function executeTool(
  toolName: string,
  params: Record<string, unknown>
): Promise<{ result: unknown }> {
  const res = await fetch(`${API_URL}/api/v1/tools/${toolName}/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });

  if (!res.ok) throw new Error("Tool execution failed");
  return res.json();
}

// Credits/Usage (mock for now - integrate with billing later)
export interface UsageStats {
  credits_used: number;
  credits_remaining: number;
  total_requests: number;
  reset_date: string;
}

export async function getUsageStats(): Promise<UsageStats> {
  // Mock implementation - replace with actual API when billing is set up
  return {
    credits_used: 0,
    credits_remaining: 7.5,
    total_requests: 0,
    reset_date: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
  };
}

// ================================
// Feedback / RLHF
// ================================

export interface FeedbackRequest {
  workflow_id: string;
  rating: number;
  comment?: string;
  workflow_type?: string;
  agents_used?: string[];
}

export interface FeedbackResponse {
  success: boolean;
  stored_in_global_wisdom: boolean;
  message: string;
}

/**
 * Submit feedback on a workflow for RLHF
 * High ratings (4+) are stored in Global Wisdom
 */
export async function submitFeedback(
  request: FeedbackRequest
): Promise<FeedbackResponse> {
  const res = await fetch(`${API_URL}/api/v1/feedback/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!res.ok) throw new Error("Feedback submission failed");
  return res.json();
}

/**
 * Quick thumbs up for a workflow
 */
export async function thumbsUp(workflowId: string): Promise<FeedbackResponse> {
  const res = await fetch(`${API_URL}/api/v1/feedback/thumbs-up/${workflowId}`, {
    method: "POST",
  });

  if (!res.ok) throw new Error("Feedback submission failed");
  return res.json();
}

/**
 * Quick thumbs down for a workflow
 */
export async function thumbsDown(workflowId: string): Promise<FeedbackResponse> {
  const res = await fetch(`${API_URL}/api/v1/feedback/thumbs-down/${workflowId}`, {
    method: "POST",
  });

  if (!res.ok) throw new Error("Feedback submission failed");
  return res.json();
}

// ================================
// Custom Workflows
// ================================

export interface WorkflowDefinition {
  nodes: Array<{
    id: string;
    type: string;
    position: { x: number; y: number };
    data: Record<string, unknown>;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
  }>;
}

export interface WorkflowCreate {
  name: string;
  description?: string;
  definition: WorkflowDefinition;
  is_public?: boolean;
  tags?: string[];
}

export interface Workflow {
  id: string;
  name: string;
  description: string | null;
  definition: WorkflowDefinition;
  is_public: boolean;
  tags: string[] | null;
  created_at: string;
  updated_at: string;
}

/**
 * List user's custom workflows
 */
export async function listWorkflows(): Promise<Workflow[]> {
  const res = await fetch(`${API_URL}/api/v1/workflows`);
  if (!res.ok) throw new Error("Failed to fetch workflows");
  return res.json();
}

/**
 * Create a new custom workflow
 */
export async function createWorkflow(workflow: WorkflowCreate): Promise<Workflow> {
  const res = await fetch(`${API_URL}/api/v1/workflows`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(workflow),
  });

  if (!res.ok) throw new Error("Failed to create workflow");
  return res.json();
}

/**
 * Get a specific workflow
 */
export async function getWorkflow(workflowId: string): Promise<Workflow> {
  const res = await fetch(`${API_URL}/api/v1/workflows/${workflowId}`);
  if (!res.ok) throw new Error("Failed to fetch workflow");
  return res.json();
}

/**
 * Update a workflow
 */
export async function updateWorkflow(
  workflowId: string,
  updates: Partial<WorkflowCreate>
): Promise<Workflow> {
  const res = await fetch(`${API_URL}/api/v1/workflows/${workflowId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });

  if (!res.ok) throw new Error("Failed to update workflow");
  return res.json();
}

/**
 * Delete a workflow
 */
export async function deleteWorkflow(workflowId: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/workflows/${workflowId}`, {
    method: "DELETE",
  });

  if (!res.ok) throw new Error("Failed to delete workflow");
}

// Export API URL for direct use if needed
export { API_URL };


