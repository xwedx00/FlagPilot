/**
 * React Hooks for FlagPilot API
 * 
 * These hooks connect the frontend to the backend APIs
 * and handle loading states, errors, and caching.
 */

import { useState, useEffect, useCallback } from 'react';
import {
  missionApi,
  filesApi,
  creditsApi,
  userApi,
  workflowApi,
  type Mission,
  type VaultFile,
  type CreditBalance,
  type CreditTransaction,
  type UserProfile,
} from '@/lib/api-client';
import { useMissionStore, type StreamEvent } from '@/stores/mission-store';
import { toast } from 'sonner';

// =============================================================================
// Missions Hook
// =============================================================================

export interface UseMissionsReturn {
  missions: Mission[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  createMission: (title: string, description?: string) => Promise<Mission | null>;
  deleteMission: (id: string) => Promise<void>;
}

export function useMissions(): UseMissionsReturn {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchMissions = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await missionApi.list();
      setMissions(data);
    } catch (err) {
      // Gracefully handle backend unavailability
      console.warn('Failed to fetch missions (backend may be unavailable):', err);
      setMissions([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createMission = useCallback(async (title: string, description?: string) => {
    try {
      const newMission = await missionApi.create({ title, description });
      setMissions((prev) => [newMission, ...prev]);
      toast.success('Mission created');
      return newMission;
    } catch (err) {
      toast.error('Failed to create mission');
      console.error('Failed to create mission:', err);
      return null;
    }
  }, []);

  const deleteMission = useCallback(async (id: string) => {
    try {
      await missionApi.delete(id);
      setMissions((prev) => prev.filter((m) => m.id !== id));
      toast.success('Mission deleted');
    } catch (err) {
      toast.error('Failed to delete mission');
      console.error('Failed to delete mission:', err);
    }
  }, []);

  useEffect(() => {
    fetchMissions();
  }, [fetchMissions]);

  return {
    missions,
    isLoading,
    error,
    refetch: fetchMissions,
    createMission,
    deleteMission,
  };
}

// =============================================================================
// Files Hook (Data Moat)
// =============================================================================

export interface UseFilesReturn {
  files: VaultFile[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  uploadFile: (file: File) => Promise<VaultFile | null>;
  deleteFile: (id: string) => Promise<void>;
  downloadFile: (id: string) => Promise<void>;
  vectorizeFile: (id: string) => Promise<void>;
}

export function useFiles(): UseFilesReturn {
  const [files, setFiles] = useState<VaultFile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchFiles = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await filesApi.list();
      // Handle both array response and {files: []} response from backend
      setFiles(Array.isArray(data) ? data : []);
    } catch (err) {
      // Gracefully handle backend unavailability
      console.warn('Failed to fetch files (backend may be unavailable):', err);
      setFiles([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const uploadFile = useCallback(async (file: File): Promise<VaultFile | null> => {
    try {
      // Get presigned URL
      const { fileId, presignedUrl } = await filesApi.getUploadUrl({
        filename: file.name,
        contentType: file.type,
      });

      // Upload file to MinIO
      await fetch(presignedUrl, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type,
        },
      });

      // Create local file entry
      const newFile: VaultFile = {
        id: fileId,
        filename: file.name,
        contentType: file.type,
        sizeBytes: file.size,
        securityLevel: 'private',
        isVectorized: false,
        hasPII: false,
        createdAt: new Date().toISOString(),
      };

      setFiles((prev) => [newFile, ...prev]);
      toast.success(`Uploaded ${file.name}`);
      return newFile;
    } catch (err) {
      toast.error(`Failed to upload ${file.name}`);
      console.error('Failed to upload file:', err);
      return null;
    }
  }, []);

  const deleteFile = useCallback(async (id: string) => {
    try {
      await filesApi.delete(id);
      setFiles((prev) => prev.filter((f) => f.id !== id));
      toast.success('File deleted');
    } catch (err) {
      toast.error('Failed to delete file');
      console.error('Failed to delete file:', err);
    }
  }, []);

  const downloadFile = useCallback(async (id: string) => {
    try {
      const { url } = await filesApi.getDownloadUrl(id);
      window.open(url, '_blank');
    } catch (err) {
      toast.error('Failed to download file');
      console.error('Failed to download file:', err);
    }
  }, []);

  const vectorizeFile = useCallback(async (id: string) => {
    try {
      await filesApi.vectorize(id);
      setFiles((prev) =>
        prev.map((f) => (f.id === id ? { ...f, isVectorized: true } : f))
      );
      toast.success('File vectorized for RAG');
    } catch (err) {
      toast.error('Failed to vectorize file');
      console.error('Failed to vectorize file:', err);
    }
  }, []);

  useEffect(() => {
    fetchFiles();
  }, [fetchFiles]);

  return {
    files,
    isLoading,
    error,
    refetch: fetchFiles,
    uploadFile,
    deleteFile,
    downloadFile,
    vectorizeFile,
  };
}

// =============================================================================
// Credits Hook
// =============================================================================

export interface UseCreditsReturn {
  balance: CreditBalance | null;
  history: CreditTransaction[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  purchase: (amount: number) => Promise<void>;
}

export function useCredits(): UseCreditsReturn {
  const [balance, setBalance] = useState<CreditBalance | null>(null);
  const [history, setHistory] = useState<CreditTransaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchCredits = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const [balanceData, historyData] = await Promise.all([
        creditsApi.getBalance(),
        creditsApi.getHistory(),
      ]);
      setBalance(balanceData);
      setHistory(historyData);
    } catch (err) {
      // Gracefully handle backend unavailability - use defaults
      console.warn('Failed to fetch credits (backend may be unavailable):', err);
      setBalance({ current: 100, total: 100, usageThisMonth: 0 });
      setHistory([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const purchase = useCallback(async (amount: number) => {
    try {
      const { checkoutUrl } = await creditsApi.purchase(amount);
      window.open(checkoutUrl, '_blank');
    } catch (err) {
      toast.error('Failed to initiate purchase');
      console.error('Failed to purchase credits:', err);
    }
  }, []);

  useEffect(() => {
    fetchCredits();
  }, [fetchCredits]);

  return {
    balance,
    history,
    isLoading,
    error,
    refetch: fetchCredits,
    purchase,
  };
}

// =============================================================================
// User Profile Hook
// =============================================================================

export interface UseUserProfileReturn {
  profile: UserProfile | null;
  isLoading: boolean;
  error: Error | null;
  updateProfile: (data: Partial<UserProfile>) => Promise<void>;
  exportData: () => Promise<void>;
  deleteAccount: () => Promise<void>;
}

export function useUserProfile(): UseUserProfileReturn {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchProfile = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await userApi.getProfile();
      setProfile(data);
    } catch (err) {
      setError(err as Error);
      console.error('Failed to fetch profile:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateProfile = useCallback(async (data: Partial<UserProfile>) => {
    try {
      const updated = await userApi.updateProfile(data);
      setProfile(updated);
      toast.success('Profile updated');
    } catch (err) {
      toast.error('Failed to update profile');
      console.error('Failed to update profile:', err);
    }
  }, []);

  const exportData = useCallback(async () => {
    try {
      const { downloadUrl } = await userApi.exportData();
      window.open(downloadUrl, '_blank');
      toast.success('Data export ready');
    } catch (err) {
      toast.error('Failed to export data');
      console.error('Failed to export data:', err);
    }
  }, []);

  const deleteAccount = useCallback(async () => {
    try {
      await userApi.deleteAccount();
      toast.success('Account deleted');
    } catch (err) {
      toast.error('Failed to delete account');
      console.error('Failed to delete account:', err);
    }
  }, []);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  return {
    profile,
    isLoading,
    error,
    updateProfile,
    exportData,
    deleteAccount,
  };
}

// =============================================================================
// Chat/Workflow Hook
// =============================================================================

export interface UseChatReturn {
  sendMessage: (message: string, attachments?: File[]) => Promise<void>;
  isStreaming: boolean;
  cancelWorkflow: () => void;
}

export function useChat(missionId: string): UseChatReturn {
  const [isStreaming, setIsStreaming] = useState(false);
  const [cleanup, setCleanup] = useState<(() => void) | null>(null);

  const { addMessage, processStreamEvent } = useMissionStore();

  const sendMessage = useCallback(async (message: string, attachments?: File[]) => {
    // Add user message to store
    addMessage({
      role: 'user',
      content: message,
    });

    // Upload attachments first if any
    let fileIds: string[] = [];
    if (attachments && attachments.length > 0) {
      for (const file of attachments) {
        try {
          const { fileId, presignedUrl } = await filesApi.getUploadUrl({
            filename: file.name,
            contentType: file.type,
          });
          await fetch(presignedUrl, {
            method: 'PUT',
            body: file,
            headers: { 'Content-Type': file.type },
          });
          fileIds.push(fileId);
        } catch (err) {
          console.error('Failed to upload attachment:', err);
        }
      }
    }

    // Start workflow stream
    setIsStreaming(true);

    try {
      const cleanupFn = await workflowApi.start(
        {
          missionId,
          prompt: message,
          context: { fileIds },
        },
        (event: StreamEvent) => {
          processStreamEvent(event);
        },
        (error) => {
          console.error('Workflow error:', error);
          toast.error('Workflow error: ' + error.message);
          setIsStreaming(false);
        }
      );
      setCleanup(() => cleanupFn);
    } catch (err) {
      toast.error('Failed to start workflow');
      console.error('Failed to start workflow:', err);
      setIsStreaming(false);
    }
  }, [missionId, addMessage, processStreamEvent]);

  const cancelWorkflow = useCallback(() => {
    cleanup?.();
    setIsStreaming(false);
    workflowApi.cancel(missionId).catch(console.error);
  }, [cleanup, missionId]);

  return {
    sendMessage,
    isStreaming,
    cancelWorkflow,
  };
}

// =============================================================================
// Workflow History Hook
// =============================================================================

import {
  historyApi,
  workflowTemplateApi,
  type WorkflowExecution,
  type WorkflowTemplate,
  type CreateWorkflowTemplateRequest,
} from '@/lib/api-client';

export interface UseWorkflowHistoryReturn {
  executions: WorkflowExecution[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useWorkflowHistory(): UseWorkflowHistoryReturn {
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchHistory = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await historyApi.list();
      setExecutions(data);
    } catch (err) {
      console.warn('Failed to fetch workflow history:', err);
      setExecutions([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return {
    executions,
    isLoading,
    error,
    refetch: fetchHistory,
  };
}

// =============================================================================
// Workflow Templates Hook
// =============================================================================

export interface UseWorkflowTemplatesReturn {
  templates: WorkflowTemplate[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  createTemplate: (data: CreateWorkflowTemplateRequest) => Promise<WorkflowTemplate | null>;
  updateTemplate: (id: string, data: Partial<CreateWorkflowTemplateRequest>) => Promise<WorkflowTemplate | null>;
  deleteTemplate: (id: string) => Promise<void>;
  executeTemplate: (id: string, context?: { variables?: Record<string, string>; fileIds?: string[] }) => Promise<string | null>;
}

export function useWorkflowTemplates(): UseWorkflowTemplatesReturn {
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchTemplates = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await workflowTemplateApi.list();
      setTemplates(data);
    } catch (err) {
      console.warn('Failed to fetch workflow templates:', err);
      setTemplates([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createTemplate = useCallback(async (data: CreateWorkflowTemplateRequest) => {
    try {
      const newTemplate = await workflowTemplateApi.create(data);
      setTemplates((prev) => [newTemplate, ...prev]);
      toast.success('Workflow template saved');
      return newTemplate;
    } catch (err) {
      toast.error('Failed to save workflow template');
      console.error('Failed to create template:', err);
      return null;
    }
  }, []);

  const updateTemplate = useCallback(async (id: string, data: Partial<CreateWorkflowTemplateRequest>) => {
    try {
      const updated = await workflowTemplateApi.update(id, data);
      setTemplates((prev) => prev.map((t) => (t.id === id ? updated : t)));
      toast.success('Workflow template updated');
      return updated;
    } catch (err) {
      toast.error('Failed to update workflow template');
      console.error('Failed to update template:', err);
      return null;
    }
  }, []);

  const deleteTemplate = useCallback(async (id: string) => {
    try {
      await workflowTemplateApi.delete(id);
      setTemplates((prev) => prev.filter((t) => t.id !== id));
      toast.success('Workflow template deleted');
    } catch (err) {
      toast.error('Failed to delete workflow template');
      console.error('Failed to delete template:', err);
    }
  }, []);

  const executeTemplate = useCallback(async (id: string, context?: { variables?: Record<string, string>; fileIds?: string[] }) => {
    try {
      const { executionId } = await workflowTemplateApi.execute(id, context);
      toast.success('Workflow started');
      return executionId;
    } catch (err) {
      toast.error('Failed to start workflow');
      console.error('Failed to execute template:', err);
      return null;
    }
  }, []);

  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  return {
    templates,
    isLoading,
    error,
    refetch: fetchTemplates,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    executeTemplate,
  };
}

// Export all hooks
export {
  type Mission,
  type VaultFile,
  type CreditBalance,
  type CreditTransaction,
  type UserProfile,
  type WorkflowExecution,
  type WorkflowTemplate,
};

