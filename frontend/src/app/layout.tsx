import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { SiteNav } from "@/components/SiteNav";
import { Copilot } from "@/components/Copilot";
import { AuthShell } from "@/components/AuthShell";
import { AuthProvider } from "@/lib/auth";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "DClaw Continuity",
  description: "AI-powered business continuity planning",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-slate-50 min-h-screen`}>
        <AuthProvider>
          <SiteNav />
          <main className="max-w-6xl mx-auto px-6 py-8">
            <AuthShell>{children}</AuthShell>
          </main>
          <Copilot />
        </AuthProvider>
      </body>
    </html>
  );
}
