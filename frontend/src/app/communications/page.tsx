"use client";

import { useEffect, useState } from "react";
import { Megaphone, Sparkles } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  api,
  type BusinessFunction,
  type CommunicationPlan,
} from "@/lib/api";

export default function CommunicationsPage() {
  const [functions, setFunctions] = useState<BusinessFunction[]>([]);
  const [plans, setPlans] = useState<CommunicationPlan[]>([]);
  const [selectedFn, setSelectedFn] = useState("");
  const [audience, setAudience] = useState("Customers");
  const [scenario, setScenario] = useState("");
  const [context, setContext] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function refresh() {
    try {
      const [f, p] = await Promise.all([
        api.functions.list(),
        api.communications.list(),
      ]);
      setFunctions(f);
      setPlans(p);
      if (!selectedFn && f.length > 0) setSelectedFn(f[0].id);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed to load");
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function draft() {
    if (!selectedFn || !scenario.trim()) return;
    setBusy(true);
    setErr(null);
    try {
      await api.communications.draft(selectedFn, audience, scenario, context);
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
        <h1 className="text-2xl font-bold">Communication plans</h1>
        <p className="text-sm text-slate-500">
          Pre-draft stakeholder communications for likely crisis scenarios.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-500" /> Draft with AI
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
                    {functions.map((f) => (
                      <option key={f.id} value={f.id}>
                        {f.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label className="text-xs">Audience</Label>
                  <Input
                    value={audience}
                    onChange={(e) => setAudience(e.target.value)}
                    placeholder="e.g. Customers, Regulators, Internal"
                  />
                </div>
                <div>
                  <Label className="text-xs">Scenario</Label>
                  <Input
                    value={scenario}
                    onChange={(e) => setScenario(e.target.value)}
                    placeholder="e.g. Datacenter outage"
                  />
                </div>
                <div className="md:col-span-3">
                  <Label className="text-xs">Extra context (optional)</Label>
                  <Input
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                  />
                </div>
              </div>
              <Button onClick={draft} disabled={busy || !scenario.trim()}>
                {busy ? "Drafting…" : "Draft plan"}
              </Button>
            </>
          )}
          {err && <p className="text-sm text-red-600">{err}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Plans</CardTitle>
        </CardHeader>
        <CardContent>
          {plans.length === 0 ? (
            <p className="text-sm text-slate-500">No plans yet.</p>
          ) : (
            <ul className="space-y-3">
              {plans.map((p) => (
                <li key={p.id} className="border rounded p-3">
                  <div className="flex items-center gap-3">
                    <Megaphone className="h-5 w-5 text-blue-500" />
                    <div className="flex-1">
                      <div className="font-medium">
                        {p.audience} · {p.scenario}
                      </div>
                      <div className="text-xs text-slate-500">
                        {functionsById[p.function_id]?.name ?? "—"} · tone:{" "}
                        {p.tone}
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-1">
                    {p.channels.map((c) => (
                      <Badge key={c} variant="secondary">
                        {c}
                      </Badge>
                    ))}
                  </div>
                  {p.templates.length > 0 && (
                    <details className="mt-3 text-sm">
                      <summary className="cursor-pointer text-slate-600">
                        {p.templates.length} template
                        {p.templates.length === 1 ? "" : "s"}
                      </summary>
                      <ul className="mt-2 space-y-3">
                        {p.templates.map((t) => (
                          <li key={t.id} className="border-l-2 border-blue-200 pl-3">
                            <div className="text-xs text-slate-500">
                              <strong>{t.channel}</strong>
                              {t.trigger ? ` — ${t.trigger}` : ""}
                            </div>
                            {t.subject && (
                              <div className="font-medium">{t.subject}</div>
                            )}
                            <p className="whitespace-pre-wrap text-slate-700 mt-1">
                              {t.body}
                            </p>
                          </li>
                        ))}
                      </ul>
                    </details>
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
