"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

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
];

export function SiteNav() {
  const path = usePathname();
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
        <nav className="flex items-center gap-1 text-sm">
          {links.map((l) => {
            const active =
              l.href === "/" ? path === "/" : path?.startsWith(l.href);
            return (
              <Link
                key={l.href}
                href={l.href}
                className={cn(
                  "px-3 py-1.5 rounded-md transition-colors",
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
      </div>
    </header>
  );
}
