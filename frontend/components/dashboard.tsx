"use client";

import * as React from "react";
import { useState, useRef, useEffect } from "react";
// Custom chat implementation to avoid AI SDK beta issues
import {
  Shield,
  Search,
  Sparkles,
  FileText,
  Settings,
  HelpCircle,
  LogOut,
  Upload,
  Send,
  Plus,
  Scale,
  DollarSign,
  ChevronRight,
} from "lucide-react";
import { authClient } from "@/lib/auth-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader } from "@/components/ui/loader";
import { Markdown } from "@/components/ui/markdown";
import { cn } from "@/lib/utils";
import { DocumentUpload } from "@/components/document-upload";
import { SettingsModal } from "@/components/settings-modal";
import { toast } from "sonner";

// Agent definitions for FlagPilot
const AGENTS = [
  { id: "contract-guardian", name: "Contract Guardian", icon: "🛡️", color: "bg-blue-500", description: "Analyzes contracts for red flags" },
  { id: "job-authenticator", name: "Job Authenticator", icon: "🔍", color: "bg-green-500", description: "Verifies job legitimacy" },
  { id: "payment-enforcer", name: "Payment Enforcer", icon: "💰", color: "bg-yellow-500", description: "Ensures payment security" },
  { id: "talent-vet", name: "Talent Vet", icon: "👤", color: "bg-purple-500", description: "Vets clients and employers" },
  { id: "ghosting-shield", name: "Ghosting Shield", icon: "👻", color: "bg-pink-500", description: "Prevents communication drops" },
  { id: "scope-sentinel", name: "Scope Sentinel", icon: "📏", color: "bg-orange-500", description: "Guards against scope creep" },
  { id: "dispute-mediator", name: "Dispute Mediator", icon: "⚖️", color: "bg-indigo-500", description: "Resolves conflicts fairly" },
  { id: "orchestrator", name: "FlagPilot AI", icon: "🚀", color: "bg-primary", description: "Coordinates all agents" },
];

interface DashboardProps {
  session: {
    user: {
      id: string;
      name: string;
      email: string;
      image?: string;
    };
  };
}

// Simple message type
interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export function Dashboard({ session }: DashboardProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [settingsTab, setSettingsTab] = useState("profile");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const orchestratorAgent = AGENTS.find(a => a.id === "orchestrator") || AGENTS[0];

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userInput = input.trim();
    setInput("");

    // Add user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: userInput,
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Create placeholder for assistant message
    const assistantId = `assistant-${Date.now()}`;
    setMessages(prev => [...prev, { id: assistantId, role: "assistant", content: "" }]);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [...messages, userMessage].map(m => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      if (!response.ok) throw new Error("Chat request failed");

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let fullContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        fullContent += chunk;

        // Update assistant message with streamed content
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantId ? { ...m, content: fullContent } : m
          )
        );
      }
    } catch (error) {
      toast.error("Failed to send message");
      console.error(error);
      // Remove the empty assistant message on error
      setMessages(prev => prev.filter(m => m.id !== assistantId));
    } finally {
      setIsLoading(false);
    }
  };

  const getMessageContent = (message: ChatMessage): string => {
    return message.content;
  };

  const handleSignOut = async () => {
    await authClient.signOut();
    window.location.reload();
  };

  const quickActions = [
    { icon: FileText, label: "Contract Review", prompt: "Review my contract for potential issues", color: "bg-blue-500" },
    { icon: Search, label: "Job Verification", prompt: "Verify this job posting for legitimacy", color: "bg-green-500" },
    { icon: DollarSign, label: "Payment Security", prompt: "Help me secure payment for my project", color: "bg-yellow-500" },
    { icon: Scale, label: "Dispute Resolution", prompt: "I need help resolving a client dispute", color: "bg-purple-500" },
  ];

  return (
    <TooltipProvider>
      <div className="min-h-screen w-full bg-gradient-to-br from-background via-background to-primary/5">
        {/* Background decoration - same as login */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/10 rounded-full blur-3xl" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-primary/5 rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/5 rounded-full blur-3xl" />
        </div>

        {/* Header */}
        <header className="sticky top-0 z-50 border-b bg-background/80 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Logo */}
              <div className="flex items-center gap-2 px-3 py-1.5 bg-primary/10 rounded-full">
                <Shield className="h-5 w-5 text-primary" />
                <span className="font-semibold hidden sm:inline">FlagPilot</span>
              </div>

              {/* Status */}
              <Badge variant="secondary" className="hidden sm:flex">
                <Sparkles className="h-3 w-3 mr-1" />
                {isLoading ? "Processing..." : "Ready"}
              </Badge>
            </div>

            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" onClick={() => setShowUpload(true)} className="hidden sm:flex">
                <Upload className="h-4 w-4 mr-2" />
                Upload
              </Button>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={session.user.image} />
                      <AvatarFallback className="bg-primary text-primary-foreground text-sm">
                        {session.user.name?.[0]?.toUpperCase() || "U"}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-64">
                  <DropdownMenuLabel>
                    <div className="flex items-center gap-3">
                      <Avatar className="h-10 w-10">
                        <AvatarImage src={session.user.image} />
                        <AvatarFallback className="bg-primary text-primary-foreground">
                          {session.user.name?.[0]?.toUpperCase() || "U"}
                        </AvatarFallback>
                      </Avatar>
                      <div className="overflow-hidden">
                        <p className="font-medium truncate">{session.user.name}</p>
                        <p className="text-xs text-muted-foreground truncate">{session.user.email}</p>
                      </div>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => { setSettingsTab("profile"); setShowSettings(true); }}>
                    <Settings className="mr-2 h-4 w-4" />
                    Settings
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => { setSettingsTab("billing"); setShowSettings(true); }}>
                    <DollarSign className="mr-2 h-4 w-4" />
                    Billing
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => { setSettingsTab("help"); setShowSettings(true); }}>
                    <HelpCircle className="mr-2 h-4 w-4" />
                    Help Center
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="text-destructive" onClick={handleSignOut}>
                    <LogOut className="mr-2 h-4 w-4" />
                    Sign Out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-5xl mx-auto px-4 py-8 relative z-10">
          {messages.length === 0 ? (
            /* Empty State - Welcome Screen */
            <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)]">
              {/* Agent Avatars */}
              <div className="flex justify-center -space-x-3 mb-8">
                {AGENTS.slice(0, 5).map((agent, i) => (
                  <Tooltip key={agent.id}>
                    <TooltipTrigger asChild>
                      <div
                        className={`w-14 h-14 ${agent.color} rounded-full flex items-center justify-center text-xl border-4 border-background shadow-lg cursor-pointer hover:scale-110 transition-transform hover:z-10`}
                        style={{ animationDelay: `${i * 100}ms` }}
                      >
                        {agent.icon}
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p className="font-medium">{agent.name}</p>
                      <p className="text-xs text-muted-foreground">{agent.description}</p>
                    </TooltipContent>
                  </Tooltip>
                ))}
              </div>

              <h1 className="text-3xl md:text-4xl font-bold text-center mb-4">
                Protect Your Freelance Career
              </h1>
              <p className="text-muted-foreground text-center max-w-md mb-8">
                13 specialized AI agents working together to analyze contracts,
                verify jobs, and protect your earnings.
              </p>

              {/* Quick Actions */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-2xl mb-8">
                {quickActions.map((action, i) => (
                  <Card
                    key={i}
                    className="cursor-pointer hover:shadow-lg transition-all hover:scale-[1.02] border-border/50 bg-card/50 backdrop-blur-sm"
                    onClick={() => setInput(action.prompt)}
                  >
                    <CardContent className="p-4 flex items-center gap-4">
                      <div className={`w-12 h-12 ${action.color} rounded-xl flex items-center justify-center shadow-lg`}>
                        <action.icon className="h-6 w-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <p className="font-semibold">{action.label}</p>
                        <p className="text-sm text-muted-foreground">AI-powered analysis</p>
                      </div>
                      <ChevronRight className="h-5 w-5 text-muted-foreground" />
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Input Area */}
              <Card className="w-full max-w-2xl border-border/50 bg-card/50 backdrop-blur-sm shadow-xl">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="shrink-0"
                      onClick={() => setShowUpload(true)}
                    >
                      <Plus className="h-5 w-5" />
                    </Button>
                    <Input
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Ask FlagPilot AI to analyze contracts, verify jobs..."
                      className="flex-1 border-0 bg-transparent focus-visible:ring-0 text-base"
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                    />
                    <Button
                      size="icon"
                      className="shrink-0 rounded-xl shadow-lg"
                      onClick={handleSendMessage}
                      disabled={!input.trim() || isLoading}
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            /* Chat View */
            <div className="space-y-6">
              {/* Messages */}
              <div className="space-y-6 pb-32">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={cn(
                      "flex gap-4",
                      message.role === "user" ? "flex-row-reverse" : ""
                    )}
                  >
                    <Avatar className="h-10 w-10 shrink-0 shadow-lg">
                      {message.role === "assistant" ? (
                        <div className={`w-full h-full ${orchestratorAgent.color} flex items-center justify-center text-lg`}>
                          {orchestratorAgent.icon}
                        </div>
                      ) : (
                        <>
                          <AvatarImage src={session.user.image} />
                          <AvatarFallback className="bg-muted">
                            {session.user.name?.[0]?.toUpperCase() || "U"}
                          </AvatarFallback>
                        </>
                      )}
                    </Avatar>
                    <Card
                      className={cn(
                        "flex-1 border-border/50",
                        message.role === "user"
                          ? "bg-primary text-primary-foreground ml-16"
                          : "bg-card/80 backdrop-blur-sm mr-16"
                      )}
                    >
                      <CardContent className="p-4">
                        {message.role === "assistant" && (
                          <div className="flex items-center gap-2 mb-3">
                            <Badge variant="secondary" className="text-xs">
                              {orchestratorAgent.name}
                            </Badge>
                          </div>
                        )}
                        <div className="prose prose-sm dark:prose-invert max-w-none">
                          <Markdown>{getMessageContent(message)}</Markdown>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex gap-4">
                    <Avatar className="h-10 w-10 shrink-0 shadow-lg">
                      <div className="w-full h-full bg-primary flex items-center justify-center text-lg animate-pulse">
                        🚀
                      </div>
                    </Avatar>
                    <Card className="bg-card/80 backdrop-blur-sm border-border/50 mr-16">
                      <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                          <Loader size="sm" />
                          <span className="text-sm text-muted-foreground">Analyzing your request...</span>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Fixed Input */}
              <div className="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-background via-background to-transparent">
                <div className="max-w-3xl mx-auto">
                  <Card className="border-border/50 bg-card/90 backdrop-blur-xl shadow-2xl">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="shrink-0"
                          onClick={() => setShowUpload(true)}
                        >
                          <Plus className="h-5 w-5" />
                        </Button>
                        <Input
                          value={input}
                          onChange={(e) => setInput(e.target.value)}
                          placeholder="Continue the conversation..."
                          className="flex-1 border-0 bg-transparent focus-visible:ring-0 text-base"
                          onKeyDown={(e) => {
                            if (e.key === "Enter" && !e.shiftKey) {
                              e.preventDefault();
                              handleSendMessage();
                            }
                          }}
                        />
                        <Button
                          size="icon"
                          className="shrink-0 rounded-xl shadow-lg"
                          onClick={handleSendMessage}
                          disabled={!input.trim() || isLoading}
                        >
                          <Send className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          )}
        </main>

        {/* Document Upload Modal */}
        {showUpload && (
          <DocumentUpload
            userId={session.user.id}
            onClose={() => setShowUpload(false)}
            onUploadComplete={(doc) => {
              setShowUpload(false);
              setInput(`Analyze the document: ${doc.name}`);
              toast.success("Document uploaded!", { description: doc.name });
            }}
          />
        )}

        {/* Settings Modal */}
        <SettingsModal
          open={showSettings}
          onOpenChange={setShowSettings}
          user={session.user}
          initialTab={settingsTab}
        />
      </div>
    </TooltipProvider>
  );
}
