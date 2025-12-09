"use client"

import React, { useEffect, useRef, useState } from "react"
import { ChevronDown, ChevronUp, Terminal, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

export interface LogEntry {
  id: string
  timestamp: Date
  agentId: string
  type: "info" | "thinking" | "output" | "error" | "status"
  message: string
  metadata?: Record<string, unknown>
}

interface LiveConsoleProps {
  logs: LogEntry[]
  className?: string
  maxHeight?: number
  onClear?: () => void
  defaultExpanded?: boolean
}

const AGENT_COLORS: Record<string, string> = {
  flagpilot: "text-violet-400",
  "contract-guardian": "text-blue-400",
  "legal-eagle": "text-blue-400",
  "job-authenticator": "text-amber-400",
  "payment-enforcer": "text-emerald-400",
  negotiator: "text-cyan-400",
  iris: "text-pink-400",
  coach: "text-orange-400",
  connector: "text-sky-400",
  "scope-sentinel": "text-red-400",
  adjudicator: "text-purple-400",
  sentinel: "text-yellow-400",
  ledger: "text-green-400",
  scribe: "text-indigo-400",
  "vault-keeper": "text-teal-400",
}

const TYPE_ICONS: Record<string, string> = {
  info: "ℹ",
  thinking: "💭",
  output: "→",
  error: "✗",
  status: "●",
}

export function LiveConsole({
  logs,
  className,
  maxHeight = 200,
  onClear,
  defaultExpanded = false,
}: LiveConsoleProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (scrollRef.current && isExpanded) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs, isExpanded])

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })
  }

  const getAgentColor = (agentId: string) => {
    return AGENT_COLORS[agentId] || "text-zinc-400"
  }

  const getTypeColor = (type: LogEntry["type"]) => {
    switch (type) {
      case "error":
        return "text-red-400"
      case "thinking":
        return "text-amber-400"
      case "output":
        return "text-emerald-400"
      case "status":
        return "text-blue-400"
      default:
        return "text-zinc-500"
    }
  }

  return (
    <div
      className={cn(
        "border-t border-zinc-800 bg-zinc-950 transition-all duration-200",
        className
      )}
    >
      {/* Header Bar */}
      <div
        className="flex items-center justify-between px-3 py-2 cursor-pointer hover:bg-zinc-900/50"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <Terminal className="h-4 w-4 text-emerald-500" />
          <span className="font-mono text-xs font-medium text-zinc-300">
            AGENT CONSOLE
          </span>
          {logs.length > 0 && (
            <span className="font-mono text-xs text-zinc-500">
              ({logs.length} entries)
            </span>
          )}
          {logs.some((l) => l.type === "error") && (
            <span className="px-1.5 py-0.5 rounded-sm text-[10px] font-mono bg-red-500/20 text-red-400 border border-red-500/30">
              ERRORS
            </span>
          )}
        </div>

        <div className="flex items-center gap-1">
          {isExpanded && onClear && logs.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onClear()
              }}
              className="h-6 px-2 text-xs text-zinc-500 hover:text-zinc-300"
            >
              Clear
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0"
          >
            {isExpanded ? (
              <ChevronDown className="h-4 w-4 text-zinc-500" />
            ) : (
              <ChevronUp className="h-4 w-4 text-zinc-500" />
            )}
          </Button>
        </div>
      </div>

      {/* Log Content */}
      {isExpanded && (
        <div
          ref={scrollRef}
          className="overflow-auto border-t border-zinc-800/50"
          style={{ maxHeight }}
        >
          {logs.length === 0 ? (
            <div className="flex items-center justify-center py-8 text-zinc-600 font-mono text-xs">
              Waiting for agent activity...
            </div>
          ) : (
            <div className="p-2 space-y-0.5">
              {logs.map((log) => (
                <div
                  key={log.id}
                  className={cn(
                    "flex items-start gap-2 px-2 py-1 rounded-sm font-mono text-xs",
                    log.type === "error" && "bg-red-500/5"
                  )}
                >
                  {/* Timestamp */}
                  <span className="text-zinc-600 shrink-0">
                    {formatTimestamp(log.timestamp)}
                  </span>

                  {/* Type Icon */}
                  <span className={cn("shrink-0 w-4", getTypeColor(log.type))}>
                    {TYPE_ICONS[log.type]}
                  </span>

                  {/* Agent Name */}
                  <span
                    className={cn(
                      "shrink-0 font-semibold uppercase tracking-wider",
                      getAgentColor(log.agentId)
                    )}
                    style={{ minWidth: "120px" }}
                  >
                    {log.agentId}
                  </span>

                  {/* Message */}
                  <span
                    className={cn(
                      "flex-1",
                      log.type === "error"
                        ? "text-red-400"
                        : log.type === "output"
                        ? "text-zinc-200"
                        : "text-zinc-400"
                    )}
                  >
                    {log.message}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Hook to manage console logs
export function useConsoleLog() {
  const [logs, setLogs] = useState<LogEntry[]>([])

  const addLog = (
    agentId: string,
    type: LogEntry["type"],
    message: string,
    metadata?: Record<string, unknown>
  ) => {
    const entry: LogEntry = {
      id: `log-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      timestamp: new Date(),
      agentId,
      type,
      message,
      metadata,
    }
    setLogs((prev) => [...prev, entry])
    return entry.id
  }

  const clearLogs = () => setLogs([])

  const logInfo = (agentId: string, message: string) =>
    addLog(agentId, "info", message)

  const logThinking = (agentId: string, message: string) =>
    addLog(agentId, "thinking", message)

  const logOutput = (agentId: string, message: string) =>
    addLog(agentId, "output", message)

  const logError = (agentId: string, message: string) =>
    addLog(agentId, "error", message)

  const logStatus = (agentId: string, message: string) =>
    addLog(agentId, "status", message)

  return {
    logs,
    addLog,
    clearLogs,
    logInfo,
    logThinking,
    logOutput,
    logError,
    logStatus,
  }
}

// Export for SSE integration
export function createLogFromSSE(event: {
  type: string
  agentId?: string
  agent?: string
  message?: string
  content?: string
  thought?: string
  action?: string
  status?: string
  error?: string
}): LogEntry | null {
  const agentId = event.agentId || event.agent || "system"
  let type: LogEntry["type"] = "info"
  let message = ""

  switch (event.type) {
    case "agent_status":
      type = "status"
      message = `Status: ${event.status}${event.action ? ` - ${event.action}` : ""}`
      break
    case "agent_thinking":
      type = "thinking"
      message = event.thought || event.message || "Thinking..."
      break
    case "agent_output":
    case "message":
      type = "output"
      message = event.content || event.message || ""
      break
    case "agent_error":
    case "error":
      type = "error"
      message = event.error || event.message || "Unknown error"
      break
    default:
      return null
  }

  if (!message) return null

  return {
    id: `log-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    timestamp: new Date(),
    agentId,
    type,
    message,
  }
}
