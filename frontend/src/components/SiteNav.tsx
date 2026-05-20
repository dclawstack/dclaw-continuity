"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LogOut } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/functions", label: "Functions" },
  { href: "/bcps", label: "BCPs" },
  { href: "/impact", label: "Impact" },
  { href: "/recovery", label: "Recovery" },
  { href: "/exercises", label: "Exercises" },
  { href: "/crisis", label: "Crisis" },
  { href: "/vendors", label: "Vendors" },
  { href: "/communications", label: "Comms" },
  { href: "/work-area", label: "Sites" },
  { href: "/it-dr", label: "IT DR" },
  { href: "/supply-chain", label: "Supply" },
  { href: "/regulatory", label: "Reports" },
];

export function SiteNav() {
  const path = usePathname() || "/";
  const { user, signOut } = useAuth();
  const isAuthPage = path === "/login" || path === "/signup";

  return (
    <header className="border-b bg-white">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center gap-6">
        <div className="flex items-center gap-2">
          <div
            className="h-6 w-6 rounded"
            style={{ backgroundColor: "#3B82F6" }}
          />
          <span className="font-semibold">DClaw Continuity</span>
        </div>
        {!isAuthPage && user && (
          <nav className="flex items-center gap-1 text-sm overflow-x-auto">
            {links.map((l) => {
              const active =
                l.href === "/" ? path === "/" : path.startsWith(l.href);
              return (
                <Link
                  key={l.href}
                  href={l.href}
                  className={cn(
                    "px-3 py-1.5 rounded-md whitespace-nowrap transition-colors",
                    active
                      ? "bg-slate-900 text-white"
                      : "text-slate-600 hover:bg-slate-100",
                  )}
                >
                  {l.label}
                </Link>
              );
            })}
          </nav>
        )}
        <div className="ml-auto flex items-center gap-3">
          {user ? (
            <>
              <span className="text-xs text-slate-500">{user.email}</span>
              <Button size="sm" variant="ghost" onClick={signOut}>
                <LogOut className="h-4 w-4 mr-1" /> Sign out
              </Button>
            </>
          ) : (
            !isAuthPage && (
              <Link
                href="/login"
                className="text-sm text-blue-600 hover:underline"
              >
                Sign in
              </Link>
            )
          )}
        </div>
      </div>
    </header>
  );
}
