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
import { Loader } from "@/components/ui/loader";
import { Card, CardContent } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { 
  Shield, 
  User, 
  Briefcase, 
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Globe,
  Bell,
  Lock,
  Scale,
  Brain,
  Zap,
  Check,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

interface OnboardingModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  user: {
    id: string;
    name: string;
    email: string;
    image?: string;
  };
  onComplete: () => void;
}

const FREELANCE_TYPES = [
  "Web Developer", "Mobile Developer", "Full Stack Developer", "UI/UX Designer",
  "Graphic Designer", "Content Writer", "Copywriter", "Video Editor",
  "Virtual Assistant", "Social Media Manager", "SEO Specialist", "Data Analyst",
  "Project Manager", "Consultant", "Other",
];

const EXPERIENCE_LEVELS = [
  { value: "beginner", label: "Beginner", desc: "0-1 years", icon: "🌱" },
  { value: "intermediate", label: "Intermediate", desc: "2-4 years", icon: "📈" },
  { value: "experienced", label: "Experienced", desc: "5-9 years", icon: "⭐" },
  { value: "expert", label: "Expert", desc: "10+ years", icon: "🏆" },
];

const PLATFORMS = [
  { id: "upwork", name: "Upwork", icon: "💼" },
  { id: "fiverr", name: "Fiverr", icon: "🎯" },
  { id: "toptal", name: "Toptal", icon: "🔝" },
  { id: "freelancer", name: "Freelancer", icon: "🌐" },
  { id: "direct", name: "Direct Clients", icon: "🤝" },
  { id: "linkedin", name: "LinkedIn", icon: "💼" },
];

const PROTECTION_PRIORITIES = [
  { id: "contracts", name: "Contracts", icon: "📜", color: "bg-blue-500" },
  { id: "payments", name: "Payments", icon: "💰", color: "bg-yellow-500" },
  { id: "scams", name: "Scam Detection", icon: "🔍", color: "bg-red-500" },
  { id: "scope", name: "Scope Creep", icon: "📏", color: "bg-orange-500" },
  { id: "disputes", name: "Disputes", icon: "⚖️", color: "bg-purple-500" },
];

export function OnboardingModal({ open, onOpenChange, user, onComplete }: OnboardingModalProps) {
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    displayName: user.name || "",
    freelanceType: "",
    experienceLevel: "",
    platforms: [] as string[],
    hourlyRate: "",
    protectionPriorities: [] as string[],
    gdprConsent: false,
    emailNotifications: true,
  });

  const totalSteps = 4;
  const progress = (step / totalSteps) * 100;

  const handleNext = () => {
    if (step < totalSteps) {
      setStep(step + 1);
      toast.success(`Step ${step} completed!`, { duration: 1500 });
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleComplete = async () => {
    setIsLoading(true);
    
    try {
      await fetch("/api/user/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId: user.id,
          ...formData,
          platforms: JSON.stringify(formData.platforms),
          protectionPriorities: JSON.stringify(formData.protectionPriorities),
          onboardingCompleted: true,
        }),
      });
      
      localStorage.setItem(`onboarding_completed_${user.id}`, "true");
      onComplete();
    } catch (error) {
      localStorage.setItem(`onboarding_completed_${user.id}`, "true");
      onComplete();
    } finally {
      setIsLoading(false);
    }
  };

  const toggleItem = (list: string[], item: string, key: 'platforms' | 'protectionPriorities') => {
    setFormData((prev) => ({
      ...prev,
      [key]: prev[key].includes(item)
        ? prev[key].filter((p) => p !== item)
        : [...prev[key], item],
    }));
  };

  const canProceed = () => {
    switch (step) {
      case 1: return formData.displayName && formData.freelanceType && formData.experienceLevel;
      case 2: return formData.platforms.length > 0;
      case 3: return formData.protectionPriorities.length > 0;
      case 4: return formData.gdprConsent;
      default: return false;
    }
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent 
        side="bottom" 
        className="h-[85vh] rounded-t-3xl"
        onPointerDownOutside={(e) => e.preventDefault()}
        onEscapeKeyDown={(e) => e.preventDefault()}
      >
        <div className="max-w-4xl mx-auto h-full flex flex-col">
          {/* Header */}
          <SheetHeader className="pb-4 border-b">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-primary/10">
                  <Shield className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <SheetTitle className="text-xl">Welcome to FlagPilot</SheetTitle>
                  <SheetDescription>Let's set up your AI protection in {totalSteps} quick steps</SheetDescription>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-sm font-medium">Step {step} of {totalSteps}</p>
                  <p className="text-xs text-muted-foreground">{Math.round(progress)}% complete</p>
                </div>
              </div>
            </div>
            <Progress value={progress} className="h-2 mt-4" />
          </SheetHeader>

          {/* Content */}
          <div className="flex-1 overflow-y-auto py-6">
            {/* Step 1: Profile */}
            {step === 1 && (
              <div className="grid md:grid-cols-2 gap-8 animate-in fade-in slide-in-from-right-4 duration-300">
                <div className="space-y-6">
                  <div className="flex items-center gap-3 p-4 rounded-xl bg-primary/5 border border-primary/20">
                    <User className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-semibold">Tell us about yourself</p>
                      <p className="text-xs text-muted-foreground">This helps our AI provide personalized protection</p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Display Name *</Label>
                    <Input
                      value={formData.displayName}
                      onChange={(e) => setFormData({ ...formData, displayName: e.target.value })}
                      placeholder="Your name"
                      className="h-12"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>What type of freelance work do you do? *</Label>
                    <Select
                      value={formData.freelanceType}
                      onValueChange={(value) => setFormData({ ...formData, freelanceType: value })}
                    >
                      <SelectTrigger className="h-12">
                        <SelectValue placeholder="Select your specialty" />
                      </SelectTrigger>
                      <SelectContent>
                        {FREELANCE_TYPES.map((type) => (
                          <SelectItem key={type} value={type}>{type}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Hourly Rate (USD)</Label>
                    <Input
                      type="number"
                      value={formData.hourlyRate}
                      onChange={(e) => setFormData({ ...formData, hourlyRate: e.target.value })}
                      placeholder="e.g., 50"
                      className="h-12"
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <Label>Experience Level *</Label>
                  <div className="grid grid-cols-2 gap-3">
                    {EXPERIENCE_LEVELS.map((level) => (
                      <Card
                        key={level.value}
                        className={cn(
                          "cursor-pointer transition-all hover:scale-[1.02]",
                          formData.experienceLevel === level.value
                            ? "border-primary ring-2 ring-primary shadow-lg"
                            : "hover:shadow-md"
                        )}
                        onClick={() => setFormData({ ...formData, experienceLevel: level.value })}
                      >
                        <CardContent className="p-4 flex items-center gap-3">
                          <span className="text-2xl">{level.icon}</span>
                          <div>
                            <p className="font-semibold">{level.label}</p>
                            <p className="text-xs text-muted-foreground">{level.desc}</p>
                          </div>
                          {formData.experienceLevel === level.value && (
                            <Check className="h-5 w-5 text-primary ml-auto" />
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Step 2: Platforms */}
            {step === 2 && (
              <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                <div className="flex items-center gap-3 p-4 rounded-xl bg-primary/5 border border-primary/20">
                  <Briefcase className="h-5 w-5 text-primary" />
                  <div>
                    <p className="font-semibold">Where do you find work?</p>
                    <p className="text-xs text-muted-foreground">We'll tailor scam detection for your platforms</p>
                  </div>
                  <Badge className="ml-auto">{formData.platforms.length} selected</Badge>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {PLATFORMS.map((platform) => (
                    <Card
                      key={platform.id}
                      className={cn(
                        "cursor-pointer transition-all hover:scale-[1.02]",
                        formData.platforms.includes(platform.id)
                          ? "border-primary ring-2 ring-primary shadow-lg"
                          : "hover:shadow-md"
                      )}
                      onClick={() => toggleItem(formData.platforms, platform.id, 'platforms')}
                    >
                      <CardContent className="p-4 flex items-center gap-3">
                        <span className="text-2xl">{platform.icon}</span>
                        <p className="font-medium">{platform.name}</p>
                        {formData.platforms.includes(platform.id) && (
                          <Check className="h-5 w-5 text-primary ml-auto" />
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Step 3: Protection Priorities */}
            {step === 3 && (
              <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                <div className="flex items-center gap-3 p-4 rounded-xl bg-primary/5 border border-primary/20">
                  <Shield className="h-5 w-5 text-primary" />
                  <div>
                    <p className="font-semibold">What matters most to you?</p>
                    <p className="text-xs text-muted-foreground">Our AI will prioritize these protection areas</p>
                  </div>
                  <Badge className="ml-auto">{formData.protectionPriorities.length} selected</Badge>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                  {PROTECTION_PRIORITIES.map((priority) => (
                    <Card
                      key={priority.id}
                      className={cn(
                        "cursor-pointer transition-all hover:scale-[1.02]",
                        formData.protectionPriorities.includes(priority.id)
                          ? "border-primary ring-2 ring-primary shadow-lg"
                          : "hover:shadow-md"
                      )}
                      onClick={() => toggleItem(formData.protectionPriorities, priority.id, 'protectionPriorities')}
                    >
                      <CardContent className="p-4 flex flex-col items-center text-center gap-2">
                        <div className={cn("w-12 h-12 rounded-xl flex items-center justify-center text-2xl", priority.color)}>
                          {priority.icon}
                        </div>
                        <p className="font-medium text-sm">{priority.name}</p>
                        {formData.protectionPriorities.includes(priority.id) && (
                          <Check className="h-4 w-4 text-primary" />
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Step 4: Privacy */}
            {step === 4 && (
              <div className="grid md:grid-cols-2 gap-8 animate-in fade-in slide-in-from-right-4 duration-300">
                <div className="space-y-6">
                  <div className="flex items-center gap-3 p-4 rounded-xl bg-primary/5 border border-primary/20">
                    <Lock className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-semibold">Privacy & Consent</p>
                      <p className="text-xs text-muted-foreground">Control your data and notifications</p>
                    </div>
                  </div>

                  <Card className={cn(
                    "transition-all",
                    formData.gdprConsent ? "border-green-500 bg-green-500/5" : "border-blue-500 bg-blue-500/5"
                  )}>
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <Scale className={cn("h-5 w-5 mt-0.5", formData.gdprConsent ? "text-green-500" : "text-blue-500")} />
                        <div className="flex-1">
                          <p className="font-medium">Data Processing Consent *</p>
                          <p className="text-sm text-muted-foreground mt-1 mb-3">
                            We process your data in compliance with GDPR to provide AI-powered protection.
                          </p>
                          <div className="flex items-center justify-between">
                            <span className="text-sm">I consent to data processing</span>
                            <Switch
                              checked={formData.gdprConsent}
                              onCheckedChange={(v) => setFormData({ ...formData, gdprConsent: v })}
                            />
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Bell className="h-5 w-5 text-muted-foreground" />
                          <div>
                            <p className="font-medium">Email Notifications</p>
                            <p className="text-xs text-muted-foreground">Important updates and alerts</p>
                          </div>
                        </div>
                        <Switch
                          checked={formData.emailNotifications}
                          onCheckedChange={(v) => setFormData({ ...formData, emailNotifications: v })}
                        />
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <div className="flex items-center justify-center">
                  <Card className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/30">
                    <CardContent className="p-6 text-center">
                      <div className="flex justify-center -space-x-2 mb-4">
                        {['🛡️', '🔍', '💰', '📏', '⚖️'].map((icon, i) => (
                          <div key={i} className="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-lg border-2 border-background">
                            {icon}
                          </div>
                        ))}
                      </div>
                      <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto mb-4" />
                      <h3 className="font-bold text-lg mb-2">You're almost ready!</h3>
                      <p className="text-sm text-muted-foreground">
                        Our 13 AI agents will start protecting your freelance career based on your preferences.
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="pt-4 border-t flex justify-between items-center">
            <Button variant="ghost" onClick={handleBack} disabled={step === 1}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div className="flex items-center gap-2">
              {!canProceed() && (
                <span className="text-sm text-muted-foreground">Complete required fields</span>
              )}
              <Button onClick={handleNext} disabled={!canProceed() || isLoading} size="lg">
                {isLoading ? (
                  <Loader size="sm" className="mr-2" />
                ) : step === totalSteps ? (
                  <Sparkles className="h-4 w-4 mr-2" />
                ) : (
                  <ArrowRight className="h-4 w-4 mr-2" />
                )}
                {step === totalSteps ? "Complete Setup" : "Continue"}
              </Button>
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
