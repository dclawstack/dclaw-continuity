"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, FileWarning, Send, Sparkles } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { api, type RegulatoryReport, type ReportStatus } from "@/lib/api";

const STATUS_VARIANT: Record<ReportStatus, string> = {
  draft: "bg-slate-100 text-slate-700",
  validated: "bg-yellow-100 text-yellow-700",
  submitted: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
};

export default function RegulatoryPage() {
  const [reports, setReports] = useState<RegulatoryReport[]>([]);
  const [framework, setFramework] = useState("SOX");
  const [period, setPeriod] = useState("2026-Q1");
  const [ctx, setCtx] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [refMap, setRefMap] = useState<Record<string, string>>({});

  async function refresh() {
    try {
      setReports(await api.regulatory.list());
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed to load");
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function generate() {
    setBusy("generate");
    setErr(null);
    try {
      await api.regulatory.generate(framework, period, ctx);
      setCtx("");
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed");
    } finally {
      setBusy(null);
    }
  }

  async function submit(r: RegulatoryReport) {
    const ref = refMap[r.id] || "";
    if (!ref.trim()) return;
    setBusy(r.id);
    try {
      await api.regulatory.submit(r.id, ref);
      await refresh();
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Regulatory reporting</h1>
        <p className="text-sm text-slate-500">
          Auto-generate continuity compliance reports from workspace evidence
          and submit when validation passes.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-500" /> Generate report
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <Label className="text-xs">Framework</Label>
              <Input
                value={framework}
                onChange={(e) => setFramework(e.target.value)}
                placeholder="SOX, PCI, ISO22301…"
              />
            </div>
            <div>
              <Label className="text-xs">Period</Label>
              <Input
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                placeholder="2026-Q1"
              />
            </div>
            <div>
              <Label className="text-xs">Extra context (optional)</Label>
              <Input value={ctx} onChange={(e) => setCtx(e.target.value)} />
            </div>
          </div>
          <Button onClick={generate} disabled={busy === "generate"}>
            {busy === "generate" ? "Generating…" : "Generate"}
          </Button>
          {err && <p className="text-sm text-red-600">{err}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Reports</CardTitle>
        </CardHeader>
        <CardContent>
          {reports.length === 0 ? (
            <p className="text-sm text-slate-500">No reports yet.</p>
          ) : (
            <ul className="space-y-3">
              {reports.map((r) => (
                <li key={r.id} className="border rounded p-3 space-y-2">
                  <div className="flex items-center gap-3">
                    <Badge className={STATUS_VARIANT[r.status]}>{r.status}</Badge>
                    <div className="flex-1">
                      <div className="font-medium">{r.title}</div>
                      <div className="text-xs text-slate-500">
                        {r.framework} · {r.period}
                        {r.submission_reference
                          ? ` · ref ${r.submission_reference}`
                          : ""}
                      </div>
                    </div>
                    {r.validation.complete ? (
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                    ) : (
                      <FileWarning className="h-4 w-4 text-orange-500" />
                    )}
                  </div>
                  {!r.validation.complete && r.validation.issues?.length > 0 && (
                    <div className="text-xs text-orange-700">
                      Issues: {r.validation.issues.join(", ")}
                    </div>
                  )}
                  {r.status !== "submitted" && r.validation.complete && (
                    <div className="flex items-center gap-2">
                      <Input
                        placeholder="submission reference"
                        value={refMap[r.id] || ""}
                        onChange={(e) =>
                          setRefMap((m) => ({ ...m, [r.id]: e.target.value }))
                        }
                      />
                      <Button
                        size="sm"
                        onClick={() => submit(r)}
                        disabled={busy === r.id || !(refMap[r.id] || "").trim()}
                      >
                        <Send className="h-4 w-4 mr-1" /> Submit
                      </Button>
                    </div>
                  )}
                  <details className="text-sm">
                    <summary className="cursor-pointer text-slate-600">
                      Content
                    </summary>
                    <pre className="mt-2 text-xs bg-slate-50 p-3 rounded overflow-x-auto">
                      {JSON.stringify(r.content, null, 2)}
                    </pre>
                  </details>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
