"use client";

import { useState, useEffect } from "react";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Loader } from "@/components/ui/loader";
import {
  User,
  Settings,
  CreditCard,
  BarChart3,
  HelpCircle,
  Shield,
  Upload,
  Download,
  Trash2,
  FileText,
  Globe,
  Bell,
  Palette,
  Database,
  Lock,
  MessageSquare,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  Copy,
  BookOpen,
  Scale,
  Zap,
  Brain,
  Key,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";

interface SettingsModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  user: {
    id: string;
    name: string;
    email: string;
    image?: string;
  };
  initialTab?: string;
}

// Knowledge context presets
const KNOWLEDGE_PRESETS = [
  { id: "eu-gdpr", name: "EU GDPR Guidelines", type: "eu-law", description: "European data protection regulations" },
  { id: "eu-freelance", name: "EU Freelance Laws", type: "eu-law", description: "Freelancer rights and obligations in EU" },
  { id: "contract-templates", name: "Contract Templates", type: "contract-template", description: "Standard freelance contract clauses" },
  { id: "payment-terms", name: "Payment Protection", type: "payment", description: "Best practices for payment security" },
  { id: "ip-rights", name: "IP Rights Guide", type: "legal", description: "Intellectual property for freelancers" },
];

const AI_MODELS = [
  { value: "google/gemini-2.0-flash-001", label: "Gemini 2.0 Flash (Fast)" },
  { value: "google/gemini-pro", label: "Gemini Pro (Balanced)" },
  { value: "anthropic/claude-3-haiku", label: "Claude 3 Haiku (Fast)" },
  { value: "anthropic/claude-3-sonnet", label: "Claude 3 Sonnet (Balanced)" },
  { value: "openai/gpt-4o-mini", label: "GPT-4o Mini (Fast)" },
  { value: "openai/gpt-4o", label: "GPT-4o (Powerful)" },
];

const TIMEZONES = [
  { value: "UTC", label: "UTC (Coordinated Universal Time)" },
  { value: "America/New_York", label: "Eastern Time (US & Canada)" },
  { value: "America/Los_Angeles", label: "Pacific Time (US & Canada)" },
  { value: "Europe/London", label: "London (GMT)" },
  { value: "Europe/Paris", label: "Central European Time" },
  { value: "Asia/Tokyo", label: "Japan Standard Time" },
  { value: "Asia/Shanghai", label: "China Standard Time" },
  { value: "Australia/Sydney", label: "Australian Eastern Time" },
];

const LANGUAGES = [
  { value: "en", label: "English" },
  { value: "es", label: "Español" },
  { value: "fr", label: "Français" },
  { value: "de", label: "Deutsch" },
  { value: "pt", label: "Português" },
  { value: "zh", label: "中文" },
  { value: "ja", label: "日本語" },
];

export function SettingsModal({ open, onOpenChange, user, initialTab = "profile" }: SettingsModalProps) {
  const [activeTab, setActiveTab] = useState(initialTab);
  const [isSaving, setIsSaving] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  
  // Profile state
  const [profile, setProfile] = useState({
    displayName: user.name || "",
    email: user.email || "",
    bio: "",
    freelanceType: "",
    experienceLevel: "",
    hourlyRate: "",
    portfolioUrl: "",
    timezone: "UTC",
    language: "en",
  });

  // Preferences state
  const [preferences, setPreferences] = useState({
    aiModel: "google/gemini-2.0-flash-001",
    aiTemperature: "0.7",
    maxTokens: 4096,
    theme: "system",
    emailNotifications: true,
    agentAlerts: true,
    weeklyDigest: false,
    allowAnalytics: true,
    allowDataSharing: false,
    gdprConsent: false,
    dataRetentionDays: 90,
  });

  // Knowledge contexts
  const [knowledgeContexts, setKnowledgeContexts] = useState<Array<{
    id: string;
    name: string;
    type: string;
    isActive: boolean;
  }>>([]);

  // Usage stats (mock data)
  const [usageStats] = useState({
    chatMessages: 147,
    agentCalls: 42,
    documentsAnalyzed: 12,
    tokensUsed: 125000,
    tokensLimit: 500000,
    currentPlan: "Free",
    nextBillingDate: null as Date | null,
  });

  useEffect(() => {
    if (initialTab) {
      setActiveTab(initialTab);
    }
  }, [initialTab]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Save to API
      const response = await fetch("/api/user/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId: user.id,
          ...profile,
          gdprConsent: preferences.gdprConsent,
          emailNotifications: preferences.emailNotifications,
          agentAlerts: preferences.agentAlerts,
        }),
      });
      
      if (!response.ok) throw new Error("Failed to save");
      
      toast.success("Settings saved!", {
        description: "Your preferences have been updated.",
      });
    } catch (error) {
      console.error("Failed to save settings:", error);
      toast.error("Failed to save", {
        description: "Please try again later.",
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleExportData = async () => {
    const data = {
      profile,
      preferences,
      knowledgeContexts,
      exportDate: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `flagpilot-export-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Data exported!", {
      description: "Your data has been downloaded.",
    });
  };

  const handleImportData = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      if (data.profile) setProfile(prev => ({ ...prev, ...data.profile }));
      if (data.preferences) setPreferences(prev => ({ ...prev, ...data.preferences }));
      toast.success("Data imported!", {
        description: "Your settings have been restored.",
      });
    } catch (error) {
      console.error("Failed to import data:", error);
      toast.error("Import failed", {
        description: "Invalid file format.",
      });
    }
  };

  const handleDeleteAccount = async () => {
    try {
      await fetch(`/api/user/profile?userId=${user.id}`, { method: "DELETE" });
      toast.success("Account deleted", {
        description: "Your data has been removed.",
      });
      setShowDeleteConfirm(false);
      onOpenChange(false);
      window.location.reload();
    } catch {
      toast.error("Failed to delete account");
    }
  };

  const toggleKnowledgeContext = (id: string) => {
    setKnowledgeContexts(prev => 
      prev.map(ctx => ctx.id === id ? { ...ctx, isActive: !ctx.isActive } : ctx)
    );
  };

  const addKnowledgePreset = (preset: typeof KNOWLEDGE_PRESETS[0]) => {
    if (!knowledgeContexts.find(c => c.id === preset.id)) {
      setKnowledgeContexts(prev => [...prev, { ...preset, isActive: true }]);
      toast.success(`${preset.name} added!`, {
        description: "Knowledge context is now active.",
        duration: 2000,
      });
    } else {
      toast.info("Already added", { duration: 1500 });
    }
  };

  const removeKnowledgeContext = (id: string) => {
    const ctx = knowledgeContexts.find(c => c.id === id);
    setKnowledgeContexts(prev => prev.filter(c => c.id !== id));
    toast.success(`${ctx?.name || 'Context'} removed`, { duration: 1500 });
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full sm:max-w-4xl p-0 gap-0 overflow-hidden">
        <div className="flex h-full">
          {/* Sidebar */}
          <div className="w-56 bg-muted/30 border-r p-4 flex flex-col">
            <SheetHeader className="mb-4">
              <SheetTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Settings
              </SheetTitle>
            </SheetHeader>
            
            <nav className="space-y-1 flex-1">
              <TooltipProvider>
                {[
                  { id: "profile", icon: User, label: "Profile", desc: "Personal information" },
                  { id: "ai-settings", icon: Brain, label: "AI Settings", desc: "Model configuration" },
                  { id: "knowledge", icon: BookOpen, label: "Knowledge Base", desc: "EU laws & context" },
                  { id: "usage", icon: BarChart3, label: "Usage", desc: "Your activity stats" },
                  { id: "billing", icon: CreditCard, label: "Billing", desc: "Plans & payments" },
                  { id: "notifications", icon: Bell, label: "Notifications", desc: "Alert preferences" },
                  { id: "privacy", icon: Lock, label: "Privacy & Data", desc: "GDPR & export" },
                  { id: "help", icon: HelpCircle, label: "Help Center", desc: "Support & docs" },
                  { id: "account", icon: AlertTriangle, label: "Account", desc: "Danger zone" },
                ].map((item, idx) => (
                  <Tooltip key={item.id}>
                    <TooltipTrigger asChild>
                      <button
                        onClick={() => setActiveTab(item.id)}
                        style={{ animationDelay: `${idx * 30}ms` }}
                        className={cn(
                          "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium",
                          "transition-all duration-200 animate-in fade-in slide-in-from-left-2",
                          "hover:scale-[1.02] active:scale-[0.98]",
                          activeTab === item.id
                            ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
                            : "text-muted-foreground hover:bg-muted hover:text-foreground"
                        )}
                      >
                        <item.icon className={cn(
                          "h-4 w-4 transition-transform duration-200",
                          activeTab === item.id && "scale-110"
                        )} />
                        {item.label}
                        {item.id === "account" && (
                          <span className="ml-auto text-xs text-destructive">!</span>
                        )}
                      </button>
                    </TooltipTrigger>
                    <TooltipContent side="right">
                      <p className="text-xs">{item.desc}</p>
                    </TooltipContent>
                  </Tooltip>
                ))}
              </TooltipProvider>
            </nav>

            <Separator className="my-4" />
            
            <Button 
              onClick={handleSave} 
              disabled={isSaving} 
              className={cn(
                "w-full transition-all duration-200",
                "hover:scale-[1.02] active:scale-[0.98]",
                !isSaving && "shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30"
              )}
            >
              {isSaving ? (
                <Loader size="sm" className="mr-2" />
              ) : (
                <CheckCircle2 className="h-4 w-4 mr-2" />
              )}
              {isSaving ? "Saving..." : "Save Changes"}
            </Button>
          </div>

          {/* Content */}
          <ScrollArea className="flex-1 p-6">
            {/* Profile Tab */}
            {activeTab === "profile" && (
              <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                <div className="flex items-center gap-3 p-4 rounded-xl bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/20">
                  <User className="h-5 w-5 text-primary" />
                  <div>
                    <h3 className="font-semibold">Profile Settings</h3>
                    <p className="text-xs text-muted-foreground">
                      Manage your personal information and preferences
                    </p>
                  </div>
                </div>

                <Card className="transition-all duration-200 hover:shadow-md">
                  <CardHeader>
                    <CardTitle className="text-base">Personal Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="displayName">Display Name</Label>
                        <Input
                          id="displayName"
                          value={profile.displayName}
                          onChange={e => setProfile({ ...profile, displayName: e.target.value })}
                          className="transition-all duration-200 focus:scale-[1.01] focus:shadow-lg"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="email" className="flex items-center gap-2">
                          Email
                          <HoverCard>
                            <HoverCardTrigger>
                              <Lock className="h-3 w-3 text-muted-foreground cursor-help" />
                            </HoverCardTrigger>
                            <HoverCardContent className="w-48">
                              <p className="text-xs">Email cannot be changed. Contact support if needed.</p>
                            </HoverCardContent>
                          </HoverCard>
                        </Label>
                        <Input
                          id="email"
                          value={profile.email}
                          disabled
                          className="bg-muted cursor-not-allowed"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="bio">Bio</Label>
                      <Textarea
                        id="bio"
                        placeholder="Tell us about yourself and your work..."
                        value={profile.bio}
                        onChange={e => setProfile({ ...profile, bio: e.target.value })}
                        rows={3}
                        className="transition-all duration-200 focus:scale-[1.005] focus:shadow-lg"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="freelanceType">Freelance Type</Label>
                        <Select
                          value={profile.freelanceType}
                          onValueChange={v => setProfile({ ...profile, freelanceType: v })}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select type" />
                          </SelectTrigger>
                          <SelectContent>
                            {["Web Developer", "Mobile Developer", "UI/UX Designer", "Content Writer", "Consultant", "Other"].map(type => (
                              <SelectItem key={type} value={type}>{type}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="hourlyRate">Hourly Rate (USD)</Label>
                        <Input
                          id="hourlyRate"
                          type="number"
                          placeholder="e.g., 50"
                          value={profile.hourlyRate}
                          onChange={e => setProfile({ ...profile, hourlyRate: e.target.value })}
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="portfolioUrl">Portfolio URL</Label>
                      <Input
                        id="portfolioUrl"
                        type="url"
                        placeholder="https://yourportfolio.com"
                        value={profile.portfolioUrl}
                        onChange={e => setProfile({ ...profile, portfolioUrl: e.target.value })}
                      />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Regional Settings</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>Timezone</Label>
                        <Select
                          value={profile.timezone}
                          onValueChange={v => setProfile({ ...profile, timezone: v })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {TIMEZONES.map(tz => (
                              <SelectItem key={tz.value} value={tz.value}>{tz.label}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label>Language</Label>
                        <Select
                          value={profile.language}
                          onValueChange={v => setProfile({ ...profile, language: v })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {LANGUAGES.map(lang => (
                              <SelectItem key={lang.value} value={lang.value}>{lang.label}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* AI Settings Tab */}
            {activeTab === "ai-settings" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <Brain className="h-5 w-5" />
                    AI Settings
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Configure how FlagPilot AI agents work for you
                  </p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Model Selection</CardTitle>
                    <CardDescription>Choose the AI model that best fits your needs</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label>AI Model</Label>
                      <Select
                        value={preferences.aiModel}
                        onValueChange={v => setPreferences({ ...preferences, aiModel: v })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {AI_MODELS.map(model => (
                            <SelectItem key={model.value} value={model.value}>{model.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>Response Style (Temperature: {preferences.aiTemperature})</Label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={preferences.aiTemperature}
                        onChange={e => setPreferences({ ...preferences, aiTemperature: e.target.value })}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Precise</span>
                        <span>Creative</span>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label>Max Response Length</Label>
                      <Select
                        value={String(preferences.maxTokens)}
                        onValueChange={v => setPreferences({ ...preferences, maxTokens: parseInt(v) })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="2048">Short (2K tokens)</SelectItem>
                          <SelectItem value="4096">Medium (4K tokens)</SelectItem>
                          <SelectItem value="8192">Long (8K tokens)</SelectItem>
                          <SelectItem value="16384">Very Long (16K tokens)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Agent Configuration</CardTitle>
                    <CardDescription>Customize individual agent behaviors</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-3">
                      {[
                        { id: "contract-guardian", name: "Contract Guardian", icon: "🛡️" },
                        { id: "job-authenticator", name: "Job Authenticator", icon: "🔍" },
                        { id: "payment-enforcer", name: "Payment Enforcer", icon: "💰" },
                        { id: "scope-sentinel", name: "Scope Sentinel", icon: "📏" },
                        { id: "dispute-mediator", name: "Dispute Mediator", icon: "⚖️" },
                        { id: "talent-vet", name: "Talent Vet", icon: "👤" },
                      ].map(agent => (
                        <div key={agent.id} className="flex items-center justify-between p-3 rounded-lg border">
                          <div className="flex items-center gap-2">
                            <span className="text-xl">{agent.icon}</span>
                            <span className="text-sm font-medium">{agent.name}</span>
                          </div>
                          <Switch defaultChecked />
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Knowledge Base Tab */}
            {activeTab === "knowledge" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <BookOpen className="h-5 w-5" />
                    Knowledge Base
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Upload context and legal documents for better AI assistance
                  </p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Quick Add - Legal & Compliance</CardTitle>
                    <CardDescription>Add pre-built knowledge contexts</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 gap-2">
                      {KNOWLEDGE_PRESETS.map(preset => (
                        <div key={preset.id} className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50 transition-colors">
                          <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-primary/10">
                              {preset.type === "eu-law" ? <Scale className="h-4 w-4 text-primary" /> : <FileText className="h-4 w-4 text-primary" />}
                            </div>
                            <div>
                              <p className="font-medium text-sm">{preset.name}</p>
                              <p className="text-xs text-muted-foreground">{preset.description}</p>
                            </div>
                          </div>
                          <Button
                            size="sm"
                            variant={knowledgeContexts.find(c => c.id === preset.id) ? "secondary" : "outline"}
                            onClick={() => addKnowledgePreset(preset)}
                            disabled={!!knowledgeContexts.find(c => c.id === preset.id)}
                          >
                            {knowledgeContexts.find(c => c.id === preset.id) ? "Added" : "Add"}
                          </Button>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Upload Custom Documents</CardTitle>
                    <CardDescription>Add your own contracts, templates, or guidelines</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="border-2 border-dashed rounded-lg p-8 text-center">
                      <Upload className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                      <p className="text-sm font-medium">Drop files here or click to upload</p>
                      <p className="text-xs text-muted-foreground mt-1">PDF, TXT, DOC up to 10MB</p>
                      <Button variant="outline" className="mt-4">
                        <Upload className="h-4 w-4 mr-2" />
                        Upload Document
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {knowledgeContexts.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Active Knowledge Contexts</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {knowledgeContexts.map(ctx => (
                          <div key={ctx.id} className="flex items-center justify-between p-3 rounded-lg border">
                            <div className="flex items-center gap-2">
                              <FileText className="h-4 w-4 text-muted-foreground" />
                              <span className="text-sm font-medium">{ctx.name}</span>
                              <Badge variant="secondary" className="text-xs">{ctx.type}</Badge>
                            </div>
                            <div className="flex items-center gap-2">
                              <Switch
                                checked={ctx.isActive}
                                onCheckedChange={() => toggleKnowledgeContext(ctx.id)}
                              />
                              <Button size="icon" variant="ghost" className="h-8 w-8 text-destructive">
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}

            {/* Usage Tab */}
            {activeTab === "usage" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    Usage Statistics
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Track your FlagPilot usage and limits
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardContent className="pt-6">
                      <div className="flex items-center gap-3">
                        <div className="p-3 rounded-lg bg-blue-500/10">
                          <MessageSquare className="h-5 w-5 text-blue-500" />
                        </div>
                        <div>
                          <p className="text-2xl font-bold">{usageStats.chatMessages}</p>
                          <p className="text-sm text-muted-foreground">Chat Messages</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="pt-6">
                      <div className="flex items-center gap-3">
                        <div className="p-3 rounded-lg bg-purple-500/10">
                          <Sparkles className="h-5 w-5 text-purple-500" />
                        </div>
                        <div>
                          <p className="text-2xl font-bold">{usageStats.agentCalls}</p>
                          <p className="text-sm text-muted-foreground">Agent Calls</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="pt-6">
                      <div className="flex items-center gap-3">
                        <div className="p-3 rounded-lg bg-green-500/10">
                          <FileText className="h-5 w-5 text-green-500" />
                        </div>
                        <div>
                          <p className="text-2xl font-bold">{usageStats.documentsAnalyzed}</p>
                          <p className="text-sm text-muted-foreground">Documents Analyzed</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="pt-6">
                      <div className="flex items-center gap-3">
                        <div className="p-3 rounded-lg bg-orange-500/10">
                          <Zap className="h-5 w-5 text-orange-500" />
                        </div>
                        <div>
                          <p className="text-2xl font-bold">{(usageStats.tokensUsed / 1000).toFixed(0)}K</p>
                          <p className="text-sm text-muted-foreground">Tokens Used</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Token Usage</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>{usageStats.tokensUsed.toLocaleString()} used</span>
                        <span>{usageStats.tokensLimit.toLocaleString()} limit</span>
                      </div>
                      <Progress value={(usageStats.tokensUsed / usageStats.tokensLimit) * 100} />
                      <p className="text-xs text-muted-foreground">
                        {((usageStats.tokensLimit - usageStats.tokensUsed) / 1000).toFixed(0)}K tokens remaining this month
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Billing Tab */}
            {activeTab === "billing" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <CreditCard className="h-5 w-5" />
                    Billing & Subscription
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Manage your subscription and payment methods
                  </p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Current Plan</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between p-4 rounded-lg bg-muted/50">
                      <div>
                        <p className="font-semibold text-lg">{usageStats.currentPlan} Plan</p>
                        <p className="text-sm text-muted-foreground">500K tokens/month included</p>
                      </div>
                      <Button>Upgrade Plan</Button>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Available Plans</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-3 gap-4">
                      {[
                        { name: "Free", price: "$0", tokens: "500K", features: ["Basic agents", "5 documents", "Community support"] },
                        { name: "Pro", price: "$19", tokens: "2M", features: ["All agents", "Unlimited docs", "Priority support"], popular: true },
                        { name: "Team", price: "$49", tokens: "5M", features: ["Everything in Pro", "Team features", "API access"] },
                      ].map(plan => (
                        <div
                          key={plan.name}
                          className={cn(
                            "p-4 rounded-lg border",
                            plan.popular && "border-primary ring-1 ring-primary"
                          )}
                        >
                          {plan.popular && (
                            <Badge className="mb-2">Popular</Badge>
                          )}
                          <p className="font-semibold">{plan.name}</p>
                          <p className="text-2xl font-bold">{plan.price}<span className="text-sm font-normal text-muted-foreground">/mo</span></p>
                          <p className="text-xs text-muted-foreground mb-3">{plan.tokens} tokens/month</p>
                          <ul className="space-y-1 text-xs">
                            {plan.features.map(f => (
                              <li key={f} className="flex items-center gap-1">
                                <CheckCircle2 className="h-3 w-3 text-green-500" />
                                {f}
                              </li>
                            ))}
                          </ul>
                          <Button variant={plan.popular ? "default" : "outline"} size="sm" className="w-full mt-3">
                            {plan.name === usageStats.currentPlan ? "Current" : "Select"}
                          </Button>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Notifications Tab */}
            {activeTab === "notifications" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <Bell className="h-5 w-5" />
                    Notification Preferences
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Control how and when you receive notifications
                  </p>
                </div>

                <Card>
                  <CardContent className="pt-6 space-y-4">
                    {[
                      { key: "emailNotifications", label: "Email Notifications", desc: "Receive important updates via email" },
                      { key: "agentAlerts", label: "Agent Alerts", desc: "Get notified when agents detect risks" },
                      { key: "weeklyDigest", label: "Weekly Digest", desc: "Weekly summary of your activity" },
                    ].map(item => (
                      <div key={item.key} className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-sm">{item.label}</p>
                          <p className="text-xs text-muted-foreground">{item.desc}</p>
                        </div>
                        <Switch
                          checked={preferences[item.key as keyof typeof preferences] as boolean}
                          onCheckedChange={v => setPreferences({ ...preferences, [item.key]: v })}
                        />
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Privacy Tab */}
            {activeTab === "privacy" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <Lock className="h-5 w-5" />
                    Privacy & Data
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Control your data and privacy settings
                  </p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Data Collection</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-sm">Analytics</p>
                        <p className="text-xs text-muted-foreground">Help improve FlagPilot with anonymous usage data</p>
                      </div>
                      <Switch
                        checked={preferences.allowAnalytics}
                        onCheckedChange={v => setPreferences({ ...preferences, allowAnalytics: v })}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-sm">Data Sharing</p>
                        <p className="text-xs text-muted-foreground">Share anonymized data for AI training</p>
                      </div>
                      <Switch
                        checked={preferences.allowDataSharing}
                        onCheckedChange={v => setPreferences({ ...preferences, allowDataSharing: v })}
                      />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">GDPR Compliance</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
                      <div className="flex items-start gap-3">
                        <Scale className="h-5 w-5 text-blue-500 mt-0.5" />
                        <div>
                          <p className="font-medium text-sm">EU Data Protection</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            Your data is processed in compliance with GDPR. You have the right to access, rectify, and delete your personal data.
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-sm">GDPR Consent</p>
                        <p className="text-xs text-muted-foreground">I consent to data processing as described</p>
                      </div>
                      <Switch
                        checked={preferences.gdprConsent}
                        onCheckedChange={v => setPreferences({ ...preferences, gdprConsent: v })}
                      />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Data Retention</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <Label>Keep my data for</Label>
                      <Select
                        value={String(preferences.dataRetentionDays)}
                        onValueChange={v => setPreferences({ ...preferences, dataRetentionDays: parseInt(v) })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="30">30 days</SelectItem>
                          <SelectItem value="90">90 days</SelectItem>
                          <SelectItem value="180">6 months</SelectItem>
                          <SelectItem value="365">1 year</SelectItem>
                          <SelectItem value="-1">Forever</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Export & Import</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Button variant="outline" className="w-full" onClick={handleExportData}>
                      <Download className="h-4 w-4 mr-2" />
                      Export All Data
                    </Button>
                    <div className="relative">
                      <input
                        type="file"
                        accept=".json"
                        onChange={handleImportData}
                        className="absolute inset-0 opacity-0 cursor-pointer"
                      />
                      <Button variant="outline" className="w-full">
                        <Upload className="h-4 w-4 mr-2" />
                        Import Data
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Help Tab */}
            {activeTab === "help" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <HelpCircle className="h-5 w-5" />
                    Help Center
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Get help and learn how to use FlagPilot
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {[
                    { icon: BookOpen, title: "Documentation", desc: "Learn how to use FlagPilot", link: "#" },
                    { icon: MessageSquare, title: "Contact Support", desc: "Get help from our team", link: "#" },
                    { icon: Sparkles, title: "Feature Requests", desc: "Suggest new features", link: "#" },
                    { icon: Shield, title: "Security", desc: "Report security issues", link: "#" },
                  ].map(item => (
                    <Card key={item.title} className="cursor-pointer hover:bg-muted/50 transition-colors">
                      <CardContent className="pt-6">
                        <div className="flex items-start gap-3">
                          <div className="p-2 rounded-lg bg-primary/10">
                            <item.icon className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                            <p className="font-medium text-sm">{item.title}</p>
                            <p className="text-xs text-muted-foreground">{item.desc}</p>
                          </div>
                          <ExternalLink className="h-4 w-4 text-muted-foreground ml-auto" />
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Frequently Asked Questions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {[
                      "How do I analyze a contract?",
                      "What are the different AI agents?",
                      "How is my data protected?",
                      "Can I use FlagPilot for free?",
                    ].map((q, i) => (
                      <div key={i} className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50 cursor-pointer">
                        <span className="text-sm">{q}</span>
                        <ExternalLink className="h-4 w-4 text-muted-foreground" />
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Account Tab */}
            {activeTab === "account" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold flex items-center gap-2 text-destructive">
                    <AlertTriangle className="h-5 w-5" />
                    Account Management
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Manage your account settings and data
                  </p>
                </div>

                <Card className="border-destructive/50">
                  <CardHeader>
                    <CardTitle className="text-base text-destructive">Danger Zone</CardTitle>
                    <CardDescription>Irreversible actions for your account</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="p-4 rounded-lg border border-destructive/50 bg-destructive/5">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium text-sm">Delete Account</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            Permanently delete your account and all associated data. This action cannot be undone.
                          </p>
                        </div>
                        <AlertDialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
                          <AlertDialogTrigger asChild>
                            <Button variant="destructive" size="sm">
                              <Trash2 className="h-4 w-4 mr-2" />
                              Delete
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                              <AlertDialogDescription>
                                This action cannot be undone. This will permanently delete your account and remove all your data from our servers including:
                                <ul className="list-disc list-inside mt-2 space-y-1">
                                  <li>All chat history</li>
                                  <li>Uploaded documents</li>
                                  <li>Profile and preferences</li>
                                  <li>Subscription data</li>
                                </ul>
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>Cancel</AlertDialogCancel>
                              <AlertDialogAction
                                onClick={handleDeleteAccount}
                                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                              >
                                Yes, delete my account
                              </AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      </div>
                    </div>

                    <div className="p-4 rounded-lg border">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium text-sm">Clear All Data</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            Delete all your chats, documents, and preferences while keeping your account.
                          </p>
                        </div>
                        <Button variant="outline" size="sm">
                          Clear Data
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </ScrollArea>
        </div>
      </SheetContent>
    </Sheet>
  );
}
