"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  AlertCircle,
  AlertTriangle,
  Briefcase,
  Building2,
  ClipboardCheck,
  FileText,
  Gauge,
  LifeBuoy,
  Megaphone,
  Network,
  ScrollText,
  ServerCog,
  Shield,
} from "lucide-react";

import { cn } from "@/lib/utils";

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface NavSection {
  label: string;
  items: NavItem[];
}

const SECTIONS: NavSection[] = [
  {
    label: "",
    items: [{ href: "/", label: "Dashboard", icon: Gauge }],
  },
  {
    label: "Planning",
    items: [
      { href: "/functions", label: "Functions", icon: Briefcase },
      { href: "/bcps", label: "BCPs", icon: FileText },
      { href: "/impact", label: "Impact", icon: AlertTriangle },
      { href: "/recovery", label: "Recovery", icon: LifeBuoy },
    ],
  },
  {
    label: "Operations",
    items: [
      { href: "/exercises", label: "Exercises", icon: ClipboardCheck },
      { href: "/crisis", label: "Crisis", icon: AlertCircle },
      { href: "/communications", label: "Communications", icon: Megaphone },
    ],
  },
  {
    label: "Resilience",
    items: [
      { href: "/work-area", label: "Work Sites", icon: Building2 },
      { href: "/it-dr", label: "IT DR", icon: ServerCog },
      { href: "/vendors", label: "Vendors", icon: Shield },
      { href: "/supply-chain", label: "Supply Chain", icon: Network },
    ],
  },
  {
    label: "Compliance",
    items: [
      { href: "/regulatory", label: "Reports", icon: ScrollText },
    ],
  },
];

export function Sidebar() {
  const path = usePathname() || "/";

  return (
    <aside className="hidden md:flex md:flex-col w-56 shrink-0 border-r bg-white">
      <div className="h-14 flex items-center gap-2 px-5 border-b">
        <div
          className="h-6 w-6 rounded"
          style={{ backgroundColor: "#3B82F6" }}
        />
        <span className="font-semibold">DClaw Continuity</span>
      </div>
      <nav className="flex-1 overflow-y-auto py-4 px-3 text-sm space-y-5">
        {SECTIONS.map((section) => (
          <div key={section.label || "root"}>
            {section.label && (
              <div className="px-2 mb-1 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                {section.label}
              </div>
            )}
            <ul className="space-y-0.5">
              {section.items.map((item) => {
                const active =
                  item.href === "/"
                    ? path === "/"
                    : path.startsWith(item.href);
                const Icon = item.icon;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex items-center gap-2 px-2 py-1.5 rounded-md transition-colors",
                        active
                          ? "bg-slate-900 text-white"
                          : "text-slate-600 hover:bg-slate-100",
                      )}
                    >
                      <Icon className="h-4 w-4 shrink-0" />
                      <span className="truncate">{item.label}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  );
}
