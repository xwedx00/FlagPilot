import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Use standalone only in Docker/production (set via env)
  output: process.env.NEXT_OUTPUT_STANDALONE === 'true' ? 'standalone' : undefined,
  reactStrictMode: false,
  typescript: {
    ignoreBuildErrors: true,
  },
  // Allow browser preview proxy origins for development
  allowedDevOrigins: [
    "http://127.0.0.1:*",
    "http://localhost:*",
  ],
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "pub-6f0cf05705c7412b93a792350f3b3aa5.r2.dev",
      },
      {
        protocol: "https",
        hostname: "jdj14ctwppwprnqu.public.blob.vercel-storage.com",
      },
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: "http://127.0.0.1:8000/api/v1/:path*",
      },
    ];
  },
};

export default nextConfig;
