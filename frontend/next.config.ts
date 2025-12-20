import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: "/api/agui/:path*",
        destination: "http://127.0.0.1:8000/api/agui/:path*",
      },
    ];
  },
};

export default nextConfig;
