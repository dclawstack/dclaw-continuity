"use client";

import { useState } from "react";
import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface BusinessContinuityPlan {
  id: string;
  business_unit: string;
  impact_level: string;
  rto_hours: number;
  rpo_hours: number;
  backup_sites: string[];
  recovery_status: string;
  created_at: string
}

export default function Dashboard() {
  const [businessUnit, setBusinessUnit] = useState("");
const [impactLevel, setImpactLevel] = useState("Low");
  const [businessContinuityPlan, setBusinessContinuityPlan] = useState<BusinessContinuityPlan | null>(null);
  const [extraData, setExtraData] = useState<any>(null);
const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    if (!businessUnit || !impactLevel) return;
    setLoading(true);
    try {
      const res = await fetch("/plans", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
        businessUnit: businessUnit,
        impact_level: impactLevel,
        }),
      });
      const data = await res.json();
      setBusinessContinuityPlan(data);
      const extraRes = await fetch(`/plans/${plan_id}/drills`);
      const extraData = await extraRes.json();
      setExtraData(extraData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <div className="flex items-center gap-3">
        <RefreshCw className="w-8 h-8" style={{ color: "#16A34A" }} />
        <div>
          <h1 className="text-2xl font-bold">DClaw Continuity</h1>
          <p className="text-sm text-slate-500">Business continuity planning</p>
        </div>
        <Badge className="ml-auto" style={{ backgroundColor: "#16A34A" }}>Operations</Badge>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Generate BCP</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Business unit</label>
              <Input value={businessUnit} onChange={(e) => setBusinessUnit(e.target.value)} placeholder="e.g. Engineering" />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Impact level</label>
              <select value={impactLevel} onChange={(e) => setImpactLevel(e.target.value)} className="flex h-9 w-full rounded-md border border-slate-200 bg-transparent px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-brand">
                <option value="Low">Low</option><option value="Medium">Medium</option><option value="High">High</option><option value="Critical">Critical</option>
              </select>
            </div>
          </div>
          <Button onClick={handleSubmit} disabled={loading || !businessUnit || !impactLevel}>
            {loading ? "Processing..." : "Generate BCP"}
          </Button>
        </CardContent>
      </Card>

      {businessContinuityPlan && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

          <Card>
            <CardHeader>
              <CardTitle>BCP Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p><strong>ID:</strong> {plan.id}</p>
              <p><strong>Business Unit:</strong> {plan.business_unit}</p>
              <p><strong>Impact Level:</strong> {plan.impact_level}</p>
              <p><strong>RTO:</strong> {plan.rto_hours + ' hours'}</p>
              <p><strong>RPO:</strong> {plan.rpo_hours + ' hours'}</p>
              <p><strong>Recovery Status:</strong> {plan.recovery_status}</p>
              <p><strong>Created:</strong> {new Date(plan.created_at).toLocaleString()}</p>
            </CardContent>
          </Card>
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Backup Sites</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {plan.backup_sites.map((item: string, i: number) => (
                  <Badge key={i} variant="secondary">{item}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Drill History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {extraData?.map((rec: any, i: number) => (
                  <div key={i} className="flex items-center justify-between p-2 bg-slate-50 rounded">
                    <span className="text-sm">{rec.date}</span>
                    <Badge variant={rec.result === "Passed" ? "default" : "secondary"}>{rec.result}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
