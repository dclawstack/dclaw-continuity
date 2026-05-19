"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, ServerCog, Sparkles, XCircle } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  api,
  type ITDRPlan,
  type ITSystem,
  type SystemTier,
} from "@/lib/api";

const TIERS: SystemTier[] = ["tier-0", "tier-1", "tier-2", "tier-3"];

export default function ITDRPage() {
  const [systems, setSystems] = useState<ITSystem[]>([]);
  const [plans, setPlans] = useState<ITDRPlan[]>([]);
  const [name, setName] = useState("");
  const [owner, setOwner] = useState("");
  const [tier, setTier] = useState<SystemTier>("tier-2");
  const [rto, setRto] = useState(30);
  const [rpo, setRpo] = useState(5);
  const [backup, setBackup] = useState("");
  const [selected, setSelected] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function refresh() {
    try {
      const [s, p] = await Promise.all([
        api.itDr.listSystems(),
        api.itDr.listPlans(),
      ]);
      setSystems(s);
      setPlans(p);
      if (!selected && s.length > 0) setSelected(s[0].id);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed to load");
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function addSystem(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setBusy("system");
    try {
      await api.itDr.createSystem({
        name,
        owner,
        tier,
        rto_minutes: rto,
        rpo_minutes: rpo,
        backup_strategy: backup,
      });
      setName("");
      setOwner("");
      setBackup("");
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed");
    } finally {
      setBusy(null);
    }
  }

  async function generate() {
    if (!selected) return;
    setBusy("generate");
    setErr(null);
    try {
      await api.itDr.generatePlan(selected);
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed");
    } finally {
      setBusy(null);
    }
  }

  async function recordTest(planId: string, passed: boolean) {
    setBusy(planId);
    try {
      await api.itDr.recordTest(planId, passed);
      await refresh();
    } finally {
      setBusy(null);
    }
  }

  const systemsById = Object.fromEntries(systems.map((s) => [s.id, s]));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">IT disaster recovery</h1>
        <p className="text-sm text-slate-500">
          Register systems, generate AI-drafted DR plans aligned to RTO/RPO,
          and record test runs.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ServerCog className="h-5 w-5 text-blue-500" /> Add system
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={addSystem}
            className="grid grid-cols-1 md:grid-cols-3 gap-3"
          >
            <div className="md:col-span-2">
              <Label className="text-xs">Name</Label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div>
              <Label className="text-xs">Owner</Label>
              <Input value={owner} onChange={(e) => setOwner(e.target.value)} />
            </div>
            <div>
              <Label className="text-xs">Tier</Label>
              <select
                value={tier}
                onChange={(e) => setTier(e.target.value as SystemTier)}
                className="mt-1 flex h-10 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
              >
                {TIERS.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <Label className="text-xs">RTO (min)</Label>
              <Input
                type="number"
                min={0}
                value={rto}
                onChange={(e) => setRto(Number(e.target.value))}
              />
            </div>
            <div>
              <Label className="text-xs">RPO (min)</Label>
              <Input
                type="number"
                min={0}
                value={rpo}
                onChange={(e) => setRpo(Number(e.target.value))}
              />
            </div>
            <div className="md:col-span-3">
              <Label className="text-xs">Backup strategy</Label>
              <Input
                value={backup}
                onChange={(e) => setBackup(e.target.value)}
                placeholder="e.g. WAL streaming + 5m snapshots"
              />
            </div>
            <div className="md:col-span-3">
              <Button type="submit" disabled={busy === "system"}>
                {busy === "system" ? "Adding…" : "Add system"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-500" /> Generate DR plan
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {systems.length === 0 ? (
            <p className="text-sm text-slate-500">Add a system first.</p>
          ) : (
            <>
              <div>
                <Label className="text-xs">System</Label>
                <select
                  value={selected}
                  onChange={(e) => setSelected(e.target.value)}
                  className="mt-1 flex h-10 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
                >
                  {systems.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} ({s.tier})
                    </option>
                  ))}
                </select>
              </div>
              <Button onClick={generate} disabled={busy === "generate"}>
                {busy === "generate" ? "Generating…" : "Generate plan"}
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
            <p className="text-sm text-slate-500">No DR plans yet.</p>
          ) : (
            <ul className="space-y-3">
              {plans.map((p) => (
                <li key={p.id} className="border rounded p-3 space-y-2">
                  <div className="flex items-center gap-3">
                    <div className="flex-1">
                      <div className="font-medium">{p.title}</div>
                      <div className="text-xs text-slate-500">
                        {systemsById[p.system_id]?.name ?? "—"} ·{" "}
                        {p.test_plan.length} test
                        {p.test_plan.length === 1 ? "" : "s"} scheduled
                      </div>
                    </div>
                    {p.last_test_passed != null && (
                      <Badge
                        className={
                          p.last_test_passed
                            ? "bg-green-100 text-green-700"
                            : "bg-red-100 text-red-700"
                        }
                      >
                        last test {p.last_test_passed ? "passed" : "failed"}
                      </Badge>
                    )}
                  </div>
                  {p.summary && <p className="text-sm text-slate-600">{p.summary}</p>}
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => recordTest(p.id, true)}
                      disabled={busy === p.id}
                    >
                      <CheckCircle2 className="h-4 w-4 mr-1" /> Record pass
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => recordTest(p.id, false)}
                      disabled={busy === p.id}
                    >
                      <XCircle className="h-4 w-4 mr-1" /> Record fail
                    </Button>
                  </div>
                  <details className="text-sm">
                    <summary className="cursor-pointer text-slate-600">
                      Procedure JSON
                    </summary>
                    <pre className="mt-2 text-xs bg-slate-50 p-3 rounded overflow-x-auto">
                      {JSON.stringify(p.procedure, null, 2)}
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
