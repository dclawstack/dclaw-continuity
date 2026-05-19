"use client";

import { useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  api,
  type BusinessFunction,
  type ImpactAssessment,
} from "@/lib/api";

export default function ImpactPage() {
  const [functions, setFunctions] = useState<BusinessFunction[]>([]);
  const [assessments, setAssessments] = useState<ImpactAssessment[]>([]);
  const [selectedFn, setSelectedFn] = useState("");
  const [scenario, setScenario] = useState("");
  const [context, setContext] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function refresh() {
    try {
      const [fns, ia] = await Promise.all([
        api.functions.list(),
        api.impact.list(),
      ]);
      setFunctions(fns);
      setAssessments(ia);
      if (!selectedFn && fns.length > 0) setSelectedFn(fns[0].id);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed to load");
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function model() {
    if (!selectedFn || !scenario.trim()) return;
    setBusy(true);
    setErr(null);
    try {
      await api.impact.model(selectedFn, scenario, context);
      setScenario("");
      setContext("");
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
        <h1 className="text-2xl font-bold">Business impact analysis</h1>
        <p className="text-sm text-slate-500">
          Model disruption scenarios to quantify revenue, operational, and
          reputation impact.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-blue-500" /> Model a
            scenario
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
                        {fn.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label className="text-xs">Scenario</Label>
                  <Input
                    value={scenario}
                    onChange={(e) => setScenario(e.target.value)}
                    placeholder="e.g. 8-hour datacenter outage"
                  />
                </div>
                <div className="md:col-span-2">
                  <Label className="text-xs">Extra context (optional)</Label>
                  <Input
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                    placeholder="e.g. during peak holiday hours"
                  />
                </div>
              </div>
              <Button onClick={model} disabled={busy || !scenario.trim()}>
                {busy ? "Modeling…" : "Model impact"}
              </Button>
            </>
          )}
          {err && <p className="text-sm text-red-600">{err}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Past assessments</CardTitle>
        </CardHeader>
        <CardContent>
          {assessments.length === 0 ? (
            <p className="text-sm text-slate-500">No assessments yet.</p>
          ) : (
            <ul className="space-y-3">
              {assessments.map((a) => (
                <li key={a.id} className="border rounded p-3">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="font-medium">{a.scenario}</div>
                      <div className="text-xs text-slate-500">
                        {functionsById[a.function_id]?.name ?? "—"}
                      </div>
                    </div>
                    <div className="text-right text-sm">
                      <div className="font-semibold">
                        ${a.revenue_impact_usd.toLocaleString()}
                      </div>
                      <div className="text-xs text-slate-500">
                        ops {a.operational_impact_score}/10 · rep{" "}
                        {a.reputation_impact_score}/10
                      </div>
                    </div>
                  </div>
                  {a.description && (
                    <p className="text-sm text-slate-600 mt-2">
                      {a.description}
                    </p>
                  )}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
