import { createUploadthing, type FileRouter } from "uploadthing/next"
import { UploadThingError } from "uploadthing/server"

const f = createUploadthing({
    errorFormatter: (err) => {
        console.error("Upload error:", err)
        return {
            message: err.message || "Failed to upload file",
            cause: err.cause instanceof Error ? err.cause.message : undefined
        }
    },
})

export const ourFileRouter = {
    // Define avatar upload route
    avatarUploader: f({
        image: {
            maxFileSize: "4MB",
            maxFileCount: 1
        }
    })
        .middleware(async ({ req }) => {
            try {
                // Generate a unique filename with timestamp
                const date = new Date().toISOString().split('T')[0]
                const timestamp = Date.now().toString(36)
                const fileName = `${date}_${timestamp}`

                return {
                    fileName
                }
            } catch (error) {
                console.error("Error in upload middleware:", error)
                throw new UploadThingError("Failed to process upload")
            }
        })
        .onUploadComplete(async ({ file }) => {
            try {
                return { ufsUrl: file.ufsUrl }
            } catch (error) {
                console.error("Error in onUploadComplete:", error)
                throw new UploadThingError("Failed to complete upload")
            }
        }),

    // Define text/document upload router for RAG
    textUploader: f({
        text: { maxFileSize: "4MB" },
        pdf: { maxFileSize: "4MB" },
    })
        .middleware(async ({ req }) => {
            const user = { id: "user-via-frontend" };
            return { userId: user.id };
        })
        .onUploadComplete(async ({ metadata, file }) => {
            console.log("Upload complete for userId:", metadata.userId);
            return { uploadedBy: metadata.userId, url: file.url, name: file.name };
        }),
} satisfies FileRouter

export type OurFileRouter = typeof ourFileRouter
