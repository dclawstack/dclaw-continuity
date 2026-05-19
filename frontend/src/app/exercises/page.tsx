"use client";

import { useEffect, useState } from "react";
import { Play, Sparkles, ClipboardCheck } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { api, type BCP, type Exercise } from "@/lib/api";

const STATUS_VARIANT: Record<string, string> = {
  planned: "bg-slate-100 text-slate-700",
  running: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
  cancelled: "bg-slate-200 text-slate-500",
};

export default function ExercisesPage() {
  const [bcps, setBcps] = useState<BCP[]>([]);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [selectedBcp, setSelectedBcp] = useState("");
  const [focus, setFocus] = useState("");
  const [observations, setObservations] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function refresh() {
    try {
      const [b, e] = await Promise.all([
        api.bcps.list(),
        api.exercises.list(),
      ]);
      setBcps(b);
      setExercises(e);
      if (!selectedBcp && b.length > 0) setSelectedBcp(b[0].id);
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : "Failed to load");
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function generate() {
    if (!selectedBcp) return;
    setBusy("generate");
    setErr(null);
    try {
      await api.exercises.generate(selectedBcp, focus);
      setFocus("");
      await refresh();
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : "Failed");
    } finally {
      setBusy(null);
    }
  }

  async function start(id: string) {
    setBusy(id);
    try {
      await api.exercises.start(id);
      await refresh();
    } finally {
      setBusy(null);
    }
  }

  async function evaluate(id: string) {
    const obs = (observations[id] || "").trim();
    if (!obs) return;
    setBusy(id);
    setErr(null);
    try {
      await api.exercises.evaluate(id, obs);
      setObservations((o) => ({ ...o, [id]: "" }));
      await refresh();
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : "Failed");
    } finally {
      setBusy(null);
    }
  }

  const bcpsById = Object.fromEntries(bcps.map((b) => [b.id, b]));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Exercise management</h1>
        <p className="text-sm text-slate-500">
          Plan and run continuity exercises with AI-generated scenarios and
          evaluation.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-500" /> Generate exercise
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {bcps.length === 0 ? (
            <p className="text-sm text-slate-500">
              Create a BCP first so we have something to exercise.
            </p>
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
                  <Label className="text-xs">Focus (optional)</Label>
                  <Input
                    value={focus}
                    onChange={(e) => setFocus(e.target.value)}
                    placeholder="e.g. ransomware on transaction DB"
                  />
                </div>
              </div>
              <Button onClick={generate} disabled={busy === "generate"}>
                {busy === "generate" ? "Generating…" : "Generate scenario"}
              </Button>
            </>
          )}
          {err && <p className="text-sm text-red-600">{err}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>All exercises</CardTitle>
        </CardHeader>
        <CardContent>
          {exercises.length === 0 ? (
            <p className="text-sm text-slate-500">No exercises yet.</p>
          ) : (
            <ul className="space-y-4">
              {exercises.map((e) => (
                <li key={e.id} className="border rounded p-4 space-y-3">
                  <div className="flex items-center gap-3">
                    <Badge className={STATUS_VARIANT[e.status] ?? ""}>
                      {e.status}
                    </Badge>
                    <div className="flex-1">
                      <div className="font-medium">{e.name}</div>
                      <div className="text-xs text-slate-500">
                        {bcpsById[e.bcp_id]?.title ?? "—"}
                      </div>
                    </div>
                    {e.status === "completed" && (
                      <div className="text-right text-sm">
                        <div className="font-semibold">{e.score}/100</div>
                        <div className="text-xs text-slate-500">score</div>
                      </div>
                    )}
                  </div>
                  <details className="text-sm">
                    <summary className="cursor-pointer text-slate-600">
                      Scenario & objectives
                    </summary>
                    <div className="mt-2 space-y-2">
                      <p className="whitespace-pre-wrap text-slate-700">
                        {e.scenario}
                      </p>
                      <ul className="list-disc pl-5 text-slate-600">
                        {e.objectives.map((o, i) => (
                          <li key={i}>{o}</li>
                        ))}
                      </ul>
                    </div>
                  </details>
                  {e.status === "planned" && (
                    <Button
                      size="sm"
                      onClick={() => start(e.id)}
                      disabled={busy === e.id}
                    >
                      <Play className="h-4 w-4 mr-1" /> Start
                    </Button>
                  )}
                  {e.status === "running" && (
                    <div className="space-y-2">
                      <Label className="text-xs">
                        Operator observations
                      </Label>
                      <textarea
                        value={observations[e.id] || ""}
                        onChange={(ev) =>
                          setObservations((o) => ({
                            ...o,
                            [e.id]: ev.target.value,
                          }))
                        }
                        rows={3}
                        className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        placeholder="What happened? What worked? What didn't?"
                      />
                      <Button
                        size="sm"
                        onClick={() => evaluate(e.id)}
                        disabled={
                          busy === e.id || !(observations[e.id] || "").trim()
                        }
                      >
                        <ClipboardCheck className="h-4 w-4 mr-1" /> Evaluate
                      </Button>
                    </div>
                  )}
                  {e.status === "completed" && e.evaluation && (
                    <details className="text-sm">
                      <summary className="cursor-pointer text-slate-600">
                        Evaluation
                      </summary>
                      <pre className="mt-2 text-xs bg-slate-50 p-3 rounded overflow-x-auto">
                        {JSON.stringify(e.evaluation, null, 2)}
                      </pre>
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
