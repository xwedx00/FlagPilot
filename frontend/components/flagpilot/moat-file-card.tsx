'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import {
  FileText,
  FileImage,
  FileVideo,
  FileAudio,
  FileArchive,
  FileSpreadsheet,
  FileCode,
  File,
  Shield,
  AlertTriangle,
  Sparkles,
  MoreVertical,
  Download,
  Trash2,
  Plus,
  Eye,
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';

type SecurityLevel = 'public' | 'private';

interface MoatFileCardProps {
  id: string;
  filename: string;
  contentType: string;
  sizeBytes: number;
  securityLevel: SecurityLevel;
  hasPII?: boolean;
  isVectorized?: boolean;
  thumbnailUrl?: string;
  createdAt?: Date;
  onAddToContext?: () => void;
  onDelete?: () => void;
  onDownload?: () => void;
  onPreview?: () => void;
  className?: string;
}

/**
 * Get the appropriate icon for a file type
 */
function getFileIcon(contentType: string) {
  if (contentType.startsWith('image/')) return FileImage;
  if (contentType.startsWith('video/')) return FileVideo;
  if (contentType.startsWith('audio/')) return FileAudio;
  if (contentType.includes('pdf')) return FileText;
  if (contentType.includes('spreadsheet') || contentType.includes('excel') || contentType.includes('csv'))
    return FileSpreadsheet;
  if (contentType.includes('zip') || contentType.includes('archive') || contentType.includes('tar'))
    return FileArchive;
  if (contentType.includes('javascript') || contentType.includes('json') || contentType.includes('html'))
    return FileCode;
  return File;
}

/**
 * Format file size to human readable
 */
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

/**
 * MoatFileCard - File card for the Personal Data Moat
 * 
 * Displays file with security level (private/public border color),
 * PII detection badge, and vectorization status.
 * 
 * @example
 * <MoatFileCard
 *   id="1"
 *   filename="contract.pdf"
 *   contentType="application/pdf"
 *   sizeBytes={1024000}
 *   securityLevel="private"
 *   hasPII={true}
 *   isVectorized={true}
 * />
 */
export function MoatFileCard({
  id,
  filename,
  contentType,
  sizeBytes,
  securityLevel,
  hasPII = false,
  isVectorized = false,
  thumbnailUrl,
  createdAt,
  onAddToContext,
  onDelete,
  onDownload,
  onPreview,
  className,
}: MoatFileCardProps) {
  const FileIcon = getFileIcon(contentType);
  const isPrivate = securityLevel === 'private';

  return (
    <div
      className={cn(
        'group relative rounded-md overflow-hidden',
        'bg-zinc-900/50 backdrop-blur-sm',
        'border transition-all duration-75',
        isPrivate
          ? 'border-purple-500/50 hover:border-purple-400'
          : 'border-zinc-700 hover:border-zinc-600',
        'hover:bg-zinc-800/50 cursor-pointer',
        className
      )}
      onClick={onPreview}
    >
      {/* Thumbnail or Icon */}
      <div className="aspect-[4/3] bg-zinc-800 flex items-center justify-center relative">
        {thumbnailUrl ? (
          <img
            src={thumbnailUrl}
            alt={filename}
            className="w-full h-full object-cover"
          />
        ) : (
          <FileIcon className="w-12 h-12 text-zinc-500" />
        )}

        {/* Security indicator overlay */}
        {isPrivate && (
          <div className="absolute top-2 left-2">
            <Shield className="w-4 h-4 text-purple-400" />
          </div>
        )}

        {/* Hover overlay with actions */}
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onPreview?.();
            }}
            className="p-2 rounded-md bg-zinc-800 hover:bg-zinc-700 transition-colors"
          >
            <Eye className="w-4 h-4" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDownload?.();
            }}
            className="p-2 rounded-md bg-zinc-800 hover:bg-zinc-700 transition-colors"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* File info */}
      <div className="p-3">
        <div className="flex items-start justify-between gap-2 mb-2">
          <h4 className="text-sm font-medium truncate flex-1" title={filename}>
            {filename}
          </h4>
          
          {/* Actions dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger
              onClick={(e) => e.stopPropagation()}
              className="p-1 rounded hover:bg-zinc-700 transition-colors opacity-0 group-hover:opacity-100"
            >
              <MoreVertical className="w-4 h-4 text-zinc-400" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuItem onClick={onAddToContext}>
                <Plus className="w-4 h-4 mr-2" />
                Add to Context
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onDownload}>
                <Download className="w-4 h-4 mr-2" />
                Download
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={onDelete}
                className="text-rose-400 focus:text-rose-400"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete from Moat
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Metadata */}
        <div className="flex items-center gap-2 text-xs text-zinc-500 mb-2">
          <span className="font-mono">{formatFileSize(sizeBytes)}</span>
          {createdAt && (
            <>
              <span>•</span>
              <span>{createdAt.toLocaleDateString()}</span>
            </>
          )}
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-1.5">
          {hasPII && (
            <span className="fp-badge-danger text-[10px] px-1.5 py-0.5 rounded flex items-center gap-1">
              <AlertTriangle className="w-2.5 h-2.5" />
              PII DETECTED
            </span>
          )}
          {isVectorized && (
            <span className="fp-badge-purple text-[10px] px-1.5 py-0.5 rounded flex items-center gap-1">
              <Sparkles className="w-2.5 h-2.5" />
              VECTORIZED
            </span>
          )}
          {isPrivate && (
            <span className="fp-badge-info text-[10px] px-1.5 py-0.5 rounded flex items-center gap-1">
              <Shield className="w-2.5 h-2.5" />
              PRIVATE
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * File upload dropzone for the Vault
 */
export function MoatDropzone({
  onDrop,
  isActive,
  className,
}: {
  onDrop?: (files: File[]) => void;
  isActive?: boolean;
  className?: string;
}) {
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    onDrop?.(files);
  };

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      className={cn(
        'fp-dropzone',
        isActive && 'fp-dropzone-active',
        className
      )}
    >
      <Shield className="w-10 h-10 text-zinc-500" />
      <p className="text-sm text-zinc-400 text-center">
        Drop contracts here to secure them
      </p>
      <p className="text-xs text-zinc-600">
        PDFs, DOCX, images, and more
      </p>
    </div>
  );
}

export type { MoatFileCardProps, SecurityLevel };
