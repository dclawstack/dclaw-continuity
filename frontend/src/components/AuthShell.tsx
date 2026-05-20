"use client";

import { RequireAuth } from "@/components/RequireAuth";

export function AuthShell({ children }: { children: React.ReactNode }) {
  return <RequireAuth>{children}</RequireAuth>;
}
