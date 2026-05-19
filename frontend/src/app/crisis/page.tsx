"use client";

import { useEffect, useState } from "react";
import { AlertCircle, ArrowRight } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  api,
  type ActivationStatus,
  type BCP,
  type CrisisActivation,
} from "@/lib/api";

const STATUS_VARIANT: Record<ActivationStatus, string> = {
  activated: "bg-red-100 text-red-700",
  recovering: "bg-orange-100 text-orange-700",
  stabilized: "bg-yellow-100 text-yellow-700",
  closed: "bg-slate-200 text-slate-500",
};

const NEXT_STATUS: Record<ActivationStatus, ActivationStatus | null> = {
  activated: "recovering",
  recovering: "stabilized",
  stabilized: "closed",
  closed: null,
};

export default function CrisisPage() {
  const [bcps, setBcps] = useState<BCP[]>([]);
  const [activations, setActivations] = useState<CrisisActivation[]>([]);
  const [selectedBcp, setSelectedBcp] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [externalId, setExternalId] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function refresh() {
    try {
      const [b, a] = await Promise.all([
        api.bcps.list(),
        api.crisis.list(false),
      ]);
      setBcps(b);
      setActivations(a);
      if (!selectedBcp && b.length > 0) setSelectedBcp(b[0].id);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed to load");
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function activate() {
    if (!selectedBcp || !title.trim()) return;
    setBusy("activate");
    setErr(null);
    try {
      await api.crisis.activate({
        bcp_id: selectedBcp,
        title,
        description,
        external_crisis_id: externalId || undefined,
        source: externalId ? "dclaw-crisis" : "manual",
      });
      setTitle("");
      setDescription("");
      setExternalId("");
      await refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed");
    } finally {
      setBusy(null);
    }
  }

  async function advance(a: CrisisActivation) {
    const next = NEXT_STATUS[a.status];
    if (!next) return;
    setBusy(a.id);
    try {
      await api.crisis.updateStatus(a.id, next, `advanced to ${next}`);
      await refresh();
    } finally {
      setBusy(null);
    }
  }

  const bcpsById = Object.fromEntries(bcps.map((b) => [b.id, b]));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Crisis activations</h1>
        <p className="text-sm text-slate-500">
          Activate a BCP when a real crisis occurs, then track recovery
          status. The upstream DClaw Crisis app can also activate via the API.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-red-500" /> Activate BCP
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {bcps.length === 0 ? (
            <p className="text-sm text-slate-500">No BCPs to activate.</p>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-xs">BCP</Label>
                  <select
                    value={selectedBcp}
                    onChange={(e) => setSelectedBcp(e.target.value)}
                    className="mt-1 flex h-10 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
                  >
                    {bcps.map((b) => (
                      <option key={b.id} value={b.id}>
                        {b.title}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label className="text-xs">
                    External crisis ID (optional)
                  </Label>
                  <Input
                    value={externalId}
                    onChange={(e) => setExternalId(e.target.value)}
                    placeholder="e.g. INC-2026-0521"
                  />
                </div>
                <div>
                  <Label className="text-xs">Title</Label>
                  <Input
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="e.g. Datacenter east-1 offline"
                  />
                </div>
                <div>
                  <Label className="text-xs">Description</Label>
                  <Input
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />
                </div>
              </div>
              <Button
                onClick={activate}
                variant="destructive"
                disabled={busy === "activate" || !title.trim()}
              >
                {busy === "activate" ? "Activating…" : "Activate"}
              </Button>
            </>
          )}
          {err && <p className="text-sm text-red-600">{err}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Activations</CardTitle>
        </CardHeader>
        <CardContent>
          {activations.length === 0 ? (
            <p className="text-sm text-slate-500">No activations yet.</p>
          ) : (
            <ul className="space-y-3">
              {activations.map((a) => (
                <li key={a.id} className="border rounded p-3">
                  <div className="flex items-center gap-3">
                    <Badge className={STATUS_VARIANT[a.status]}>
                      {a.status}
                    </Badge>
                    <div className="flex-1">
                      <div className="font-medium">{a.title}</div>
                      <div className="text-xs text-slate-500">
                        {bcpsById[a.bcp_id]?.title ?? "—"} ·{" "}
                        {new Date(a.activated_at).toLocaleString()}
                        {a.external_crisis_id && ` · ${a.external_crisis_id}`}
                      </div>
                    </div>
                    {NEXT_STATUS[a.status] && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => advance(a)}
                        disabled={busy === a.id}
                      >
                        Mark {NEXT_STATUS[a.status]}{" "}
                        <ArrowRight className="h-4 w-4 ml-1" />
                      </Button>
                    )}
                  </div>
                  {a.description && (
                    <p className="text-sm text-slate-600 mt-2">
                      {a.description}
                    </p>
                  )}
                  {a.timeline.length > 0 && (
                    <details className="mt-2 text-sm">
                      <summary className="cursor-pointer text-slate-600">
                        Timeline ({a.timeline.length})
                      </summary>
                      <ul className="mt-2 space-y-1 text-xs text-slate-600">
                        {a.timeline.map((t, i) => (
                          <li key={i}>
                            <code className="text-[10px]">
                              {new Date(t.at).toLocaleTimeString()}
                            </code>{" "}
                            <strong>{t.status}</strong>
                            {t.note ? ` — ${t.note}` : ""}
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
