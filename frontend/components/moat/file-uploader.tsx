"use client"

import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  UploadCloud,
  File,
  FileText,
  Image,
  X,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Shield,
  Lock,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { toast } from "sonner"

interface UploadedFile {
  id: string
  file: File
  status: "pending" | "uploading" | "processing" | "ready" | "error"
  progress: number
  error?: string
}

interface MoatFileUploaderProps {
  projectId?: string
  onUploadComplete?: (fileId: string, objectKey: string) => void
  className?: string
}

const FILE_ICONS: Record<string, React.ReactNode> = {
  pdf: <FileText className="w-5 h-5 text-red-400" />,
  doc: <FileText className="w-5 h-5 text-blue-400" />,
  docx: <FileText className="w-5 h-5 text-blue-400" />,
  txt: <FileText className="w-5 h-5 text-zinc-400" />,
  png: <Image className="w-5 h-5 text-purple-400" />,
  jpg: <Image className="w-5 h-5 text-purple-400" />,
  jpeg: <Image className="w-5 h-5 text-purple-400" />,
}

export function MoatFileUploader({ projectId, onUploadComplete, className }: MoatFileUploaderProps) {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [isUploading, setIsUploading] = useState(false)
  
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map((file) => ({
      id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      file,
      status: "pending",
      progress: 0,
    }))
    setFiles((prev) => [...prev, ...newFiles])
  }, [])
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/msword": [".doc"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "text/plain": [".txt"],
      "image/*": [".png", ".jpg", ".jpeg"],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
  })
  
  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id))
  }
  
  const uploadFile = async (uploadedFile: UploadedFile) => {
    const { id, file } = uploadedFile
    
    // Update status to uploading
    setFiles((prev) =>
      prev.map((f) =>
        f.id === id ? { ...f, status: "uploading", progress: 0 } : f
      )
    )
    
    try {
      // 1. Get presigned URL from backend
      const urlResponse = await fetch("/api/files/upload-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          filename: file.name,
          contentType: file.type,
          projectId,
        }),
      })
      
      if (!urlResponse.ok) {
        throw new Error("Failed to get upload URL")
      }
      
      const { uploadUrl, objectKey, fileId } = await urlResponse.json()
      
      // 2. Upload directly to MinIO/S3
      const uploadResponse = await fetch(uploadUrl, {
        method: "PUT",
        body: file,
        headers: {
          "Content-Type": file.type,
        },
      })
      
      if (!uploadResponse.ok) {
        throw new Error("Upload failed")
      }
      
      // Update progress
      setFiles((prev) =>
        prev.map((f) =>
          f.id === id ? { ...f, progress: 100, status: "processing" } : f
        )
      )
      
      // 3. Notify backend to process (will trigger RAG pipeline)
      // This is handled automatically via MinIO webhook, but we can also trigger manually
      
      // Wait a bit for processing
      await new Promise((resolve) => setTimeout(resolve, 1500))
      
      // Mark as ready
      setFiles((prev) =>
        prev.map((f) =>
          f.id === id ? { ...f, status: "ready" } : f
        )
      )
      
      onUploadComplete?.(fileId, objectKey)
      toast.success(`${file.name} added to your Data Moat`)
      
    } catch (error) {
      console.error("Upload error:", error)
      setFiles((prev) =>
        prev.map((f) =>
          f.id === id
            ? { ...f, status: "error", error: (error as Error).message }
            : f
        )
      )
      toast.error(`Failed to upload ${file.name}`)
    }
  }
  
  const uploadAllFiles = async () => {
    setIsUploading(true)
    const pendingFiles = files.filter((f) => f.status === "pending")
    
    for (const file of pendingFiles) {
      await uploadFile(file)
    }
    
    setIsUploading(false)
  }
  
  const getFileExtension = (filename: string) => {
    return filename.split(".").pop()?.toLowerCase() || ""
  }
  
  const pendingCount = files.filter((f) => f.status === "pending").length
  const readyCount = files.filter((f) => f.status === "ready").length
  
  return (
    <Card className={cn("border-zinc-800 bg-zinc-900/50", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-sm font-mono tracking-wide flex items-center gap-2">
              <Shield className="w-4 h-4 text-emerald-500" />
              PERSONAL DATA MOAT
            </CardTitle>
            <CardDescription className="text-xs mt-1">
              Your files are encrypted and isolated in EU-West storage
            </CardDescription>
          </div>
          <Badge variant="outline" className="text-[10px] border-emerald-500/50 text-emerald-400">
            <Lock className="w-3 h-3 mr-1" />
            ENCRYPTED
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={cn(
            "border-2 border-dashed rounded-sm p-8 text-center cursor-pointer transition-all",
            isDragActive
              ? "border-emerald-500 bg-emerald-500/10"
              : "border-zinc-700 hover:border-zinc-600 hover:bg-zinc-800/50"
          )}
        >
          <input {...getInputProps()} />
          <UploadCloud
            className={cn(
              "w-10 h-10 mx-auto mb-4",
              isDragActive ? "text-emerald-500" : "text-zinc-500"
            )}
          />
          <p className="text-sm text-zinc-300">
            {isDragActive
              ? "Drop files here..."
              : "Drag contracts, invoices, or evidence here"}
          </p>
          <p className="text-xs text-zinc-600 mt-2">
            PDF, DOC, TXT, Images • Max 50MB
          </p>
        </div>
        
        {/* File List */}
        {files.length > 0 && (
          <ScrollArea className="max-h-60">
            <div className="space-y-2">
              {files.map((uploadedFile) => {
                const ext = getFileExtension(uploadedFile.file.name)
                
                return (
                  <div
                    key={uploadedFile.id}
                    className="flex items-center gap-3 p-2 rounded-sm bg-zinc-800/50 border border-zinc-700"
                  >
                    {/* Icon */}
                    <div className="w-8 h-8 flex items-center justify-center rounded-sm bg-zinc-900">
                      {FILE_ICONS[ext] || <File className="w-5 h-5 text-zinc-500" />}
                    </div>
                    
                    {/* File Info */}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-zinc-200 truncate">
                        {uploadedFile.file.name}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-[10px] text-zinc-500">
                          {(uploadedFile.file.size / 1024).toFixed(1)} KB
                        </span>
                        
                        {uploadedFile.status === "uploading" && (
                          <div className="flex-1 max-w-24">
                            <Progress value={uploadedFile.progress} className="h-1" />
                          </div>
                        )}
                        
                        {uploadedFile.status === "processing" && (
                          <Badge variant="outline" className="text-[10px] py-0">
                            <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                            Processing
                          </Badge>
                        )}
                        
                        {uploadedFile.status === "ready" && (
                          <Badge className="text-[10px] py-0 bg-emerald-500/20 text-emerald-400">
                            <CheckCircle2 className="w-3 h-3 mr-1" />
                            Ready
                          </Badge>
                        )}
                        
                        {uploadedFile.status === "error" && (
                          <Badge variant="destructive" className="text-[10px] py-0">
                            <AlertCircle className="w-3 h-3 mr-1" />
                            Error
                          </Badge>
                        )}
                      </div>
                    </div>
                    
                    {/* Remove Button */}
                    {uploadedFile.status !== "uploading" && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 text-zinc-500 hover:text-zinc-300"
                        onClick={() => removeFile(uploadedFile.id)}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                )
              })}
            </div>
          </ScrollArea>
        )}
        
        {/* Upload Button */}
        {pendingCount > 0 && (
          <Button
            onClick={uploadAllFiles}
            disabled={isUploading}
            className="w-full bg-emerald-600 hover:bg-emerald-700 font-mono text-sm"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <UploadCloud className="w-4 h-4 mr-2" />
                Upload {pendingCount} file{pendingCount > 1 ? "s" : ""} to Moat
              </>
            )}
          </Button>
        )}
        
        {/* Stats */}
        {readyCount > 0 && (
          <p className="text-xs text-center text-zinc-500">
            {readyCount} file{readyCount > 1 ? "s" : ""} protected in your Data Moat
          </p>
        )}
      </CardContent>
    </Card>
  )
}
