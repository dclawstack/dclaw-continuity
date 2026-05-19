"use client";

import { useEffect, useState } from "react";
import { Sparkles, ShieldAlert } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { api, type BCP, type BusinessFunction } from "@/lib/api";

const STATUS_VARIANT: Record<string, string> = {
  draft: "bg-slate-100 text-slate-700",
  review: "bg-yellow-100 text-yellow-700",
  approved: "bg-green-100 text-green-700",
  retired: "bg-slate-200 text-slate-500",
};

export default function BCPsPage() {
  const [bcps, setBCPs] = useState<BCP[]>([]);
  const [functions, setFunctions] = useState<BusinessFunction[]>([]);
  const [selectedFn, setSelectedFn] = useState<string>("");
  const [context, setContext] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [openBcp, setOpenBcp] = useState<BCP | null>(null);

  async function refresh() {
    try {
      const [fns, plans] = await Promise.all([
        api.functions.list(),
        api.bcps.list(),
      ]);
      setFunctions(fns);
      setBCPs(plans);
      if (!selectedFn && fns.length > 0) setSelectedFn(fns[0].id);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed to load");
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function generate() {
    if (!selectedFn) return;
    setBusy(true);
    setErr(null);
    try {
      await api.bcps.generate(selectedFn, context);
      setContext("");
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Generation failed");
    } finally {
      setBusy(false);
    }
  }

  async function runGap(bcpId: string) {
    setBusy(true);
    try {
      const updated = await api.bcps.gapAnalysis(bcpId);
      setOpenBcp(updated);
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Gap analysis failed");
    } finally {
      setBusy(false);
    }
  }

  const functionsById = Object.fromEntries(functions.map((f) => [f.id, f]));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Business continuity plans</h1>
        <p className="text-sm text-slate-500">
          Draft a BCP for a function with the Copilot, then review and run a gap
          analysis.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-500" />
            Generate BCP with AI
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {functions.length === 0 ? (
            <p className="text-sm text-slate-500">
              Create a business function first.
            </p>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-xs">Function</Label>
                  <select
                    value={selectedFn}
                    onChange={(e) => setSelectedFn(e.target.value)}
                    className="mt-1 flex h-10 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
                  >
                    {functions.map((fn) => (
                      <option key={fn.id} value={fn.id}>
                        {fn.name} ({fn.criticality})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label className="text-xs">Extra context (optional)</Label>
                  <Input
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                    placeholder="e.g. regional datacenter outage"
                  />
                </div>
              </div>
              <Button onClick={generate} disabled={busy || !selectedFn}>
                {busy ? "Generating…" : "Generate BCP"}
              </Button>
            </>
          )}
          {err && <p className="text-sm text-red-600">{err}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>All BCPs</CardTitle>
        </CardHeader>
        <CardContent>
          {bcps.length === 0 ? (
            <p className="text-sm text-slate-500">No BCPs yet.</p>
          ) : (
            <ul className="divide-y">
              {bcps.map((bcp) => (
                <li key={bcp.id} className="py-3 flex items-center gap-3">
                  <Badge className={STATUS_VARIANT[bcp.status] ?? ""}>
                    {bcp.status}
                  </Badge>
                  <div className="flex-1">
                    <div className="font-medium">{bcp.title}</div>
                    <div className="text-xs text-slate-500">
                      {functionsById[bcp.function_id]?.name ?? "—"} ·{" "}
                      {bcp.gaps.length} gap{bcp.gaps.length === 1 ? "" : "s"}
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setOpenBcp(bcp)}
                  >
                    View
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => runGap(bcp.id)}
                    disabled={busy}
                  >
                    <ShieldAlert className="h-4 w-4 mr-1" />
                    Gap analysis
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      {openBcp && <BCPDetail bcp={openBcp} onClose={() => setOpenBcp(null)} />}
    </div>
  );
}

function BCPDetail({ bcp, onClose }: { bcp: BCP; onClose: () => void }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{bcp.title}</CardTitle>
        <Button size="sm" variant="ghost" onClick={onClose}>
          Close
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-slate-600">{bcp.summary}</p>
        <pre className="text-xs bg-slate-50 p-3 rounded overflow-x-auto">
          {JSON.stringify(bcp.content, null, 2)}
        </pre>
        {bcp.gaps.length > 0 && (
          <div>
            <h3 className="font-medium mb-2">Identified gaps</h3>
            <ul className="space-y-2">
              {bcp.gaps.map((gap, i) => (
                <li
                  key={i}
                  className="text-sm border-l-2 border-red-300 pl-3 py-1"
                >
                  <strong>{String(gap.severity || "")}</strong>:{" "}
                  {String(gap.issue || "")} — {String(gap.recommendation || "")}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
