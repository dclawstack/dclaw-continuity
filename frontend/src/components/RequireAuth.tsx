"use client";

import { useRouter, usePathname } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "@/lib/auth";

const PUBLIC_PATHS = new Set(["/login", "/signup"]);

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { token, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname() || "/";
  const isPublic = PUBLIC_PATHS.has(pathname);

  useEffect(() => {
    if (loading) return;
    if (!token && !isPublic) {
      router.replace("/login");
    }
    if (token && isPublic) {
      router.replace("/");
    }
  }, [token, loading, isPublic, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[40vh] text-sm text-slate-500">
        Loading…
      </div>
    );
  }
  if (!token && !isPublic) {
    return null; // redirecting
  }
  return <>{children}</>;
}
