"use client";

import { useEffect, useState } from "react";
import { Factory, Sparkles } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { api, type Supplier } from "@/lib/api";

function probColor(p: number): string {
  if (p >= 75) return "bg-red-100 text-red-700";
  if (p >= 50) return "bg-orange-100 text-orange-700";
  if (p >= 25) return "bg-yellow-100 text-yellow-700";
  return "bg-green-100 text-green-700";
}

export default function SupplyChainPage() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [name, setName] = useState("");
  const [category, setCategory] = useState("");
  const [region, setRegion] = useState("");
  const [criticality, setCriticality] = useState("medium");
  const [busy, setBusy] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [latest, setLatest] = useState<
    Record<string, { prob: number; summary: string; drivers: unknown[] }>
  >({});

  async function refresh() {
    try {
      setSuppliers(await api.supplyChain.list());
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
    try {
      await api.supplyChain.create({
        name,
        category,
        region,
        criticality,
      });
      setName("");
      setCategory("");
      setRegion("");
      setCriticality("medium");
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed");
    } finally {
      setBusy(null);
    }
  }

  async function assess(s: Supplier) {
    setBusy(s.id);
    setErr(null);
    try {
      const a = await api.supplyChain.assess(s.id);
      setLatest((m) => ({
        ...m,
        [s.id]: {
          prob: a.disruption_probability,
          summary: a.summary,
          drivers: a.risk_drivers,
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
        <h1 className="text-2xl font-bold">Supply chain continuity</h1>
        <p className="text-sm text-slate-500">
          Register critical suppliers and let the Copilot predict disruption
          probability and recommend alternatives.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Add supplier</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={add}
            className="grid grid-cols-1 md:grid-cols-2 gap-3"
          >
            <div>
              <Label className="text-xs">Name</Label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div>
              <Label className="text-xs">Category</Label>
              <Input
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              />
            </div>
            <div>
              <Label className="text-xs">Region</Label>
              <Input
                value={region}
                onChange={(e) => setRegion(e.target.value)}
              />
            </div>
            <div>
              <Label className="text-xs">Criticality</Label>
              <select
                value={criticality}
                onChange={(e) => setCriticality(e.target.value)}
                className="mt-1 flex h-10 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
              >
                <option value="low">low</option>
                <option value="medium">medium</option>
                <option value="high">high</option>
                <option value="critical">critical</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <Button type="submit" disabled={busy === "create"}>
                {busy === "create" ? "Adding…" : "Add supplier"}
              </Button>
            </div>
          </form>
          {err && <p className="text-sm text-red-600 mt-3">{err}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Factory className="h-5 w-5 text-blue-500" /> Suppliers
          </CardTitle>
        </CardHeader>
        <CardContent>
          {suppliers.length === 0 ? (
            <p className="text-sm text-slate-500">No suppliers yet.</p>
          ) : (
            <ul className="space-y-3">
              {suppliers.map((s) => {
                const l = latest[s.id];
                return (
                  <li key={s.id} className="border rounded p-3">
                    <div className="flex items-center gap-3">
                      <Badge variant="secondary">{s.criticality}</Badge>
                      <div className="flex-1">
                        <div className="font-medium">{s.name}</div>
                        <div className="text-xs text-slate-500">
                          {s.category || "no category"} ·{" "}
                          {s.region || "no region"}
                        </div>
                      </div>
                      {s.disruption_probability > 0 && (
                        <Badge className={probColor(s.disruption_probability)}>
                          {s.disruption_probability}% disruption risk
                        </Badge>
                      )}
                      <Button
                        size="sm"
                        onClick={() => assess(s)}
                        disabled={busy === s.id}
                      >
                        <Sparkles className="h-4 w-4 mr-1" />
                        {busy === s.id ? "Predicting…" : "Predict"}
                      </Button>
                    </div>
                    {l && (
                      <div className="mt-2 text-sm">
                        <p className="text-slate-700">{l.summary}</p>
                        <ul className="list-disc pl-5 text-xs text-slate-500 mt-1">
                          {l.drivers
                            .slice(0, 4)
                            .map((d, i) => (
                              <li key={i}>
                                {typeof d === "string"
                                  ? d
                                  : JSON.stringify(d)}
                              </li>
                            ))}
                        </ul>
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
