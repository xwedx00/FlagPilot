import { S3Client, PutObjectCommand, GetObjectCommand, DeleteObjectCommand, ListObjectsV2Command } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

// MinIO S3-compatible client
const s3Client = new S3Client({
  region: "us-east-1", // Required but not used by MinIO
  endpoint: process.env.MINIO_ENDPOINT || "http://localhost:9000",
  credentials: {
    accessKeyId: process.env.MINIO_ACCESS_KEY || "flagpilot",
    secretAccessKey: process.env.MINIO_SECRET_KEY || "flagpilot123",
  },
  forcePathStyle: true, // Required for MinIO
});

const BUCKET = process.env.MINIO_BUCKET || "flagpilot-uploads";

/**
 * Upload a file to MinIO
 */
export async function uploadFile(
  key: string,
  body: Buffer | Blob | string,
  contentType?: string
): Promise<string> {
  const command = new PutObjectCommand({
    Bucket: BUCKET,
    Key: key,
    Body: body instanceof Blob ? Buffer.from(await body.arrayBuffer()) : body,
    ContentType: contentType || "application/octet-stream",
  });

  await s3Client.send(command);
  return `${process.env.MINIO_ENDPOINT}/${BUCKET}/${key}`;
}

/**
 * Get a signed URL for downloading a file
 */
export async function getDownloadUrl(key: string, expiresIn = 3600): Promise<string> {
  const command = new GetObjectCommand({
    Bucket: BUCKET,
    Key: key,
  });

  return getSignedUrl(s3Client, command, { expiresIn });
}

/**
 * Get a signed URL for uploading a file
 */
export async function getUploadUrl(key: string, contentType: string, expiresIn = 3600): Promise<string> {
  const command = new PutObjectCommand({
    Bucket: BUCKET,
    Key: key,
    ContentType: contentType,
  });

  return getSignedUrl(s3Client, command, { expiresIn });
}

/**
 * Delete a file from MinIO
 */
export async function deleteFile(key: string): Promise<void> {
  const command = new DeleteObjectCommand({
    Bucket: BUCKET,
    Key: key,
  });

  await s3Client.send(command);
}

/**
 * List files in a directory
 */
export async function listFiles(prefix?: string): Promise<string[]> {
  const command = new ListObjectsV2Command({
    Bucket: BUCKET,
    Prefix: prefix,
  });

  const response = await s3Client.send(command);
  return response.Contents?.map(obj => obj.Key!).filter(Boolean) || [];
}

/**
 * Generate a unique file key
 */
export function generateFileKey(filename: string, userId?: string): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 8);
  const safeFilename = filename.replace(/[^a-zA-Z0-9.-]/g, "_");
  
  if (userId) {
    return `users/${userId}/${timestamp}-${random}-${safeFilename}`;
  }
  return `uploads/${timestamp}-${random}-${safeFilename}`;
}

export { s3Client, BUCKET };
