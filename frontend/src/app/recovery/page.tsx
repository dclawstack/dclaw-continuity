"use client";

import { useEffect, useState } from "react";
import { LifeBuoy, Star } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  api,
  type BusinessFunction,
  type RecoveryStrategy,
} from "@/lib/api";

export default function RecoveryPage() {
  const [functions, setFunctions] = useState<BusinessFunction[]>([]);
  const [strategies, setStrategies] = useState<RecoveryStrategy[]>([]);
  const [selectedFn, setSelectedFn] = useState("");
  const [budget, setBudget] = useState<number | "">("");
  const [ctx, setCtx] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function refresh() {
    try {
      const [fns, strats] = await Promise.all([
        api.functions.list(),
        api.recovery.list(),
      ]);
      setFunctions(fns);
      setStrategies(strats);
      if (!selectedFn && fns.length > 0) setSelectedFn(fns[0].id);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed to load");
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function recommend() {
    if (!selectedFn) return;
    setBusy(true);
    setErr(null);
    try {
      await api.recovery.recommend(
        selectedFn,
        typeof budget === "number" ? budget : undefined,
        ctx,
      );
      setCtx("");
      setBudget("");
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed");
    } finally {
      setBusy(false);
    }
  }

  const functionsById = Object.fromEntries(functions.map((f) => [f.id, f]));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Recovery strategies</h1>
        <p className="text-sm text-slate-500">
          AI-recommended strategies balancing cost, RTO, and RPO.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <LifeBuoy className="h-5 w-5 text-blue-500" /> Recommend strategies
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {functions.length === 0 ? (
            <p className="text-sm text-slate-500">
              Create a business function first.
            </p>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label className="text-xs">Function</Label>
                  <select
                    value={selectedFn}
                    onChange={(e) => setSelectedFn(e.target.value)}
                    className="mt-1 flex h-10 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
                  >
                    {functions.map((fn) => (
                      <option key={fn.id} value={fn.id}>
                        {fn.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label className="text-xs">Budget cap (USD, optional)</Label>
                  <Input
                    type="number"
                    min={0}
                    value={budget}
                    onChange={(e) =>
                      setBudget(
                        e.target.value === "" ? "" : Number(e.target.value),
                      )
                    }
                    placeholder="e.g. 50000"
                  />
                </div>
                <div>
                  <Label className="text-xs">Extra context</Label>
                  <Input
                    value={ctx}
                    onChange={(e) => setCtx(e.target.value)}
                    placeholder="e.g. cloud-first preferred"
                  />
                </div>
              </div>
              <Button onClick={recommend} disabled={busy}>
                {busy ? "Recommending…" : "Recommend 3 strategies"}
              </Button>
            </>
          )}
          {err && <p className="text-sm text-red-600">{err}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>All strategies</CardTitle>
        </CardHeader>
        <CardContent>
          {strategies.length === 0 ? (
            <p className="text-sm text-slate-500">No strategies yet.</p>
          ) : (
            <ul className="space-y-3">
              {strategies.map((s) => (
                <li key={s.id} className="border rounded p-3">
                  <div className="flex items-start gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        {s.is_recommended && (
                          <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                        )}
                        <span className="font-medium">{s.title}</span>
                        <Badge variant="secondary">
                          {s.kind.replace("_", " ")}
                        </Badge>
                      </div>
                      <div className="text-xs text-slate-500 mt-1">
                        {functionsById[s.function_id]?.name ?? "—"} · RTO{" "}
                        {s.rto_minutes}m · RPO {s.rpo_minutes}m
                      </div>
                      {s.description && (
                        <p className="text-sm text-slate-600 mt-2">
                          {s.description}
                        </p>
                      )}
                    </div>
                    <div className="text-sm font-semibold">
                      ${s.estimated_cost_usd.toLocaleString()}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
