import { Toaster } from "@/components/ui/sonner";
import type { Metadata } from "next";
import { ThemeProvider } from "../components/provider";
import "./globals.css";
import { Analytics } from "@vercel/analytics/next";
import { JetBrains_Mono, IBM_Plex_Sans } from "next/font/google";
import { SwUnregister } from "@/components/sw-unregister";

// Industrial typography
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

const ibmPlexSans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"),
  title: "FlagPilot - AI Agents for Freelancers",
  description:
    "Multi-agent AI platform that protects freelancers. Contract analysis, scam detection, payment collection, and more with autonomous AI agents.",
  openGraph: {
    title: "FlagPilot - Build Your Ideas with AI Agents",
    description:
      "13 specialized AI agents working as a team to protect freelancers. Contract Guardian, Job Authenticator, Payment Enforcer, and more.",
    url: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
    siteName: "FlagPilot",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "FlagPilot - AI Agents for Freelancers",
      },
    ],
    locale: "en-US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "FlagPilot - AI Agents for Freelancers",
    description: "13 specialized AI agents working as a team to protect freelancers.",
    images: ["/og-image.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className="dark">
      <body className={`${ibmPlexSans.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem={false}
          disableTransitionOnChange
        >
          {children}
          <Toaster />
          <SwUnregister />
          {process.env.NEXT_PUBLIC_APP_URL?.includes("localhost") ? null : <Analytics />}
        </ThemeProvider>
      </body>
    </html>
  );
}
