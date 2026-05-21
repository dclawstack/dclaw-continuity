"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { Sidebar } from "@/components/Sidebar";
import { TopBar } from "@/components/TopBar";
import { useAuth } from "@/lib/auth";

// Pages that render without the sidebar / no-token redirect.
const PUBLIC_PATHS = new Set(["/", "/login", "/signup"]);
const AUTH_PATHS = new Set(["/login", "/signup"]);

export function AppShell({ children }: { children: React.ReactNode }) {
  const { token, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname() || "/";
  const isPublic = PUBLIC_PATHS.has(pathname);
  const isAuthPage = AUTH_PATHS.has(pathname);

  useEffect(() => {
    if (loading) return;
    // Force sign-in for any non-public route when no token.
    if (!token && !isPublic) router.replace("/login");
    // Already signed in: don't waste their time on login/signup.
    if (token && isAuthPage) router.replace("/dashboard");
  }, [token, loading, isPublic, isAuthPage, router]);

  // Landing page: render bare, no chrome. Skip the loading gate so the
  // public marketing surface SSRs immediately (no flash of "Loading…").
  if (pathname === "/") {
    return <>{children}</>;
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen text-sm text-slate-500">
        Loading…
      </div>
    );
  }

  // Auth pages: thin top bar, centered card.
  if (isAuthPage) {
    return (
      <div className="min-h-screen flex flex-col">
        <TopBar />
        <main className="flex-1 px-6 py-8">{children}</main>
      </div>
    );
  }

  // Protected pages: redirect-in-flight when no token.
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
