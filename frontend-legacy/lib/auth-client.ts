import { createAuthClient } from "better-auth/react";
import { organizationClient } from "better-auth/client/plugins";

// Use relative URL in development to avoid CORS issues with browser previews
// This allows requests to go through the same origin regardless of proxy
export const authClient = createAuthClient({
  baseURL: typeof window !== "undefined" 
    ? window.location.origin  // Use current origin (works with any proxy)
    : process.env.NEXT_PUBLIC_APP_URL,
  plugins: [organizationClient()],
});
