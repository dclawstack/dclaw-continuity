"use client";

import { useEffect, useState } from "react";
import { Shield, Trash2 } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { api, type Vendor } from "@/lib/api";

const RISK_VARIANT: Record<string, string> = {
  low: "bg-green-100 text-green-700",
  medium: "bg-yellow-100 text-yellow-700",
  high: "bg-orange-100 text-orange-700",
  critical: "bg-red-100 text-red-700",
};

export default function VendorsPage() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [services, setServices] = useState("");
  const [tier, setTier] = useState("tier-2");
  const [busy, setBusy] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [assessSummaries, setAssessSummaries] = useState<
    Record<string, { score: number; risk: string; summary: string }>
  >({});

  async function refresh() {
    try {
      setVendors(await api.vendors.list());
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed to load");
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setBusy("create");
    setErr(null);
    try {
      await api.vendors.create({
        name,
        description,
        services_provided: services,
        tier,
      });
      setName("");
      setDescription("");
      setServices("");
      setTier("tier-2");
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed");
    } finally {
      setBusy(null);
    }
  }

  async function assess(v: Vendor) {
    setBusy(v.id);
    setErr(null);
    try {
      const a = await api.vendors.assess(v.id);
      setAssessSummaries((m) => ({
        ...m,
        [v.id]: {
          score: a.readiness_score,
          risk: a.risk_level,
          summary: a.summary,
        },
      }));
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed");
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Vendor continuity</h1>
        <p className="text-sm text-slate-500">
          Register critical vendors and have the Copilot score their continuity
          readiness.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Add vendor</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={add}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            <div>
              <Label className="text-xs">Name</Label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="e.g. Acquiring bank"
              />
            </div>
            <div>
              <Label className="text-xs">Tier</Label>
              <select
                value={tier}
                onChange={(e) => setTier(e.target.value)}
                className="mt-1 flex h-10 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
              >
                <option value="tier-1">tier-1</option>
                <option value="tier-2">tier-2</option>
                <option value="tier-3">tier-3</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <Label className="text-xs">Description</Label>
              <Input
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
            <div className="md:col-span-2">
              <Label className="text-xs">Services provided</Label>
              <Input
                value={services}
                onChange={(e) => setServices(e.target.value)}
                placeholder="e.g. card settlement, fraud scoring"
              />
            </div>
            <div className="md:col-span-2">
              <Button type="submit" disabled={busy === "create"}>
                {busy === "create" ? "Adding…" : "Add vendor"}
              </Button>
            </div>
          </form>
          {err && <p className="text-sm text-red-600 mt-3">{err}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Vendors</CardTitle>
        </CardHeader>
        <CardContent>
          {vendors.length === 0 ? (
            <p className="text-sm text-slate-500">No vendors yet.</p>
          ) : (
            <ul className="space-y-3">
              {vendors.map((v) => {
                const a = assessSummaries[v.id];
                return (
                  <li key={v.id} className="border rounded p-3">
                    <div className="flex items-center gap-3">
                      <Badge variant="secondary">{v.tier}</Badge>
                      <div className="flex-1">
                        <div className="font-medium">{v.name}</div>
                        <div className="text-xs text-slate-500">
                          {v.services_provided || "(no services recorded)"}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-semibold">
                          {v.readiness_score || "—"}/100
                        </div>
                        <div className="text-xs text-slate-500">readiness</div>
                      </div>
                      <Button
                        size="sm"
                        onClick={() => assess(v)}
                        disabled={busy === v.id}
                      >
                        <Shield className="h-4 w-4 mr-1" />
                        {busy === v.id ? "Assessing…" : "AI assess"}
                      </Button>
                    </div>
                    {a && (
                      <div className="mt-3 flex items-start gap-3">
                        <Badge className={RISK_VARIANT[a.risk] ?? ""}>
                          {a.risk} risk
                        </Badge>
                        <p className="text-sm text-slate-600">{a.summary}</p>
                      </div>
                    )}
                  </li>
                );
              })}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
