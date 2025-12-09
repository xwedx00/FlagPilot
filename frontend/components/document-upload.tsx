"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Loader } from "@/components/ui/loader";
import { Switch } from "@/components/ui/switch";
import {
  Upload,
  FileText,
  X,
  CheckCircle2,
  AlertCircle,
  File,
  Image as ImageIcon,
  FileCode,
  Trash2,
  Lock,
  Globe,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { uploadAndVectorize, type VectorNamespace } from "@/lib/api";

interface DocumentUploadProps {
  userId: string;
  onClose: () => void;
  onUploadComplete: (doc: { name: string; type: string; url: string; vectorized: boolean }) => void;
}

const DOCUMENT_TYPES = [
  { value: "contract", label: "Contract", icon: FileText },
  { value: "invoice", label: "Invoice", icon: FileText },
  { value: "job-posting", label: "Job Posting", icon: FileCode },
  { value: "message", label: "Client Message", icon: FileText },
  { value: "portfolio", label: "Portfolio Item", icon: ImageIcon },
  { value: "cv", label: "CV / Resume", icon: FileText },
  { value: "other", label: "Other Document", icon: File },
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ACCEPTED_FILE_TYPES = [
  "application/pdf",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "text/plain",
  "image/png",
  "image/jpeg",
  "image/webp",
];

export function DocumentUpload({ userId, onClose, onUploadComplete }: DocumentUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState("");
  const [description, setDescription] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [storageType, setStorageType] = useState<VectorNamespace>("personal_vault");

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const validateFile = (file: File): string | null => {
    if (file.size > MAX_FILE_SIZE) {
      return "File size must be less than 10MB";
    }
    if (!ACCEPTED_FILE_TYPES.includes(file.type)) {
      return "File type not supported. Please upload PDF, DOC, DOCX, TXT, PNG, JPG, or WEBP files.";
    }
    return null;
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    setError(null);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      const validationError = validateFile(droppedFile);
      if (validationError) {
        setError(validationError);
        return;
      }
      setFile(droppedFile);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const validationError = validateFile(selectedFile);
      if (validationError) {
        setError(validationError);
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file || !documentType) return;

    setIsUploading(true);
    setUploadProgress(0);
    setError(null);

    try {
      // Use the new MinIO presigned URL upload flow
      const result = await uploadAndVectorize(file, {
        documentType,
        description,
        namespace: storageType,
        onProgress: (percent) => setUploadProgress(Math.min(percent, 90)),
      });

      setUploadProgress(100);

      // Store document reference locally for tracking
      const existingDocs = JSON.parse(localStorage.getItem(`user_documents_${userId}`) || "[]");
      existingDocs.push({
        name: file.name,
        type: documentType,
        url: result.downloadUrl,
        objectKey: result.objectKey,
        vectorized: result.vectorized,
        documentId: result.documentId,
        namespace: storageType,
        description,
        uploadedAt: new Date().toISOString(),
      });
      localStorage.setItem(`user_documents_${userId}`, JSON.stringify(existingDocs));

      setTimeout(() => {
        onUploadComplete({
          name: file.name,
          type: documentType,
          url: result.downloadUrl,
          vectorized: result.vectorized,
        });
      }, 500);
    } catch (err) {
      console.error("Upload error:", err);
      setError(`Failed to upload document. ${err instanceof Error ? err.message : "Please try again."}`);
      setIsUploading(false);
    }
  };

  const getFileIcon = () => {
    if (!file) return File;
    if (file.type.startsWith("image/")) return ImageIcon;
    if (file.type.includes("pdf") || file.type.includes("document")) return FileText;
    return FileCode;
  };

  const FileIcon = getFileIcon();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop with blur */}
      <div
        className="absolute inset-0 bg-background/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-10 w-full max-w-lg mx-4 bg-card rounded-2xl shadow-2xl border overflow-hidden">
        {/* Header */}
        <div className="p-6 pb-4 flex items-center justify-between border-b">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Upload className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h2 className="font-semibold">Upload Document</h2>
              <p className="text-xs text-muted-foreground">For AI analysis and RAG context</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Drop Zone */}
          {!file ? (
            <div
              className={cn(
                "border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer",
                isDragging
                  ? "border-primary bg-primary/5"
                  : "border-border hover:border-primary/50 hover:bg-muted/50"
              )}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => document.getElementById("file-input")?.click()}
            >
              <input
                id="file-input"
                type="file"
                className="hidden"
                accept={ACCEPTED_FILE_TYPES.join(",")}
                onChange={handleFileSelect}
              />
              <Upload className={cn(
                "h-10 w-10 mx-auto mb-3",
                isDragging ? "text-primary" : "text-muted-foreground"
              )} />
              <p className="font-medium mb-1">
                {isDragging ? "Drop your file here" : "Drag & drop or click to upload"}
              </p>
              <p className="text-xs text-muted-foreground">
                PDF, DOC, DOCX, TXT, PNG, JPG up to 10MB
              </p>
            </div>
          ) : (
            <div className="border rounded-xl p-4">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-lg bg-primary/10">
                  <FileIcon className="h-6 w-6 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">{file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                {!isUploading && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setFile(null)}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                )}
              </div>
              {isUploading && (
                <div className="mt-3 space-y-2">
                  <Progress value={uploadProgress} className="h-1.5" />
                  <p className="text-xs text-muted-foreground text-center">
                    {uploadProgress < 100 ? "Uploading..." : "Processing with AI..."}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-destructive/10 text-destructive text-sm">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {error}
            </div>
          )}

          {/* Document Type Selection */}
          {file && !isUploading && (
            <>
              <div className="space-y-2">
                <Label>Document Type</Label>
                <Select value={documentType} onValueChange={setDocumentType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select document type" />
                  </SelectTrigger>
                  <SelectContent>
                    {DOCUMENT_TYPES.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        <div className="flex items-center gap-2">
                          <type.icon className="h-4 w-4" />
                          {type.label}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea
                  id="description"
                  placeholder="Add context about this document..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={2}
                />
              </div>

              {/* Storage Type Toggle */}
              <div className="space-y-3 p-4 rounded-lg border bg-muted/30">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {storageType === "personal_vault" ? (
                      <Lock className="h-4 w-4 text-primary" />
                    ) : (
                      <Globe className="h-4 w-4 text-green-500" />
                    )}
                    <Label htmlFor="storage-type" className="font-medium">
                      {storageType === "personal_vault" ? "Personal Vault" : "Global Wisdom"}
                    </Label>
                  </div>
                  <Switch
                    id="storage-type"
                    checked={storageType === "global_wisdom"}
                    onCheckedChange={(checked) =>
                      setStorageType(checked ? "global_wisdom" : "personal_vault")
                    }
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  {storageType === "personal_vault" ? (
                    <>
                      <strong>Private:</strong> Only you can access this document. Used for personal context like CVs, contracts, and job descriptions.
                    </>
                  ) : (
                    <>
                      <strong>Shared:</strong> This document helps improve AI suggestions for all users. Best for general knowledge and successful workflow examples.
                    </>
                  )}
                </p>
              </div>

              {/* Info */}
              <div className="flex items-start gap-2 p-3 rounded-lg bg-muted text-sm">
                <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 shrink-0" />
                <p className="text-muted-foreground">
                  {storageType === "personal_vault"
                    ? "This document will be processed and added to your personal knowledge base for AI-powered analysis and recommendations."
                    : "This document will be anonymized and added to the global knowledge base to help improve AI suggestions for all users."
                  }
                </p>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 pt-0 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose} disabled={isUploading}>
            Cancel
          </Button>
          <Button
            onClick={handleUpload}
            disabled={!file || !documentType || isUploading}
          >
            {isUploading ? (
              <>
                <Loader size="sm" className="mr-2" />
                {uploadProgress < 100 ? "Uploading..." : "Processing..."}
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Upload & Analyze
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
