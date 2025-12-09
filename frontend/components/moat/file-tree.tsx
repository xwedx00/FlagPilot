"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  ChevronRight,
  ChevronDown,
  Folder,
  FolderOpen,
  FileText,
  Image,
  File,
  Download,
  Trash2,
  Eye,
  MoreVertical,
  Search,
  Database,
} from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"

interface MoatFile {
  id: string
  name: string
  type: "file" | "folder"
  path: string
  size?: number
  contentType?: string
  embeddingStatus?: "pending" | "embedded" | "failed"
  modifiedAt?: Date
  children?: MoatFile[]
}

interface MoatFileTreeProps {
  files: MoatFile[]
  onDownload?: (file: MoatFile) => void
  onDelete?: (file: MoatFile) => void
  onPreview?: (file: MoatFile) => void
  className?: string
}

const FILE_ICONS: Record<string, React.ReactNode> = {
  pdf: <FileText className="w-4 h-4 text-red-400" />,
  doc: <FileText className="w-4 h-4 text-blue-400" />,
  docx: <FileText className="w-4 h-4 text-blue-400" />,
  txt: <FileText className="w-4 h-4 text-zinc-400" />,
  png: <Image className="w-4 h-4 text-purple-400" />,
  jpg: <Image className="w-4 h-4 text-purple-400" />,
  jpeg: <Image className="w-4 h-4 text-purple-400" />,
}

function FileTreeItem({
  file,
  level = 0,
  onDownload,
  onDelete,
  onPreview,
}: {
  file: MoatFile
  level?: number
  onDownload?: (file: MoatFile) => void
  onDelete?: (file: MoatFile) => void
  onPreview?: (file: MoatFile) => void
}) {
  const [isExpanded, setIsExpanded] = useState(false)
  const isFolder = file.type === "folder"
  const ext = file.name.split(".").pop()?.toLowerCase() || ""
  
  const formatSize = (bytes?: number) => {
    if (!bytes) return ""
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`
  }
  
  return (
    <div>
      <div
        className={cn(
          "flex items-center gap-2 py-1.5 px-2 rounded-sm hover:bg-zinc-800/50 transition-colors group",
          "cursor-pointer"
        )}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => isFolder && setIsExpanded(!isExpanded)}
      >
        {/* Expand/Collapse Icon */}
        {isFolder ? (
          isExpanded ? (
            <ChevronDown className="w-4 h-4 text-zinc-500" />
          ) : (
            <ChevronRight className="w-4 h-4 text-zinc-500" />
          )
        ) : (
          <span className="w-4" />
        )}
        
        {/* File/Folder Icon */}
        {isFolder ? (
          isExpanded ? (
            <FolderOpen className="w-4 h-4 text-amber-400" />
          ) : (
            <Folder className="w-4 h-4 text-amber-400" />
          )
        ) : (
          FILE_ICONS[ext] || <File className="w-4 h-4 text-zinc-500" />
        )}
        
        {/* Name */}
        <span className="text-sm text-zinc-200 flex-1 truncate">{file.name}</span>
        
        {/* Embedding Status */}
        {!isFolder && file.embeddingStatus && (
          <Badge
            variant="outline"
            className={cn(
              "text-[10px] py-0 px-1.5",
              file.embeddingStatus === "embedded" && "border-emerald-500/50 text-emerald-400",
              file.embeddingStatus === "pending" && "border-amber-500/50 text-amber-400",
              file.embeddingStatus === "failed" && "border-red-500/50 text-red-400"
            )}
          >
            {file.embeddingStatus === "embedded" && <Database className="w-2.5 h-2.5 mr-1" />}
            {file.embeddingStatus === "embedded" ? "RAG" : file.embeddingStatus}
          </Badge>
        )}
        
        {/* Size */}
        {!isFolder && file.size && (
          <span className="text-[10px] text-zinc-500 font-mono">
            {formatSize(file.size)}
          </span>
        )}
        
        {/* Actions */}
        {!isFolder && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={(e) => e.stopPropagation()}
              >
                <MoreVertical className="w-4 h-4 text-zinc-500" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="bg-zinc-900 border-zinc-800">
              <DropdownMenuItem onClick={() => onPreview?.(file)}>
                <Eye className="w-4 h-4 mr-2" />
                Preview
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onDownload?.(file)}>
                <Download className="w-4 h-4 mr-2" />
                Download
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => onDelete?.(file)}
                className="text-red-400 focus:text-red-400"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
      
      {/* Children */}
      {isFolder && isExpanded && file.children && (
        <div>
          {file.children.map((child) => (
            <FileTreeItem
              key={child.id}
              file={child}
              level={level + 1}
              onDownload={onDownload}
              onDelete={onDelete}
              onPreview={onPreview}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export function MoatFileTree({
  files,
  onDownload,
  onDelete,
  onPreview,
  className,
}: MoatFileTreeProps) {
  const [searchQuery, setSearchQuery] = useState("")
  
  const filterFiles = (items: MoatFile[], query: string): MoatFile[] => {
    if (!query) return items
    
    return items.reduce<MoatFile[]>((acc, item) => {
      if (item.name.toLowerCase().includes(query.toLowerCase())) {
        acc.push(item)
      } else if (item.children) {
        const filteredChildren = filterFiles(item.children, query)
        if (filteredChildren.length > 0) {
          acc.push({ ...item, children: filteredChildren })
        }
      }
      return acc
    }, [])
  }
  
  const filteredFiles = filterFiles(files, searchQuery)
  
  return (
    <Card className={cn("border-zinc-800 bg-zinc-900/50", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-mono tracking-wide">
            DATA MOAT FILES
          </CardTitle>
          <Badge variant="outline" className="text-[10px]">
            {files.length} items
          </Badge>
        </div>
        
        {/* Search */}
        <div className="relative mt-2">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <Input
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 h-8 text-sm bg-zinc-800 border-zinc-700"
          />
        </div>
      </CardHeader>
      
      <CardContent className="p-0">
        <ScrollArea className="h-80">
          <div className="p-2">
            {filteredFiles.length === 0 ? (
              <div className="py-8 text-center text-zinc-500 text-sm">
                {searchQuery ? "No files match your search" : "No files in your Data Moat"}
              </div>
            ) : (
              filteredFiles.map((file) => (
                <FileTreeItem
                  key={file.id}
                  file={file}
                  onDownload={onDownload}
                  onDelete={onDelete}
                  onPreview={onPreview}
                />
              ))
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}

// Export types for external use
export type { MoatFile, MoatFileTreeProps }
