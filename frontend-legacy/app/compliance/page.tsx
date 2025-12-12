"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
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
} from "@/components/ui/alert-dialog"
import {
  Shield,
  Download,
  Trash2,
  MapPin,
  Server,
  Lock,
  FileText,
  Clock,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react"
import { toast } from "sonner"

export default function CompliancePage() {
  const [isExporting, setIsExporting] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  
  const handleExportData = async () => {
    setIsExporting(true)
    try {
      // Simulate export
      await new Promise((resolve) => setTimeout(resolve, 2000))
      toast.success("Export request submitted. You'll receive an email with download link.")
    } catch (error) {
      toast.error("Export failed. Please try again.")
    } finally {
      setIsExporting(false)
    }
  }
  
  const handleDeleteAllData = async () => {
    setIsDeleting(true)
    try {
      // Simulate deletion
      await new Promise((resolve) => setTimeout(resolve, 3000))
      toast.success("All data deletion initiated. This may take up to 30 days to complete.")
    } catch (error) {
      toast.error("Deletion failed. Please contact support.")
    } finally {
      setIsDeleting(false)
    }
  }
  
  return (
    <div className="min-h-screen bg-zinc-950 p-6">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-mono font-bold text-zinc-100 flex items-center gap-3">
            <Shield className="w-6 h-6 text-emerald-500" />
            Data Sovereignty & Compliance
          </h1>
          <p className="text-zinc-400 mt-2">
            Manage your Personal Data Moat according to GDPR and EU AI Act requirements
          </p>
        </div>
        
        {/* Compliance Status */}
        <Card className="border-zinc-800 bg-zinc-900/50">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-mono">COMPLIANCE STATUS</CardTitle>
              <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
                <CheckCircle2 className="w-3 h-3 mr-1" />
                COMPLIANT
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-4 rounded-sm bg-zinc-800/50 border border-zinc-700">
                <div className="flex items-center gap-2 mb-2">
                  <MapPin className="w-4 h-4 text-blue-400" />
                  <span className="text-xs text-zinc-400">Data Location</span>
                </div>
                <p className="text-sm font-mono text-zinc-200">EU-West-1 (Ireland)</p>
              </div>
              <div className="p-4 rounded-sm bg-zinc-800/50 border border-zinc-700">
                <div className="flex items-center gap-2 mb-2">
                  <Lock className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs text-zinc-400">Encryption</span>
                </div>
                <p className="text-sm font-mono text-zinc-200">AES-256 at rest</p>
              </div>
              <div className="p-4 rounded-sm bg-zinc-800/50 border border-zinc-700">
                <div className="flex items-center gap-2 mb-2">
                  <Server className="w-4 h-4 text-violet-400" />
                  <span className="text-xs text-zinc-400">Isolation</span>
                </div>
                <p className="text-sm font-mono text-zinc-200">Tenant Isolated</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        {/* Privacy Controls */}
        <Card className="border-zinc-800 bg-zinc-900/50">
          <CardHeader>
            <CardTitle className="text-sm font-mono">PRIVACY CONTROLS</CardTitle>
            <CardDescription>Control how your data is used</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Analytics Data Collection</Label>
                <p className="text-xs text-zinc-500">
                  Allow anonymous usage analytics to improve the platform
                </p>
              </div>
              <Switch defaultChecked />
            </div>
            
            <Separator className="bg-zinc-800" />
            
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>AI Model Training</Label>
                <p className="text-xs text-zinc-500">
                  Your data is NEVER used to train AI models
                </p>
              </div>
              <Badge variant="outline" className="text-emerald-400 border-emerald-500/50">
                Always Off
              </Badge>
            </div>
            
            <Separator className="bg-zinc-800" />
            
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Data Retention</Label>
                <p className="text-xs text-zinc-500">
                  How long we keep your data after account deletion
                </p>
              </div>
              <Badge variant="outline">30 days</Badge>
            </div>
          </CardContent>
        </Card>
        
        {/* Data Portability */}
        <Card className="border-zinc-800 bg-zinc-900/50">
          <CardHeader>
            <CardTitle className="text-sm font-mono">DATA PORTABILITY (GDPR Article 20)</CardTitle>
            <CardDescription>Export all your data in machine-readable format</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-zinc-400">
              Download a complete archive of all your data including:
            </p>
            <ul className="space-y-2 text-sm text-zinc-300">
              <li className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-zinc-500" />
                All uploaded documents from your Data Moat
              </li>
              <li className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-zinc-500" />
                Agent conversation history and memories
              </li>
              <li className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-zinc-500" />
                Credit transaction history
              </li>
              <li className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-zinc-500" />
                Profile and preference data
              </li>
            </ul>
            
            <Button
              onClick={handleExportData}
              disabled={isExporting}
              className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700"
            >
              {isExporting ? (
                <>
                  <Clock className="w-4 h-4 mr-2 animate-spin" />
                  Preparing Export...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4 mr-2" />
                  Request Data Export
                </>
              )}
            </Button>
            <p className="text-xs text-zinc-500">
              Export is prepared within 24 hours and sent to your email
            </p>
          </CardContent>
        </Card>
        
        {/* Right to Erasure */}
        <Card className="border-red-900/50 bg-red-950/10">
          <CardHeader>
            <CardTitle className="text-sm font-mono text-red-400">
              RIGHT TO ERASURE (GDPR Article 17)
            </CardTitle>
            <CardDescription>Permanently delete all your data</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 rounded-sm bg-red-950/30 border border-red-900/50">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-red-400">Nuclear Option</h4>
                  <p className="text-sm text-zinc-400 mt-1">
                    This action will permanently delete:
                  </p>
                  <ul className="text-sm text-zinc-400 mt-2 space-y-1 list-disc list-inside">
                    <li>All files in your Personal Data Moat</li>
                    <li>All vector embeddings (RAG knowledge)</li>
                    <li>All agent memories and conversation history</li>
                    <li>Your account and all associated data</li>
                  </ul>
                  <p className="text-sm text-red-400 mt-3 font-medium">
                    This cannot be undone.
                  </p>
                </div>
              </div>
            </div>
            
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button
                  variant="destructive"
                  className="w-full sm:w-auto"
                  disabled={isDeleting}
                >
                  {isDeleting ? (
                    <>
                      <Clock className="w-4 h-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Trash2 className="w-4 h-4 mr-2" />
                      Purge My Data Moat
                    </>
                  )}
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent className="bg-zinc-900 border-zinc-800">
                <AlertDialogHeader>
                  <AlertDialogTitle className="text-red-400">
                    Are you absolutely sure?
                  </AlertDialogTitle>
                  <AlertDialogDescription>
                    This action cannot be undone. This will permanently delete your
                    account and remove all your data from our servers.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel className="bg-zinc-800 border-zinc-700">
                    Cancel
                  </AlertDialogCancel>
                  <AlertDialogAction
                    onClick={handleDeleteAllData}
                    className="bg-red-600 hover:bg-red-700"
                  >
                    Yes, delete everything
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </CardContent>
        </Card>
        
        {/* Legal References */}
        <Card className="border-zinc-800 bg-zinc-900/50">
          <CardHeader>
            <CardTitle className="text-sm font-mono">LEGAL FRAMEWORK</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <a
                href="https://gdpr.eu/"
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 rounded-sm bg-zinc-800/50 border border-zinc-700 hover:border-zinc-600 transition-colors"
              >
                <h4 className="font-medium text-zinc-200">GDPR Compliance</h4>
                <p className="text-xs text-zinc-500 mt-1">
                  General Data Protection Regulation
                </p>
              </a>
              <a
                href="https://artificialintelligenceact.eu/"
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 rounded-sm bg-zinc-800/50 border border-zinc-700 hover:border-zinc-600 transition-colors"
              >
                <h4 className="font-medium text-zinc-200">EU AI Act</h4>
                <p className="text-xs text-zinc-500 mt-1">
                  Artificial Intelligence Act Compliance
                </p>
              </a>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
