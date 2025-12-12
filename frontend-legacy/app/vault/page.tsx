"use client";

import { useState } from 'react';
import {
  AppLayout,
  MoatFileCard,
  MoatDropzone,
  type SecurityLevel,
} from '@/components/flagpilot';
import { authClient } from '@/lib/auth-client';
import { redirect } from 'next/navigation';
import { Loader } from '@/components/ui/loader';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { 
  Search, 
  Grid3X3, 
  List, 
  Upload, 
  Download, 
  FileText,
  FileImage,
  Shield,
  Sparkles,
  AlertTriangle,
  X,
  ExternalLink,
} from 'lucide-react';
import { useFiles, useCredits, type VaultFile } from '@/hooks/use-api';

// Format file size helper
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export default function VaultPage() {
  const { data: session, isPending: sessionPending } = authClient.useSession();
  
  // API hooks - fetches real data from backend
  const { 
    files, 
    isLoading: filesLoading, 
    uploadFile, 
    deleteFile, 
    downloadFile,
    vectorizeFile,
  } = useFiles();
  const { balance, isLoading: creditsLoading } = useCredits();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [activeTab, setActiveTab] = useState('all');
  const [isDragging, setIsDragging] = useState(false);
  const [previewFile, setPreviewFile] = useState<VaultFile | null>(null);

  // Filter files based on search and tab
  const filteredFiles = files.filter((file) => {
    const matchesSearch = file.filename.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTab =
      activeTab === 'all' ||
      (activeTab === 'private' && file.securityLevel === 'private') ||
      (activeTab === 'vectorized' && file.isVectorized);
    return matchesSearch && matchesTab;
  });

  // Handle file drop - upload to MinIO
  const handleFileDrop = async (droppedFiles: File[]) => {
    setIsDragging(false);
    for (const file of droppedFiles) {
      await uploadFile(file);
    }
  };

  // Handle file deletion
  const handleDelete = async (fileId: string) => {
    await deleteFile(fileId);
  };

  // Handle file download
  const handleDownload = async (fileId: string) => {
    await downloadFile(fileId);
  };

  if (sessionPending || filesLoading || creditsLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-zinc-950">
        <Loader variant="dots" size="lg" />
      </div>
    );
  }

  if (!session) {
    redirect('/');
  }

  return (
    <AppLayout
      breadcrumbs={[
        { label: 'Home', href: '/' },
        { label: 'The Vault' },
      ]}
      user={{
        name: session.user?.name || 'User',
        email: session.user?.email || '',
        avatarUrl: session.user?.image || undefined,
      }}
      credits={balance ? { current: balance.current, total: balance.total } : { current: 0, total: 0 }}
    >
      <div
        className="h-full flex flex-col p-6 overflow-hidden"
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          const droppedFiles = Array.from(e.dataTransfer.files);
          handleFileDrop(droppedFiles);
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold mb-1">The Vault</h1>
            <p className="text-sm text-zinc-400">
              Your Personal Data Moat - Secure file storage with AI-powered indexing
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-md transition-colors ${
                viewMode === 'grid' ? 'bg-zinc-800 text-white' : 'text-zinc-500 hover:text-white'
              }`}
            >
              <Grid3X3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-md transition-colors ${
                viewMode === 'list' ? 'bg-zinc-800 text-white' : 'text-zinc-500 hover:text-white'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Search and filters */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <Input
              placeholder="Search files..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-zinc-900 border-zinc-700"
            />
          </div>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="bg-zinc-900 border border-zinc-800">
              <TabsTrigger value="all" className="data-[state=active]:bg-zinc-800">
                All Files
              </TabsTrigger>
              <TabsTrigger value="private" className="data-[state=active]:bg-zinc-800">
                Private
              </TabsTrigger>
              <TabsTrigger value="vectorized" className="data-[state=active]:bg-zinc-800">
                Vectorized
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {/* Drop overlay */}
        {isDragging && (
          <div className="absolute inset-0 bg-purple-500/10 border-2 border-dashed border-purple-500 z-10 flex items-center justify-center m-6 rounded-lg">
            <div className="text-center">
              <Upload className="w-12 h-12 text-purple-400 mx-auto mb-4" />
              <p className="text-lg font-medium text-purple-400">
                Drop files to upload to your Vault
              </p>
            </div>
          </div>
        )}

        {/* File grid */}
        <div className="flex-1 overflow-auto fp-scrollbar">
          {filteredFiles.length === 0 ? (
            <MoatDropzone
              onDrop={handleFileDrop}
              isActive={isDragging}
              className="h-64"
            />
          ) : (
            <div className={`grid gap-4 ${viewMode === 'grid' ? 'grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5' : 'grid-cols-1'}`}>
              {filteredFiles.map((file) => (
                <MoatFileCard
                  key={file.id}
                  id={file.id}
                  filename={file.filename}
                  contentType={file.contentType}
                  sizeBytes={file.sizeBytes}
                  securityLevel={file.securityLevel}
                  hasPII={file.hasPII}
                  isVectorized={file.isVectorized}
                  createdAt={new Date(file.createdAt)}
                  onDelete={() => handleDelete(file.id)}
                  onDownload={() => handleDownload(file.id)}
                  onAddToContext={() => console.log('Add to context', file.id)}
                  onPreview={() => setPreviewFile(file)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Stats footer */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-zinc-800 text-sm text-zinc-500">
          <span>{filteredFiles.length} files</span>
          <span>
            {(filteredFiles.reduce((acc, f) => acc + f.sizeBytes, 0) / 1024 / 1024).toFixed(1)} MB
            used
          </span>
        </div>
      </div>

      {/* File Preview Dialog */}
      <Dialog open={!!previewFile} onOpenChange={(open) => !open && setPreviewFile(null)}>
        <DialogContent className="max-w-4xl h-[85vh] p-0 gap-0 bg-zinc-950 flex flex-col">
          {previewFile && (
            <>
              <DialogHeader className="p-4 border-b border-zinc-800 shrink-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="size-10 rounded-lg bg-zinc-800 flex items-center justify-center">
                      {previewFile.contentType.includes('image') ? (
                        <FileImage className="size-5 text-zinc-400" />
                      ) : (
                        <FileText className="size-5 text-zinc-400" />
                      )}
                    </div>
                    <div>
                      <DialogTitle className="text-base">{previewFile.filename}</DialogTitle>
                      <p className="text-xs text-muted-foreground">
                        {formatFileSize(previewFile.sizeBytes)} • {new Date(previewFile.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" className="gap-2">
                      <Download className="size-4" />
                      Download
                    </Button>
                    <Button variant="outline" size="sm" className="gap-2">
                      <ExternalLink className="size-4" />
                      Open
                    </Button>
                  </div>
                </div>
              </DialogHeader>

              {/* Preview Content */}
              <div className="flex-1 overflow-auto p-6">
                {previewFile.contentType.includes('image') ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="bg-zinc-900 rounded-lg p-8 border border-zinc-800">
                      <FileImage className="size-24 text-zinc-600 mx-auto mb-4" />
                      <p className="text-sm text-zinc-500 text-center">Image preview</p>
                    </div>
                  </div>
                ) : previewFile.contentType.includes('pdf') ? (
                  <div className="h-full bg-zinc-900 rounded-lg border border-zinc-800 flex flex-col">
                    <div className="flex-1 flex items-center justify-center">
                      <div className="text-center p-8">
                        <FileText className="size-16 text-zinc-600 mx-auto mb-4" />
                        <h3 className="font-medium mb-2">PDF Preview</h3>
                        <p className="text-sm text-zinc-500 mb-4">
                          Connect to MinIO to enable live PDF preview
                        </p>
                        <div className="bg-zinc-800 rounded-lg p-4 text-left max-w-md mx-auto">
                          <p className="text-xs text-zinc-400 font-mono">
                            File: {previewFile.filename}<br/>
                            Size: {formatFileSize(previewFile.sizeBytes)}<br/>
                            Type: {previewFile.contentType}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-full bg-zinc-900 rounded-lg border border-zinc-800 flex items-center justify-center">
                    <div className="text-center p-8">
                      <FileText className="size-16 text-zinc-600 mx-auto mb-4" />
                      <h3 className="font-medium mb-2">File Preview</h3>
                      <p className="text-sm text-zinc-500">
                        Preview not available for this file type
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* File metadata footer */}
              <div className="p-4 border-t border-zinc-800 shrink-0">
                <div className="flex items-center gap-3">
                  {previewFile.securityLevel === 'private' && (
                    <Badge variant="outline" className="gap-1 border-purple-500/50 text-purple-400">
                      <Shield className="size-3" />
                      Private
                    </Badge>
                  )}
                  {previewFile.isVectorized && (
                    <Badge variant="outline" className="gap-1 border-emerald-500/50 text-emerald-400">
                      <Sparkles className="size-3" />
                      Vectorized
                    </Badge>
                  )}
                  {previewFile.hasPII && (
                    <Badge variant="outline" className="gap-1 border-amber-500/50 text-amber-400">
                      <AlertTriangle className="size-3" />
                      PII Detected
                    </Badge>
                  )}
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </AppLayout>
  );
}
