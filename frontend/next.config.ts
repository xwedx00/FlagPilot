import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: false,
  transpilePackages: ["@copilotkit/react-core", "@copilotkit/react-ui", "@copilotkit/runtime-client-gql"],
  async rewrites() {
    return [
      {
        source: "/api/health",
        destination: "http://127.0.0.1:8000/health",
      },
      // CopilotKit endpoint - primary integration point
      {
        source: "/api/copilotkit",
        destination: "http://127.0.0.1:8000/copilotkit",
      },
      {
        source: "/api/copilotkit/:path*",
        destination: "http://127.0.0.1:8000/copilotkit/:path*",
      },
      // Legacy agent listing endpoint
      {
        source: "/api/agents/:path*",
        destination: "http://127.0.0.1:8000/api/agents/:path*",
      },
    ];
  },
};

export default nextConfig;
