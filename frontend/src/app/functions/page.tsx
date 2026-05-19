"use client";

import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  api,
  type BusinessFunction,
  type Criticality,
} from "@/lib/api";

const CRITICALITY: Criticality[] = ["low", "medium", "high", "critical"];

const CRITICALITY_VARIANT: Record<string, string> = {
  critical: "bg-red-100 text-red-700",
  high: "bg-orange-100 text-orange-700",
  medium: "bg-yellow-100 text-yellow-700",
  low: "bg-slate-100 text-slate-700",
};

export default function FunctionsPage() {
  const [functions, setFunctions] = useState<BusinessFunction[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [owner, setOwner] = useState("");
  const [criticality, setCriticality] = useState<Criticality>("medium");
  const [rto, setRto] = useState(60);
  const [rpo, setRpo] = useState(15);
  const [saving, setSaving] = useState(false);

  async function refresh() {
    setLoading(true);
    try {
      setFunctions(await api.functions.list());
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function createFn(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    setErr(null);
    try {
      await api.functions.create({
        name,
        description,
        owner,
        criticality,
        rto_minutes: rto,
        rpo_minutes: rpo,
      });
      setName("");
      setDescription("");
      setOwner("");
      setCriticality("medium");
      setRto(60);
      setRpo(15);
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed");
    } finally {
      setSaving(false);
    }
  }

  async function remove(id: string) {
    if (!confirm("Delete this function and all its plans?")) return;
    try {
      await api.functions.delete(id);
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed");
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Business functions</h1>
        <p className="text-sm text-slate-500">
          Critical capabilities that need continuity planning. Set RTO/RPO
          targets here.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Create function</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={createFn}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            <Field label="Name">
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="e.g. Order intake"
              />
            </Field>
            <Field label="Owner">
              <Input
                value={owner}
                onChange={(e) => setOwner(e.target.value)}
                placeholder="e.g. Operations"
              />
            </Field>
            <Field label="Description" className="md:col-span-2">
              <Input
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Short description"
              />
            </Field>
            <Field label="Criticality">
              <select
                value={criticality}
                onChange={(e) => setCriticality(e.target.value as Criticality)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
              >
                {CRITICALITY.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label="RTO (min)">
                <Input
                  type="number"
                  min={0}
                  value={rto}
                  onChange={(e) => setRto(Number(e.target.value))}
                />
              </Field>
              <Field label="RPO (min)">
                <Input
                  type="number"
                  min={0}
                  value={rpo}
                  onChange={(e) => setRpo(Number(e.target.value))}
                />
              </Field>
            </div>
            <div className="md:col-span-2">
              <Button type="submit" disabled={saving}>
                {saving ? "Creating…" : "Create function"}
              </Button>
            </div>
          </form>
          {err && <p className="text-sm text-red-600 mt-3">{err}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>All functions</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : functions.length === 0 ? (
            <p className="text-sm text-slate-500">No functions yet.</p>
          ) : (
            <ul className="divide-y">
              {functions.map((fn) => (
                <li
                  key={fn.id}
                  className="py-3 flex items-center gap-3"
                >
                  <Badge className={CRITICALITY_VARIANT[fn.criticality] ?? ""}>
                    {fn.criticality}
                  </Badge>
                  <div className="flex-1">
                    <div className="font-medium">{fn.name}</div>
                    <div className="text-xs text-slate-500">
                      {fn.owner || "no owner"} · RTO {fn.rto_minutes}m · RPO{" "}
                      {fn.rpo_minutes}m
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => remove(fn.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function Field({
  label,
  className,
  children,
}: {
  label: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={className}>
      <Label className="text-xs">{label}</Label>
      <div className="mt-1">{children}</div>
    </div>
  );
}
