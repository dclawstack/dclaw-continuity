"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  AlertTriangle,
  Briefcase,
  FileText,
  LifeBuoy,
  Loader2,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api, type BusinessFunction } from "@/lib/api";

interface Counts {
  functions: number;
  bcps: number;
  impact: number;
  recovery: number;
}

const CRITICALITY_VARIANT: Record<string, string> = {
  critical: "bg-red-100 text-red-700",
  high: "bg-orange-100 text-orange-700",
  medium: "bg-yellow-100 text-yellow-700",
  low: "bg-slate-100 text-slate-700",
};

export default function DashboardPage() {
  const [counts, setCounts] = useState<Counts | null>(null);
  const [functions, setFunctions] = useState<BusinessFunction[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const [fns, bcps, ia, rs] = await Promise.all([
          api.functions.list(),
          api.bcps.list(),
          api.impact.list(),
          api.recovery.list(),
        ]);
        if (!mounted) return;
        setFunctions(fns);
        setCounts({
          functions: fns.length,
          bcps: bcps.length,
          impact: ia.length,
          recovery: rs.length,
        });
      } catch (e) {
        if (!mounted) return;
        setErr(e instanceof Error ? e.message : "Failed to load");
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Continuity overview</h1>
        <p className="text-sm text-slate-500">
          AI-powered planning, impact analysis, and recovery for critical
          business functions.
        </p>
      </div>

      {err && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="py-3 text-sm text-red-700">
            {err}
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Business functions"
          value={counts?.functions ?? "—"}
          icon={<Briefcase className="h-5 w-5 text-slate-500" />}
          href="/functions"
          loading={loading}
        />
        <StatCard
          label="BCPs"
          value={counts?.bcps ?? "—"}
          icon={<FileText className="h-5 w-5 text-slate-500" />}
          href="/bcps"
          loading={loading}
        />
        <StatCard
          label="Impact assessments"
          value={counts?.impact ?? "—"}
          icon={<AlertTriangle className="h-5 w-5 text-slate-500" />}
          href="/impact"
          loading={loading}
        />
        <StatCard
          label="Recovery strategies"
          value={counts?.recovery ?? "—"}
          icon={<LifeBuoy className="h-5 w-5 text-slate-500" />}
          href="/recovery"
          loading={loading}
        />
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent functions</CardTitle>
          <Link
            href="/functions"
            className="text-sm text-blue-600 hover:underline"
          >
            Manage →
          </Link>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin" /> Loading
            </div>
          ) : functions.length === 0 ? (
            <p className="text-sm text-slate-500">
              No functions yet.{" "}
              <Link className="text-blue-600 underline" href="/functions">
                Create the first one
              </Link>{" "}
              to start planning.
            </p>
          ) : (
            <ul className="divide-y">
              {functions.slice(0, 5).map((fn) => (
                <li key={fn.id} className="py-2 flex items-center gap-3">
                  <Badge
                    className={CRITICALITY_VARIANT[fn.criticality] ?? ""}
                  >
                    {fn.criticality}
                  </Badge>
                  <span className="font-medium">{fn.name}</span>
                  <span className="text-xs text-slate-500 ml-auto">
                    RTO {fn.rto_minutes}m · RPO {fn.rpo_minutes}m
                  </span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({
  label,
  value,
  icon,
  href,
  loading,
}: {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  href: string;
  loading: boolean;
}) {
  return (
    <Link href={href} className="block">
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="py-4">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase tracking-wide text-slate-500">
              {label}
            </span>
            {icon}
          </div>
          <div className="mt-2 text-2xl font-semibold">
            {loading ? "…" : value}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
