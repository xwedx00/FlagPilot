'use client';

import * as React from 'react';
import { useRef, useEffect, useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import {
  Send,
  Paperclip,
  ChevronDown,
  FileText,
  X,
  Loader2,
  Bot,
} from 'lucide-react';
import { AgentAvatar, getAgentDisplayName } from './agent-avatar';
import { StreamableLog, LogEntry } from './streamable-log';

export interface ChatMessage {
  id: string;
  role: 'user' | 'agent' | 'system';
  content: string;
  agentId?: string;
  timestamp: Date;
  isThinking?: boolean;
  thinkingText?: string;
  logs?: LogEntry[];
  attachments?: ChatAttachment[];
  artifact?: ChatArtifact;
}

export interface ChatAttachment {
  id: string;
  filename: string;
  contentType: string;
  sizeBytes: number;
  url?: string;
}

export interface ChatArtifact {
  id: string;
  type: 'file' | 'report' | 'analysis';
  title: string;
  description?: string;
  url?: string;
}

interface ChatInterfaceProps {
  messages: ChatMessage[];
  onSend: (message: string, attachments?: File[]) => void;
  isLoading?: boolean;
  placeholder?: string;
  className?: string;
}

/**
 * User message bubble
 */
function UserBubble({ message }: { message: ChatMessage }) {
  return (
    <div className="flex justify-end mb-4 animate-slide-up">
      <div className="fp-bubble-user">
        <p className="whitespace-pre-wrap">{message.content}</p>
        
        {/* Attachments */}
        {message.attachments && message.attachments.length > 0 && (
          <div className="mt-2 pt-2 border-t border-zinc-700 flex flex-wrap gap-2">
            {message.attachments.map((att) => (
              <div
                key={att.id}
                className="flex items-center gap-1.5 text-xs text-zinc-400 bg-zinc-700/50 px-2 py-1 rounded"
              >
                <FileText className="w-3 h-3" />
                <span className="truncate max-w-[100px]">{att.filename}</span>
              </div>
            ))}
          </div>
        )}
        
        <span className="text-[10px] text-zinc-500 mt-1 block">
          {message.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      </div>
    </div>
  );
}

/**
 * Agent message bubble with thinking accordion
 */
function AgentBubble({ message }: { message: ChatMessage }) {
  const [isThinkingOpen, setIsThinkingOpen] = useState(false);
  const agentName = message.agentId
    ? getAgentDisplayName(message.agentId)
    : 'Agent';

  return (
    <div className="flex gap-3 mb-4 animate-slide-up">
      {/* Avatar */}
      <AgentAvatar
        agentId={message.agentId || 'flagpilot'}
        status={message.isThinking ? 'thinking' : 'idle'}
        size="sm"
      />

      <div className="flex-1 min-w-0">
        {/* Agent name */}
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium text-purple-400">
            {agentName}
          </span>
          <span className="text-[10px] text-zinc-500">
            {message.timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>

        {/* Thinking accordion */}
        {(message.isThinking || message.logs) && (
          <Collapsible
            open={isThinkingOpen || message.isThinking}
            onOpenChange={setIsThinkingOpen}
            className="mb-2"
          >
            <CollapsibleTrigger className="flex items-center gap-2 text-xs text-zinc-500 hover:text-zinc-400 transition-colors">
              {message.isThinking && (
                <span className="fp-thinking-dot" />
              )}
              <span>
                {message.thinkingText || `${agentName} is analyzing...`}
              </span>
              <ChevronDown
                className={cn(
                  'w-3 h-3 transition-transform',
                  isThinkingOpen && 'rotate-180'
                )}
              />
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-2">
              {message.logs && message.logs.length > 0 && (
                <StreamableLog
                  logs={message.logs}
                  maxHeight="150px"
                  showTimestamps={false}
                />
              )}
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Message content */}
        {message.content && (
          <div className="fp-bubble-agent">
            <p className="text-zinc-200 whitespace-pre-wrap leading-relaxed">
              {message.content}
            </p>
          </div>
        )}

        {/* Artifact card */}
        {message.artifact && (
          <div className="mt-3 bg-zinc-900/60 backdrop-blur border border-zinc-700 rounded-md p-3 max-w-sm">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-md bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                <FileText className="w-5 h-5 text-purple-400" />
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium truncate">
                  {message.artifact.title}
                </h4>
                {message.artifact.description && (
                  <p className="text-xs text-zinc-400 mt-0.5 line-clamp-2">
                    {message.artifact.description}
                  </p>
                )}
                <button className="text-xs text-purple-400 hover:text-purple-300 mt-1.5 font-medium">
                  View Artifact →
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * System message
 */
function SystemMessage({ message }: { message: ChatMessage }) {
  return (
    <div className="flex justify-center my-4">
      <span className="text-xs text-zinc-500 bg-zinc-800/50 px-3 py-1 rounded-full">
        {message.content}
      </span>
    </div>
  );
}

/**
 * ChatInterface - Main chat component for the War Room
 * 
 * Features:
 * - User/Agent message bubbles
 * - Thinking accordion with log stream
 * - File attachment support
 * - Auto-expanding textarea
 * - Drag & drop files
 * 
 * @example
 * <ChatInterface
 *   messages={messages}
 *   onSend={(msg, files) => handleSend(msg, files)}
 *   isLoading={isAgentThinking}
 * />
 */
export function ChatInterface({
  messages,
  onSend,
  isLoading = false,
  placeholder = 'Message FlagPilot...',
  className,
}: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        150
      )}px`;
    }
  }, [input]);

  const handleSend = useCallback(() => {
    if (!input.trim() && attachments.length === 0) return;
    onSend(input.trim(), attachments.length > 0 ? attachments : undefined);
    setInput('');
    setAttachments([]);
  }, [input, attachments, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setAttachments((prev) => [...prev, ...files]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    setAttachments((prev) => [...prev, ...files]);
  };

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div
      className={cn('flex flex-col h-full', className)}
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      {/* Drop overlay */}
      {isDragging && (
        <div className="absolute inset-0 bg-purple-500/10 border-2 border-dashed border-purple-500 rounded-md z-10 flex items-center justify-center">
          <p className="text-purple-400 font-medium">Drop files here</p>
        </div>
      )}

      {/* Messages area */}
      <ScrollArea ref={scrollRef} className="flex-1 px-4 pt-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <Bot className="w-12 h-12 text-zinc-600 mb-4" />
            <h3 className="text-lg font-medium text-zinc-400 mb-2">
              Start a Mission
            </h3>
            <p className="text-sm text-zinc-500 max-w-xs">
              Ask FlagPilot to review a contract, research a client, or draft a
              response.
            </p>
          </div>
        ) : (
          messages.map((message) => {
            if (message.role === 'user') {
              return <UserBubble key={message.id} message={message} />;
            }
            if (message.role === 'system') {
              return <SystemMessage key={message.id} message={message} />;
            }
            return <AgentBubble key={message.id} message={message} />;
          })
        )}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex items-center gap-2 text-zinc-500 text-sm mb-4">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>FlagPilot is thinking...</span>
          </div>
        )}
      </ScrollArea>

      {/* Input area */}
      <div className="border-t border-zinc-800 p-4">
        {/* Attachments preview */}
        {attachments.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {attachments.map((file, index) => (
              <div
                key={index}
                className="flex items-center gap-2 bg-zinc-800 px-2 py-1 rounded text-xs"
              >
                <FileText className="w-3 h-3 text-zinc-400" />
                <span className="truncate max-w-[120px]">{file.name}</span>
                <button
                  onClick={() => removeAttachment(index)}
                  className="text-zinc-500 hover:text-zinc-300"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="flex items-end gap-2">
          {/* File attachment button */}
          <input
            ref={fileInputRef}
            type="file"
            multiple
            className="hidden"
            onChange={handleFileSelect}
          />
          <Button
            variant="ghost"
            size="icon"
            onClick={() => fileInputRef.current?.click()}
            className="text-zinc-400 hover:text-zinc-200 flex-shrink-0"
          >
            <Paperclip className="w-5 h-5" />
          </Button>

          {/* Textarea */}
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isLoading}
            className={cn(
              'flex-1 min-h-[44px] max-h-[150px] resize-none',
              'bg-zinc-900 border-zinc-700 focus:border-purple-500',
              'text-sm placeholder:text-zinc-500'
            )}
            rows={1}
          />

          {/* Send button */}
          <Button
            onClick={handleSend}
            disabled={isLoading || (!input.trim() && attachments.length === 0)}
            className={cn(
              'flex-shrink-0 active:scale-[0.98] transition-transform',
              'bg-purple-600 hover:bg-purple-500 text-white'
            )}
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
