"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { Sidebar } from "@/components/Sidebar";
import { TopBar } from "@/components/TopBar";
import { useAuth } from "@/lib/auth";

const PUBLIC_PATHS = new Set(["/login", "/signup"]);

export function AppShell({ children }: { children: React.ReactNode }) {
  const { token, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname() || "/";
  const isPublic = PUBLIC_PATHS.has(pathname);

  useEffect(() => {
    if (loading) return;
    if (!token && !isPublic) router.replace("/login");
    if (token && isPublic) router.replace("/");
  }, [token, loading, isPublic, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen text-sm text-slate-500">
        Loading…
      </div>
    );
  }

  // Public auth pages: minimal chrome.
  if (isPublic) {
    return (
      <div className="min-h-screen flex flex-col">
        <TopBar />
        <main className="flex-1 px-6 py-8">{children}</main>
      </div>
    );
  }

  // Not signed in — redirect is firing; render nothing.
  if (!token) return null;

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <TopBar />
        <main className="flex-1 px-6 md:px-8 py-8 max-w-6xl w-full">
          {children}
        </main>
      </div>
    </div>
  );
}
