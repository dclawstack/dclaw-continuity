"use client";

import { useEffect, useState } from "react";
import {
  AlertTriangle,
  Briefcase,
  ClipboardCheck,
  Database,
  FileText,
  LifeBuoy,
  PlayCircle,
  RotateCcw,
  Shield,
  Sparkles,
  Star,
} from "lucide-react";

const STORAGE_KEY = "dclaw_demo_seeded";

// Tab keys + labels
const TABS = [
  { key: "functions", label: "Functions", icon: Briefcase },
  { key: "bcp", label: "BCP", icon: FileText },
  { key: "impact", label: "Impact", icon: AlertTriangle },
  { key: "recovery", label: "Recovery", icon: LifeBuoy },
  { key: "exercise", label: "Exercise", icon: ClipboardCheck },
  { key: "vendor", label: "Vendor", icon: Shield },
] as const;

type TabKey = (typeof TABS)[number]["key"];

export function DemoSection() {
  const [seeded, setSeeded] = useState(false);
  const [hydrated, setHydrated] = useState(false);
  const [tab, setTab] = useState<TabKey>("functions");

  useEffect(() => {
    setHydrated(true);
    setSeeded(localStorage.getItem(STORAGE_KEY) === "true");
  }, []);

  function seed() {
    localStorage.setItem(STORAGE_KEY, "true");
    setSeeded(true);
    setTab("functions");
  }

  function clear() {
    localStorage.removeItem(STORAGE_KEY);
    setSeeded(false);
  }

  return (
    <section id="demo" className="py-24 bg-white border-t border-slate-100 scroll-mt-8">
      <div className="max-w-6xl mx-auto px-6">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
            <PlayCircle className="h-3 w-3" />
            Live demo
          </div>
          <h2 className="mt-4 text-3xl md:text-4xl font-bold text-slate-900">
            Try the output without signing up.
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Seed a sample workspace and click through every artifact the
            Copilot produces — real shapes, real prose. Data lives in your
            browser; clear it any time.
          </p>
        </div>

        <div className="mt-10 rounded-2xl border border-slate-200 bg-gradient-to-br from-slate-50 to-white shadow-sm overflow-hidden">
          {/* Controls header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-200 bg-white px-5 py-3">
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <Database className="h-4 w-4 text-blue-500" />
              <span className="font-medium text-slate-900">
                Demo workspace
              </span>
              {hydrated && (
                <span className="text-xs text-slate-500">
                  · {seeded ? "populated" : "empty"}
                </span>
              )}
            </div>
            <div className="flex gap-2">
              {!seeded ? (
                <button
                  onClick={seed}
                  disabled={!hydrated}
                  className="inline-flex items-center gap-2 rounded-md bg-blue-600 text-white px-4 py-1.5 text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  <Sparkles className="h-4 w-4" /> Seed demo data
                </button>
              ) : (
                <button
                  onClick={clear}
                  className="inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white text-slate-700 px-4 py-1.5 text-sm font-medium hover:bg-slate-50 transition-colors"
                >
                  <RotateCcw className="h-4 w-4" /> Clear data
                </button>
              )}
            </div>
          </div>

          {/* Empty vs populated */}
          {!seeded ? (
            <EmptyState onSeed={seed} hydrated={hydrated} />
          ) : (
            <PopulatedState tab={tab} setTab={setTab} />
          )}
        </div>
      </div>
    </section>
  );
}

function EmptyState({
  onSeed,
  hydrated,
}: {
  onSeed: () => void;
  hydrated: boolean;
}) {
  return (
    <div className="px-6 py-20 text-center">
      <div className="mx-auto h-12 w-12 rounded-full bg-slate-100 flex items-center justify-center">
        <Database className="h-6 w-6 text-slate-400" />
      </div>
      <p className="mt-4 text-slate-600 max-w-md mx-auto">
        Your demo workspace is empty. Click below to populate it with a
        critical Payments function, an AI-drafted BCP, a quantified Black
        Friday outage impact, three recovery strategies, an exercise score,
        and a vendor assessment.
      </p>
      <button
        onClick={onSeed}
        disabled={!hydrated}
        className="mt-6 inline-flex items-center gap-2 rounded-md bg-blue-600 text-white px-5 py-2 text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
      >
        <Sparkles className="h-4 w-4" /> Seed demo data
      </button>
    </div>
  );
}

function PopulatedState({
  tab,
  setTab,
}: {
  tab: TabKey;
  setTab: (t: TabKey) => void;
}) {
  return (
    <div>
      {/* Tab bar */}
      <div className="flex items-center gap-1 px-4 py-2 border-b border-slate-200 bg-white overflow-x-auto">
        {TABS.map(({ key, label, icon: Icon }) => {
          const active = tab === key;
          return (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={
                "inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm whitespace-nowrap transition-colors " +
                (active
                  ? "bg-slate-900 text-white"
                  : "text-slate-600 hover:bg-slate-100")
              }
            >
              <Icon className="h-3.5 w-3.5" />
              {label}
            </button>
          );
        })}
      </div>

      {/* Tab content */}
      <div className="p-6 min-h-[360px]">
        {tab === "functions" && <FunctionsTab />}
        {tab === "bcp" && <BCPTab />}
        {tab === "impact" && <ImpactTab />}
        {tab === "recovery" && <RecoveryTab />}
        {tab === "exercise" && <ExerciseTab />}
        {tab === "vendor" && <VendorTab />}
      </div>
    </div>
  );
}

/* ── tab contents ──────────────────────────────────────────── */

const CRIT_VARIANT: Record<string, string> = {
  critical: "bg-red-100 text-red-700",
  high: "bg-orange-100 text-orange-700",
  medium: "bg-yellow-100 text-yellow-700",
  low: "bg-slate-100 text-slate-700",
};

function FunctionsTab() {
  const items = [
    {
      name: "Online Checkout",
      owner: "Engineering",
      criticality: "critical",
      rto: 30,
      rpo: 5,
    },
    {
      name: "Payments",
      owner: "Finance Ops",
      criticality: "critical",
      rto: 60,
      rpo: 15,
    },
    {
      name: "Customer Support",
      owner: "Operations",
      criticality: "high",
      rto: 240,
      rpo: 60,
    },
    {
      name: "Order Fulfillment",
      owner: "Logistics",
      criticality: "high",
      rto: 480,
      rpo: 60,
    },
  ];
  return (
    <ul className="divide-y divide-slate-100">
      {items.map((f) => (
        <li
          key={f.name}
          className="py-3 flex items-center gap-3 first:pt-0 last:pb-0"
        >
          <span
            className={
              "rounded-full px-2 py-0.5 text-xs font-medium " +
              (CRIT_VARIANT[f.criticality] ?? "")
            }
          >
            {f.criticality}
          </span>
          <div className="flex-1">
            <div className="font-medium text-slate-900">{f.name}</div>
            <div className="text-xs text-slate-500">{f.owner}</div>
          </div>
          <div className="text-right text-xs text-slate-500">
            RTO {f.rto}m · RPO {f.rpo}m
          </div>
        </li>
      ))}
    </ul>
  );
}

function BCPTab() {
  return (
    <div className="space-y-4">
      <div>
        <div className="text-xs uppercase tracking-wider text-slate-500">
          Title
        </div>
        <div className="text-lg font-semibold text-slate-900">
          Payments Continuity Plan — Regional Datacenter Outage
        </div>
        <div className="text-sm text-slate-600 mt-1">
          Maintain card-processing capability for ecommerce during a regional
          datacenter outage at peak hours, ensuring zero revenue loss and
          full PCI-DSS compliance.
        </div>
      </div>
      <div>
        <div className="text-xs uppercase tracking-wider text-slate-500 mb-1">
          Objectives
        </div>
        <ul className="text-sm text-slate-700 list-disc pl-5 space-y-1">
          <li>Restore checkout to ≤15 min RTO with ≤5 min RPO</li>
          <li>Maintain ≥95% of baseline payment conversion rate</li>
          <li>Issue customer comms within 30 min of incident declaration</li>
        </ul>
      </div>
      <div>
        <div className="text-xs uppercase tracking-wider text-slate-500 mb-1">
          Procedure
        </div>
        <ol className="text-sm text-slate-700 list-decimal pl-5 space-y-1">
          <li>SOC declares incident, pages on-call DBA + VP E-commerce</li>
          <li>Failover transaction DB to Region-B standby cluster (~5 min)</li>
          <li>Update DNS to route checkout API to Region-B (~3 min)</li>
          <li>Validate payment conversion rate vs baseline</li>
          <li>Publish customer-facing status update</li>
          <li>Begin PCI forensic containment workflow</li>
          <li>Plan failback to primary once root cause is contained</li>
        </ol>
      </div>
      <div className="flex items-center gap-2 text-xs">
        <span className="rounded-full bg-slate-100 px-2 py-0.5 text-slate-700">
          status: draft
        </span>
        <span className="rounded-full bg-orange-100 px-2 py-0.5 text-orange-700">
          6 gaps identified
        </span>
      </div>
    </div>
  );
}

function ImpactTab() {
  return (
    <div className="space-y-4">
      <div>
        <div className="text-xs uppercase tracking-wider text-slate-500">
          Scenario
        </div>
        <div className="text-lg font-semibold text-slate-900">
          8-hour datacenter outage during Black Friday peak
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <StatBlock
          label="Revenue impact"
          value="$2.4M"
          accent="text-red-600"
        />
        <StatBlock
          label="Operational"
          value="10 / 10"
          accent="text-orange-600"
        />
        <StatBlock
          label="Reputation"
          value="9 / 10"
          accent="text-orange-600"
        />
      </div>
      <div>
        <div className="text-xs uppercase tracking-wider text-slate-500 mb-1">
          Narrative
        </div>
        <p className="text-sm text-slate-700">
          Complete loss of card processing during Black Friday peak eliminates
          all online revenue, triggers card-network penalties, and drives
          customers to competitors. Social media erupts within 15 minutes;
          regulatory disclosure required if cardholder data is exposed.
        </p>
      </div>
      <div>
        <div className="text-xs uppercase tracking-wider text-slate-500 mb-1">
          Timeline
        </div>
        <ul className="text-sm text-slate-700 space-y-1">
          <li>
            <strong>First hour:</strong> checkout queue grows; SLAs breach
          </li>
          <li>
            <strong>First day:</strong> social media backlash; press picks
            up the outage
          </li>
          <li>
            <strong>First week:</strong> customer churn measurable in
            recurring orders
          </li>
        </ul>
      </div>
    </div>
  );
}

function StatBlock({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent: string;
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">
        {label}
      </div>
      <div className={"mt-1 text-2xl font-semibold " + accent}>{value}</div>
    </div>
  );
}

function RecoveryTab() {
  const items = [
    {
      title: "Active-active multi-region cloud cluster",
      kind: "redundancy",
      cost: 240000,
      rto: 5,
      rpo: 1,
      recommended: true,
      rationale:
        "Real-time replication + automatic DNS/API failover. Meets RTO/RPO with margin.",
    },
    {
      title: "Warm standby in secondary cloud region",
      kind: "warm_site",
      cost: 120000,
      rto: 30,
      rpo: 5,
      recommended: false,
      rationale:
        "Lower cost, manual failover. Acceptable for non-peak windows; tight under Black Friday load.",
    },
    {
      title: "Cold DR with manual restore",
      kind: "cold_site",
      cost: 25000,
      rto: 480,
      rpo: 1440,
      recommended: false,
      rationale:
        "Last-resort. Misses Black Friday targets by hours; useful only for non-critical paths.",
    },
  ];
  return (
    <ul className="space-y-3">
      {items.map((s) => (
        <li
          key={s.title}
          className={
            "rounded-lg border p-4 " +
            (s.recommended
              ? "border-yellow-300 bg-yellow-50"
              : "border-slate-200 bg-white")
          }
        >
          <div className="flex items-start gap-2">
            {s.recommended && (
              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400 mt-0.5" />
            )}
            <div className="flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-medium text-slate-900">{s.title}</span>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-700">
                  {s.kind.replace("_", " ")}
                </span>
              </div>
              <div className="text-xs text-slate-500 mt-1">
                RTO {s.rto}m · RPO {s.rpo}m
              </div>
              <p className="text-sm text-slate-700 mt-2">{s.rationale}</p>
            </div>
            <div className="text-right">
              <div className="font-semibold text-slate-900">
                ${(s.cost / 1000).toFixed(0)}k
              </div>
              <div className="text-xs text-slate-500">/ year</div>
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}

function ExerciseTab() {
  return (
    <div className="space-y-4">
      <div>
        <div className="text-xs uppercase tracking-wider text-slate-500">
          Exercise
        </div>
        <div className="text-lg font-semibold text-slate-900">
          Black-Friday Ransomware Checkout Drill
        </div>
        <div className="text-sm text-slate-600 mt-1">
          Tuesday 09:42, 72h before Black-Friday launch. Anomalous encrypted
          file extensions detected on the primary transaction DB cluster;
          checkout API begins returning 503 within four minutes.
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-slate-900 text-white px-4 py-2">
          <div className="text-xs uppercase tracking-wider text-slate-300">
            Score
          </div>
          <div className="text-2xl font-semibold">68 / 100</div>
        </div>
        <div className="flex-1">
          <div className="text-sm text-slate-700">
            Team responded within 14 minutes; comms went out at T+8m.
            Failover took 22 minutes (target: ≤15m). Recovery point lagged
            by 45 minutes — last snapshot was older than the 5-minute RPO.
          </div>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
        <Bullet
          variant="green"
          title="Strengths"
          items={[
            "PCI containment ran within target",
            "Customer comms beat 30-min SLA",
          ]}
        />
        <Bullet
          variant="red"
          title="Weaknesses"
          items={[
            "RTO missed by 7 minutes",
            "Snapshot age 9× over RPO target",
          ]}
        />
        <Bullet
          variant="blue"
          title="Recommendations"
          items={[
            "Reduce backup interval to ≤5 min",
            "Automate Region-B failover playbook",
          ]}
        />
      </div>
    </div>
  );
}

function Bullet({
  variant,
  title,
  items,
}: {
  variant: "green" | "red" | "blue";
  title: string;
  items: string[];
}) {
  const accent =
    variant === "green"
      ? "border-l-green-400"
      : variant === "red"
        ? "border-l-red-400"
        : "border-l-blue-400";
  return (
    <div className={"rounded-lg border border-slate-200 border-l-4 bg-white p-3 " + accent}>
      <div className="text-xs uppercase tracking-wider text-slate-500 mb-1">
        {title}
      </div>
      <ul className="space-y-1 text-slate-700">
        {items.map((i) => (
          <li key={i}>• {i}</li>
        ))}
      </ul>
    </div>
  );
}

function VendorTab() {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-slate-900 text-white px-4 py-2">
          <div className="text-xs uppercase tracking-wider text-slate-300">
            Readiness
          </div>
          <div className="text-2xl font-semibold">85 / 100</div>
        </div>
        <div className="flex-1">
          <div className="font-medium text-slate-900">Stripe Inc</div>
          <div className="text-xs text-slate-500">
            tier-1 · card processing, fraud detection
          </div>
          <span className="inline-block mt-1 rounded-full bg-yellow-100 px-2 py-0.5 text-xs text-yellow-700">
            medium risk
          </span>
        </div>
      </div>
      <p className="text-sm text-slate-700">
        Stripe demonstrates mature continuity practices with redundant global
        infrastructure and a strong compliance posture, but single-vendor
        dependency for 100% of US card volume creates systemic risk.
      </p>
      <div>
        <div className="text-xs uppercase tracking-wider text-slate-500 mb-2">
          Monitoring indicators
        </div>
        <ul className="text-sm text-slate-700 space-y-1">
          <li>• Stripe status page incident frequency &gt;2 per quarter</li>
          <li>• API error rate spikes &gt;0.1% for 5+ minutes</li>
          <li>• Settlement delays &gt;24 hours</li>
        </ul>
      </div>
    </div>
  );
}
