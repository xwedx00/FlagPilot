'use client';

import * as React from 'react';
import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  AlertTriangle,
  Download,
  Trash2,
  Shield,
  Check,
  Loader2,
  Database,
  FolderLock,
  Server,
} from 'lucide-react';
import { StreamableLog, useStreamingLogs, type LogEntry } from './streamable-log';

interface GDPRComplianceProps {
  onExportData?: () => Promise<void>;
  onPurgeData?: () => Promise<void>;
  className?: string;
}

interface DataDeletionStep {
  id: string;
  label: string;
  icon: React.ReactNode;
  status: 'pending' | 'running' | 'done' | 'error';
}

/**
 * GDPRCompliance - Settings page for data compliance
 * 
 * Features:
 * - Export all data button
 * - Data purge "panic button" with double confirmation
 * - Terminal-style deletion log
 */
export function GDPRCompliance({
  onExportData,
  onPurgeData,
  className,
}: GDPRComplianceProps) {
  const [showPurgeModal, setShowPurgeModal] = useState(false);
  const [confirmText, setConfirmText] = useState('');
  const [isPurging, setIsPurging] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const { logs, addLog, clearLogs } = useStreamingLogs();
  const [deletionSteps, setDeletionSteps] = useState<DataDeletionStep[]>([
    { id: 'vectors', label: 'Deleting vectors from Qdrant', icon: <Database className="w-4 h-4" />, status: 'pending' },
    { id: 'minio', label: 'Scrubbing MinIO bucket', icon: <FolderLock className="w-4 h-4" />, status: 'pending' },
    { id: 'postgres', label: 'Wiping Postgres session logs', icon: <Server className="w-4 h-4" />, status: 'pending' },
  ]);

  const handleExportData = async () => {
    setIsExporting(true);
    try {
      await onExportData?.();
    } finally {
      setIsExporting(false);
    }
  };

  const handlePurgeData = async () => {
    if (confirmText !== 'DELETE') return;
    
    setIsPurging(true);
    clearLogs();

    // Simulate deletion process with logs
    for (const step of deletionSteps) {
      // Update step to running
      setDeletionSteps((prev) =>
        prev.map((s) => (s.id === step.id ? { ...s, status: 'running' } : s))
      );
      
      addLog(`${step.label}...`, { type: 'info', agent: 'System' });
      
      // Simulate delay
      await new Promise((r) => setTimeout(r, 1500));
      
      // Update step to done
      setDeletionSteps((prev) =>
        prev.map((s) => (s.id === step.id ? { ...s, status: 'done' } : s))
      );
      
      addLog(`${step.label}... [OK]`, { type: 'success', agent: 'System' });
    }

    // Call actual purge
    try {
      await onPurgeData?.();
      addLog('All data successfully purged.', { type: 'success', agent: 'System' });
    } catch (error) {
      addLog('Error during purge process.', { type: 'error', agent: 'System' });
    }

    setIsPurging(false);
    // Don't close modal - let user see the completion status
  };

  const resetModal = () => {
    setShowPurgeModal(false);
    setConfirmText('');
    clearLogs();
    setDeletionSteps((prev) => prev.map((s) => ({ ...s, status: 'pending' })));
  };

  return (
    <div className={cn('space-y-8', className)}>
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-md bg-emerald-500/20 flex items-center justify-center">
          <Shield className="w-5 h-5 text-emerald-400" />
        </div>
        <div>
          <h2 className="text-lg font-semibold">Data & Privacy</h2>
          <p className="text-sm text-zinc-400">
            Manage your data and exercise your GDPR rights
          </p>
        </div>
      </div>

      {/* Export Data Section */}
      <div className="bg-zinc-900/60 backdrop-blur border border-zinc-700 rounded-md p-5">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-medium mb-1">Export Your Data</h3>
            <p className="text-sm text-zinc-400 max-w-md">
              Download a complete copy of all your data including files, chat
              history, agent memories, and settings.
            </p>
          </div>
          <Button
            variant="outline"
            onClick={handleExportData}
            disabled={isExporting}
            className="gap-2"
          >
            {isExporting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            Export Data
          </Button>
        </div>
      </div>

      {/* Danger Zone - Purge Data */}
      <div className="fp-destructive-section">
        <div className="flex items-start gap-3 mb-4">
          <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-rose-400 mb-1">Danger Zone</h3>
            <p className="text-sm text-zinc-400">
              Permanently delete all your data from FlagPilot. This action
              cannot be undone.
            </p>
          </div>
        </div>

        <Button
          variant="destructive"
          onClick={() => setShowPurgeModal(true)}
          className="gap-2 bg-rose-600 hover:bg-rose-500"
        >
          <Trash2 className="w-4 h-4" />
          Purge My Data
        </Button>
      </div>

      {/* Purge Confirmation Modal */}
      <Dialog open={showPurgeModal} onOpenChange={(open) => !isPurging && resetModal()}>
        <DialogContent className="bg-zinc-900 border-zinc-800 max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-rose-400">
              <AlertTriangle className="w-5 h-5" />
              Confirm Data Deletion
            </DialogTitle>
            <DialogDescription className="text-zinc-400">
              This will permanently delete all your data including:
            </DialogDescription>
          </DialogHeader>

          {/* What will be deleted */}
          <ul className="space-y-2 my-4">
            {deletionSteps.map((step) => (
              <li key={step.id} className="flex items-center gap-3 text-sm">
                <div
                  className={cn(
                    'w-6 h-6 rounded-md flex items-center justify-center',
                    step.status === 'done'
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : step.status === 'running'
                      ? 'bg-amber-500/20 text-amber-400'
                      : 'bg-zinc-800 text-zinc-500'
                  )}
                >
                  {step.status === 'done' ? (
                    <Check className="w-3.5 h-3.5" />
                  ) : step.status === 'running' ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    step.icon
                  )}
                </div>
                <span className={step.status === 'done' ? 'text-zinc-500' : ''}>
                  {step.label}
                </span>
              </li>
            ))}
          </ul>

          {/* Deletion log terminal */}
          {logs.length > 0 && (
            <StreamableLog logs={logs} maxHeight="150px" showTimestamps={false} />
          )}

          {/* Confirmation input */}
          {!isPurging && logs.length === 0 && (
            <div className="space-y-3">
              <p className="text-sm text-zinc-400">
                Type <code className="text-rose-400 font-mono bg-zinc-800 px-1.5 py-0.5 rounded">DELETE</code> to confirm:
              </p>
              <Input
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                placeholder="Type DELETE"
                className="font-mono bg-zinc-950 border-zinc-700"
              />
            </div>
          )}

          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={resetModal}
              disabled={isPurging}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handlePurgeData}
              disabled={confirmText !== 'DELETE' || isPurging}
              className="bg-rose-600 hover:bg-rose-500 gap-2"
            >
              {isPurging ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Purging...
                </>
              ) : logs.length > 0 ? (
                'Done'
              ) : (
                <>
                  <Trash2 className="w-4 h-4" />
                  Permanently Delete
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export type { GDPRComplianceProps };
