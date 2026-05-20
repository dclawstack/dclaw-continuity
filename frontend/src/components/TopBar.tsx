"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LogOut } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth";

export function TopBar() {
  const path = usePathname() || "/";
  const { user, signOut } = useAuth();
  const isAuthPage = path === "/login" || path === "/signup";

  return (
    <header className="h-14 bg-white border-b flex items-center justify-end gap-3 px-6 md:px-8">
      {user ? (
        <>
          <span className="text-xs text-slate-500">{user.email}</span>
          <Button size="sm" variant="ghost" onClick={signOut}>
            <LogOut className="h-4 w-4 mr-1" /> Sign out
          </Button>
        </>
      ) : (
        !isAuthPage && (
          <Link href="/login" className="text-sm text-blue-600 hover:underline">
            Sign in
          </Link>
        )
      )}
    </header>
  );
}
