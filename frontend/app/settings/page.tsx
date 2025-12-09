"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";
import { AppLayout } from "@/components/flagpilot";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Loader } from "@/components/ui/loader";
import { toast } from "sonner";
import {
  User,
  CreditCard,
  Shield,
  Bell,
  Database,
  Trash2,
  Download,
  Upload,
  Key,
  Mail,
  Loader2,
  Save,
  AlertTriangle,
} from "lucide-react";

export default function SettingsPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [session, setSession] = useState<any>(null);

  // Profile settings
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  // Notification settings
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [agentAlerts, setAgentAlerts] = useState(true);
  const [weeklyDigest, setWeeklyDigest] = useState(false);

  // Privacy settings
  const [globalRag, setGlobalRag] = useState(false);
  const [dataRetention, setDataRetention] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const { data } = await authClient.getSession();
        if (!data) {
          router.push("/");
          return;
        }
        setSession(data);
        setName(data.user?.name || "");
        setEmail(data.user?.email || "");
      } catch (error) {
        router.push("/");
      } finally {
        setIsLoading(false);
      }
    };
    checkAuth();
  }, [router]);

  const handleSaveProfile = async () => {
    setIsSaving(true);
    try {
      // TODO: Connect to backend API to save profile
      await new Promise((r) => setTimeout(r, 1000));
      toast.success("Profile updated successfully");
    } catch (error) {
      toast.error("Failed to update profile");
    } finally {
      setIsSaving(false);
    }
  };

  const handleExportData = async () => {
    toast.info("Preparing data export...");
    // TODO: Connect to backend API
    await new Promise((r) => setTimeout(r, 2000));
    toast.success("Export ready for download");
  };

  const handleDeleteAccount = async () => {
    if (!confirm("Are you sure you want to delete your account? This cannot be undone.")) {
      return;
    }
    toast.error("Account deletion is currently disabled");
  };

  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background">
        <Loader variant="circular" size="lg" />
      </div>
    );
  }

  return (
    <AppLayout
      breadcrumbs={[
        { label: "Home", href: "/" },
        { label: "Settings" },
      ]}
      user={{
        name: session?.user?.name || "User",
        email: session?.user?.email || "",
        avatarUrl: session?.user?.image || undefined,
      }}
      credits={{ current: 245, total: 500 }}
    >
      <div className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto p-6 space-y-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
            <p className="text-muted-foreground">
              Manage your account, preferences, and data privacy settings.
            </p>
          </div>

          <Tabs defaultValue="profile" className="space-y-6">
            <TabsList className="bg-zinc-900 border border-zinc-800">
              <TabsTrigger value="profile" className="gap-2">
                <User className="size-4" />
                Profile
              </TabsTrigger>
              <TabsTrigger value="billing" className="gap-2">
                <CreditCard className="size-4" />
                Billing
              </TabsTrigger>
              <TabsTrigger value="privacy" className="gap-2">
                <Shield className="size-4" />
                Privacy
              </TabsTrigger>
              <TabsTrigger value="notifications" className="gap-2">
                <Bell className="size-4" />
                Notifications
              </TabsTrigger>
            </TabsList>

            {/* Profile Tab */}
            <TabsContent value="profile" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Profile Information</CardTitle>
                  <CardDescription>
                    Update your personal information and profile picture.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center gap-6">
                    <Avatar className="size-20">
                      <AvatarImage src={session?.user?.image} />
                      <AvatarFallback className="text-lg bg-primary/20 text-primary">
                        {name.slice(0, 2).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div className="space-y-2">
                      <Button variant="outline" size="sm" className="gap-2">
                        <Upload className="size-4" />
                        Upload Photo
                      </Button>
                      <p className="text-xs text-muted-foreground">
                        JPG, PNG or GIF. Max 2MB.
                      </p>
                    </div>
                  </div>

                  <Separator />

                  <div className="grid gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="name">Display Name</Label>
                      <Input
                        id="name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Your name"
                      />
                    </div>

                    <div className="grid gap-2">
                      <Label htmlFor="email">Email Address</Label>
                      <div className="flex gap-2">
                        <Input
                          id="email"
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          placeholder="your@email.com"
                        />
                        <Badge variant="secondary" className="shrink-0">
                          Verified
                        </Badge>
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <Button onClick={handleSaveProfile} disabled={isSaving} className="gap-2">
                      {isSaving ? (
                        <Loader2 className="size-4 animate-spin" />
                      ) : (
                        <Save className="size-4" />
                      )}
                      Save Changes
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Security</CardTitle>
                  <CardDescription>Manage your password and security settings.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <Key className="size-5 text-muted-foreground" />
                      <div>
                        <p className="font-medium">Password</p>
                        <p className="text-sm text-muted-foreground">Last changed 30 days ago</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      Change Password
                    </Button>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <Mail className="size-5 text-muted-foreground" />
                      <div>
                        <p className="font-medium">Two-Factor Authentication</p>
                        <p className="text-sm text-muted-foreground">Add an extra layer of security</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      Enable 2FA
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Billing Tab */}
            <TabsContent value="billing" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Current Plan</CardTitle>
                  <CardDescription>
                    Your subscription and usage details.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between p-4 bg-purple-500/10 border border-purple-500/20 rounded-lg">
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold">Pro Plan</h3>
                        <Badge className="bg-purple-600">Active</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        $29/month • Renews on January 15, 2026
                      </p>
                    </div>
                    <Button variant="outline">Manage Subscription</Button>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Credits Used This Month</span>
                      <span className="font-mono">1,755 / 2,000</span>
                    </div>
                    <Progress value={87.75} className="h-2" />
                    <p className="text-xs text-muted-foreground">
                      245 credits remaining • Resets in 12 days
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Usage History</CardTitle>
                  <CardDescription>Recent credit usage by agents.</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {[
                      { agent: "Legal Eagle", action: "Contract Analysis", credits: 25, time: "2 hours ago" },
                      { agent: "Iris", action: "Client Research", credits: 10, time: "5 hours ago" },
                      { agent: "Negotiator", action: "Strategy Generation", credits: 15, time: "1 day ago" },
                      { agent: "Job Authenticator", action: "Scam Check", credits: 5, time: "2 days ago" },
                    ].map((item, i) => (
                      <div key={i} className="flex items-center justify-between py-2 border-b last:border-0">
                        <div>
                          <p className="font-medium text-sm">{item.agent}</p>
                          <p className="text-xs text-muted-foreground">{item.action}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-mono text-sm text-red-400">-{item.credits}</p>
                          <p className="text-xs text-muted-foreground">{item.time}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Privacy Tab */}
            <TabsContent value="privacy" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Personal Data Moat</CardTitle>
                  <CardDescription>
                    Control how your data is stored and used.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <p className="font-medium">Global RAG Access</p>
                      <p className="text-sm text-muted-foreground">
                        Allow agents to use shared knowledge base
                      </p>
                    </div>
                    <Switch checked={globalRag} onCheckedChange={setGlobalRag} />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <p className="font-medium">Data Retention</p>
                      <p className="text-sm text-muted-foreground">
                        Keep conversation history for context
                      </p>
                    </div>
                    <Switch checked={dataRetention} onCheckedChange={setDataRetention} />
                  </div>

                  <Separator />

                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Storage Used</span>
                      <span className="font-mono">2.4 GB / 25 GB</span>
                    </div>
                    <Progress value={9.6} className="h-2" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Data Management</CardTitle>
                  <CardDescription>Export or delete your data.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <Download className="size-5 text-muted-foreground" />
                      <div>
                        <p className="font-medium">Export Data</p>
                        <p className="text-sm text-muted-foreground">
                          Download all your data in JSON format
                        </p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" onClick={handleExportData}>
                      Export
                    </Button>
                  </div>

                  <div className="flex items-center justify-between p-4 border border-destructive/30 bg-destructive/5 rounded-lg">
                    <div className="flex items-center gap-4">
                      <AlertTriangle className="size-5 text-destructive" />
                      <div>
                        <p className="font-medium text-destructive">Delete Account</p>
                        <p className="text-sm text-muted-foreground">
                          Permanently delete your account and all data
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={handleDeleteAccount}
                    >
                      Delete
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Notifications Tab */}
            <TabsContent value="notifications" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Notification Preferences</CardTitle>
                  <CardDescription>
                    Choose what notifications you want to receive.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <p className="font-medium">Email Notifications</p>
                      <p className="text-sm text-muted-foreground">
                        Receive important updates via email
                      </p>
                    </div>
                    <Switch
                      checked={emailNotifications}
                      onCheckedChange={setEmailNotifications}
                    />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <p className="font-medium">Agent Alerts</p>
                      <p className="text-sm text-muted-foreground">
                        Get notified when agents complete tasks
                      </p>
                    </div>
                    <Switch checked={agentAlerts} onCheckedChange={setAgentAlerts} />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <p className="font-medium">Weekly Digest</p>
                      <p className="text-sm text-muted-foreground">
                        Summary of your weekly activity
                      </p>
                    </div>
                    <Switch checked={weeklyDigest} onCheckedChange={setWeeklyDigest} />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </AppLayout>
  );
}
