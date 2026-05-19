"use client";

import { useEffect, useState } from "react";
import { Building2, Sparkles, Trash2 } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  api,
  type BusinessFunction,
  type SiteKind,
  type WorkAreaPlan,
  type WorkAreaSite,
} from "@/lib/api";

const SITE_KINDS: SiteKind[] = [
  "alternate_office",
  "remote",
  "hot_site",
  "warm_site",
  "cold_site",
  "coworking",
  "other",
];

export default function WorkAreaPage() {
  const [sites, setSites] = useState<WorkAreaSite[]>([]);
  const [functions, setFunctions] = useState<BusinessFunction[]>([]);
  const [plans, setPlans] = useState<WorkAreaPlan[]>([]);
  const [siteName, setSiteName] = useState("");
  const [siteKind, setSiteKind] = useState<SiteKind>("remote");
  const [seats, setSeats] = useState(50);
  const [remoteAccess, setRemoteAccess] = useState(true);
  const [selectedFn, setSelectedFn] = useState("");
  const [headcount, setHeadcount] = useState(20);
  const [busy, setBusy] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function refresh() {
    try {
      const [s, f, p] = await Promise.all([
        api.workArea.listSites(),
        api.functions.list(),
        api.workArea.listPlans(),
      ]);
      setSites(s);
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

  async function addSite(e: React.FormEvent) {
    e.preventDefault();
    if (!siteName.trim()) return;
    setBusy("site");
    try {
      await api.workArea.createSite({
        name: siteName,
        kind: siteKind,
        capacity_seats: seats,
        has_remote_access: remoteAccess,
      });
      setSiteName("");
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed");
    } finally {
      setBusy(null);
    }
  }

  async function deleteSite(id: string) {
    if (!confirm("Delete this site?")) return;
    await api.workArea.deleteSite(id);
    await refresh();
  }

  async function recommend() {
    if (!selectedFn) return;
    setBusy("recommend");
    setErr(null);
    try {
      await api.workArea.recommend(selectedFn, headcount);
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed");
    } finally {
      setBusy(null);
    }
  }

  const functionsById = Object.fromEntries(functions.map((f) => [f.id, f]));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Work area recovery</h1>
        <p className="text-sm text-slate-500">
          Register alternate work sites and let the Copilot recommend how to
          house disrupted functions.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5 text-blue-500" /> Sites
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <form
            onSubmit={addSite}
            className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end"
          >
            <div>
              <Label className="text-xs">Name</Label>
              <Input
                value={siteName}
                onChange={(e) => setSiteName(e.target.value)}
                required
              />
            </div>
            <div>
              <Label className="text-xs">Kind</Label>
              <select
                value={siteKind}
                onChange={(e) => setSiteKind(e.target.value as SiteKind)}
                className="mt-1 flex h-10 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
              >
                {SITE_KINDS.map((k) => (
                  <option key={k} value={k}>
                    {k}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <Label className="text-xs">Capacity</Label>
              <Input
                type="number"
                min={0}
                value={seats}
                onChange={(e) => setSeats(Number(e.target.value))}
              />
            </div>
            <div>
              <Label className="flex items-center gap-2 text-xs mt-5">
                <input
                  type="checkbox"
                  checked={remoteAccess}
                  onChange={(e) => setRemoteAccess(e.target.checked)}
                />
                Remote access
              </Label>
            </div>
            <div className="md:col-span-4">
              <Button type="submit" disabled={busy === "site"}>
                {busy === "site" ? "Adding…" : "Add site"}
              </Button>
            </div>
          </form>

          {sites.length === 0 ? (
            <p className="text-sm text-slate-500">No sites yet.</p>
          ) : (
            <ul className="divide-y">
              {sites.map((s) => (
                <li key={s.id} className="py-2 flex items-center gap-3">
                  <Badge variant="secondary">{s.kind}</Badge>
                  <div className="flex-1">
                    <div className="font-medium">{s.name}</div>
                    <div className="text-xs text-slate-500">
                      {s.location || "no location"} · {s.capacity_seats} seats
                      {s.has_remote_access ? " · remote" : ""}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => deleteSite(s.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-500" /> Recommend plan
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
                    {functions.map((f) => (
                      <option key={f.id} value={f.id}>
                        {f.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label className="text-xs">Headcount required</Label>
                  <Input
                    type="number"
                    min={0}
                    value={headcount}
                    onChange={(e) => setHeadcount(Number(e.target.value))}
                  />
                </div>
              </div>
              <Button onClick={recommend} disabled={busy === "recommend"}>
                {busy === "recommend" ? "Recommending…" : "Recommend"}
              </Button>
            </>
          )}
          {err && <p className="text-sm text-red-600">{err}</p>}
        </CardContent>
      </Card>

      {plans.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Plans</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {plans.map((p) => (
                <li key={p.id} className="border rounded p-3">
                  <div className="font-medium">
                    {functionsById[p.function_id]?.name ?? "—"} ·{" "}
                    {p.headcount_required} seats
                  </div>
                  <p className="text-sm text-slate-600 mt-1">{p.summary}</p>
                  <details className="text-sm mt-2">
                    <summary className="cursor-pointer text-slate-600">
                      Details
                    </summary>
                    <pre className="mt-2 text-xs bg-slate-50 p-3 rounded overflow-x-auto">
                      {JSON.stringify(p.details, null, 2)}
                    </pre>
                  </details>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
