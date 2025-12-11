'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
    Upload,
    File,
    FileText,
    Image,
    X,
    CheckCircle2,
    AlertCircle,
    Loader2,
} from 'lucide-react';
import { toast } from 'sonner';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface FileUploadProps {
    onUploadComplete?: (files: UploadedFile[]) => void;
    maxFiles?: number;
    accept?: Record<string, string[]>;
    className?: string;
    vectorize?: boolean;
}

interface UploadedFile {
    id: string;
    name: string;
    size: number;
    type: string;
    url?: string;
    status: 'uploading' | 'processing' | 'complete' | 'error';
    progress: number;
    error?: string;
}

const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return Image;
    if (type.includes('pdf') || type.includes('document')) return FileText;
    return File;
};

export function FileUpload({
    onUploadComplete,
    maxFiles = 10,
    accept = {
        'application/pdf': ['.pdf'],
        'text/plain': ['.txt'],
        'application/msword': ['.doc'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
    },
    className,
    vectorize = true,
}: FileUploadProps) {
    const [files, setFiles] = useState<UploadedFile[]>([]);
    const [isUploading, setIsUploading] = useState(false);

    const uploadFile = async (file: File): Promise<UploadedFile> => {
        const fileId = `file-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;

        const uploadedFile: UploadedFile = {
            id: fileId,
            name: file.name,
            size: file.size,
            type: file.type,
            status: 'uploading',
            progress: 0,
        };

        // Update state with new file
        setFiles(prev => [...prev, uploadedFile]);

        try {
            // Update progress - starting upload
            setFiles(prev => prev.map(f =>
                f.id === fileId ? { ...f, progress: 10 } : f
            ));

            // Direct upload to backend (which sends to RAGFlow)
            const formData = new FormData();
            formData.append('file', file);
            formData.append('doc_type', 'document');

            const uploadResponse = await fetch(`${API_BASE_URL}/api/v1/files/upload`, {
                method: 'POST',
                credentials: 'include',
                body: formData,
            });

            // Update progress - upload complete, processing
            setFiles(prev => prev.map(f =>
                f.id === fileId ? { ...f, progress: 70, status: 'processing' } : f
            ));

            if (!uploadResponse.ok) {
                const error = await uploadResponse.json().catch(() => ({ detail: 'Upload failed' }));
                throw new Error(error.detail || 'Upload failed');
            }

            const result = await uploadResponse.json();

            // Complete - file is now in RAGFlow for vectorization
            const completedFile: UploadedFile = {
                ...uploadedFile,
                id: result.filename || fileId,
                status: 'complete',
                progress: 100,
            };

            setFiles(prev => prev.map(f =>
                f.id === fileId ? completedFile : f
            ));

            return completedFile;
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Upload failed';

            setFiles(prev => prev.map(f =>
                f.id === fileId ? { ...f, status: 'error', error: errorMessage } : f
            ));

            throw error;
        }
    };

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        if (acceptedFiles.length === 0) return;

        setIsUploading(true);
        const uploadedFiles: UploadedFile[] = [];

        for (const file of acceptedFiles) {
            try {
                const uploaded = await uploadFile(file);
                uploadedFiles.push(uploaded);
            } catch (error) {
                console.error(`Failed to upload ${file.name}:`, error);
                toast.error(`Failed to upload ${file.name}`);
            }
        }

        setIsUploading(false);

        if (uploadedFiles.length > 0) {
            toast.success(`${uploadedFiles.length} file(s) uploaded successfully`);
            onUploadComplete?.(uploadedFiles);
        }
    }, [onUploadComplete, vectorize]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept,
        maxFiles,
        disabled: isUploading,
    });

    const removeFile = (fileId: string) => {
        setFiles(prev => prev.filter(f => f.id !== fileId));
    };

    const completedFiles = files.filter(f => f.status === 'complete');
    const pendingFiles = files.filter(f => f.status !== 'complete' && f.status !== 'error');

    return (
        <div className={cn('space-y-3', className)}>
            {/* Completed files - show FIRST for visibility */}
            {completedFiles.length > 0 && (
                <div className="space-y-2">
                    <p className="text-xs text-primary font-medium flex items-center gap-1.5">
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        {completedFiles.length} file{completedFiles.length > 1 ? 's' : ''} ready
                    </p>
                    {completedFiles.map((file) => {
                        const FileIcon = getFileIcon(file.type);
                        return (
                            <div
                                key={file.id}
                                className="flex items-center gap-3 p-2.5 rounded-lg bg-primary/5 border border-primary/20"
                            >
                                <FileIcon className="h-4 w-4 text-primary shrink-0" />
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm text-white truncate">{file.name}</p>
                                </div>
                                <span className="text-xs text-primary">
                                    {(file.size / 1024).toFixed(0)} KB
                                </span>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-5 w-5 opacity-50 hover:opacity-100"
                                    onClick={(e) => { e.stopPropagation(); removeFile(file.id); }}
                                >
                                    <X className="h-3 w-3" />
                                </Button>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Compact Dropzone */}
            <div
                {...getRootProps()}
                className={cn(
                    'relative rounded-lg border-2 border-dashed p-4 transition-colors cursor-pointer',
                    isDragActive
                        ? 'border-primary bg-primary/5'
                        : 'border-slate-700 hover:border-slate-600 hover:bg-slate-900/30',
                    isUploading && 'pointer-events-none opacity-60'
                )}
            >
                <input {...getInputProps()} />
                <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-800">
                        {isUploading ? (
                            <Loader2 className="h-4 w-4 text-primary animate-spin" />
                        ) : (
                            <Upload className="h-4 w-4 text-slate-400" />
                        )}
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm text-white">
                            {isDragActive ? 'Drop files here' : 'Drop files or click to upload'}
                        </p>
                        <p className="text-xs text-slate-500">
                            PDF, DOC, TXT, Images
                        </p>
                    </div>
                </div>
            </div>

            {/* Pending uploads - show progress */}
            {pendingFiles.length > 0 && (
                <div className="space-y-2">
                    {pendingFiles.map((file) => {
                        const FileIcon = getFileIcon(file.type);
                        return (
                            <div
                                key={file.id}
                                className="flex items-center gap-3 p-2.5 rounded-lg bg-slate-900 border border-slate-800"
                            >
                                <FileIcon className="h-4 w-4 text-slate-400 shrink-0" />
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm text-white truncate">{file.name}</p>
                                    <Progress value={file.progress} className="h-1 mt-1" />
                                </div>
                                <span className="text-xs text-slate-400">
                                    {file.status === 'processing' ? 'Processing...' : `${file.progress}%`}
                                </span>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Error files */}
            {files.filter(f => f.status === 'error').map((file) => (
                <div
                    key={file.id}
                    className="flex items-center gap-3 p-2.5 rounded-lg bg-red-500/10 border border-red-500/30"
                >
                    <AlertCircle className="h-4 w-4 text-red-500 shrink-0" />
                    <div className="flex-1 min-w-0">
                        <p className="text-sm text-white truncate">{file.name}</p>
                        <p className="text-xs text-red-400">{file.error}</p>
                    </div>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-5 w-5"
                        onClick={() => removeFile(file.id)}
                    >
                        <X className="h-3 w-3" />
                    </Button>
                </div>
            ))}
        </div>
    );
}
