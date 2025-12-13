"use client";

import { UploadButton } from "@/utils/uploadthing";
import { toast } from "sonner";
import { ingestFile } from "@/lib/api";
import { Upload, Loader2 } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { authClient } from "@/lib/auth-client";

interface ChatUploadProps {
    onUpload?: (filename: string) => void;
    className?: string;
}

export function ChatUpload({ onUpload, className }: ChatUploadProps) {
    const [isIngesting, setIsIngesting] = useState(false);
    const { data: session } = authClient.useSession();


    return (
        <div className={cn("relative flex items-center", className)}>
            {isIngesting && (
                <div className="absolute inset-0 flex items-center justify-center bg-background/80 z-20 rounded-md">
                    <Loader2 className="w-4 h-4 animate-spin text-primary" />
                </div>
            )}

            <UploadButton
                endpoint="textUploader"
                appearance={{
                    button: "bg-transparent text-muted-foreground hover:bg-muted p-2 rounded-full transition-colors w-auto h-auto focus-within:ring-0 after:bg-transparent",
                    allowedContent: "hidden",
                    container: "w-auto h-auto",
                }}
                content={{
                    button({ ready }) {
                        if (ready) return <Upload className="w-5 h-5" />;
                        return <Loader2 className="w-5 h-5 animate-spin" />;
                    }
                }}
                onClientUploadComplete={async (res) => {
                    if (res && res.length > 0) {
                        const file = res[0];
                        setIsIngesting(true);
                        toast.info(`Ingesting ${file.name}...`);

                        try {
                            // Get user ID from session, fallback to anonymous
                            const userId = session?.user?.id || "anonymous";

                            // Trigger backend ingestion with proper user ID
                            await ingestFile(file.url, file.name, userId);

                            toast.success(`${file.name} ingested successfully!`);
                            if (onUpload) onUpload(file.name);
                        } catch (error) {
                            console.error(error);
                            toast.error("Ingestion failed. Proceeding with chat.");
                        } finally {
                            setIsIngesting(false);
                        }
                    }
                }}
                onUploadError={(error: Error) => {
                    toast.error(`Upload failed: ${error.message}`);
                }}
            />
        </div>
    );
}
