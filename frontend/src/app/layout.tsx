import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { AppShell } from "@/components/AppShell";
import { Copilot } from "@/components/Copilot";
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
          <AppShell>{children}</AppShell>
          <Copilot />
        </AuthProvider>
      </body>
    </html>
  );
}
