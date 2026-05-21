import Link from "next/link";
import { DemoSection } from "@/components/landing/DemoSection";
import {
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  Briefcase,
  Building2,
  CheckCircle2,
  ClipboardCheck,
  Database,
  FileText,
  Gauge,
  GitBranch,
  LifeBuoy,
  Lock,
  Megaphone,
  Network,
  Search,
  ServerCog,
  ScrollText,
  Shield,
  Sparkles,
  Zap,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="bg-white">
      <Hero />
      <FeatureGroups />
      <CopilotSection />
      <DemoSection />
      <StackSection />
      <CTASection />
      <Footer />
    </div>
  );
}

function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div
        aria-hidden
        className="absolute inset-0 -z-10 bg-gradient-to-b from-blue-50 via-white to-white"
      />
      <div
        aria-hidden
        className="absolute -top-24 left-1/2 -z-10 h-96 w-[60rem] -translate-x-1/2 rounded-full bg-blue-200/30 blur-3xl"
      />
      <div className="max-w-6xl mx-auto px-6 pt-24 pb-32 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600 mb-6">
          <Sparkles className="h-3 w-3 text-blue-500" />
          AI-powered business continuity
        </div>
        <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-slate-900">
          Business continuity that
          <br />
          <span className="bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
            actually keeps up
          </span>
        </h1>
        <p className="mt-6 mx-auto max-w-2xl text-lg text-slate-600">
          DClaw Continuity drafts BCPs in minutes, scores your impact
          scenarios, recommends recovery strategies, and runs full
          exercises — every step backed by a Copilot that cites your own
          plans.
        </p>
        <div className="mt-10 flex flex-col sm:flex-row justify-center gap-3">
          <Link
            href="/signup"
            className="inline-flex items-center justify-center gap-2 rounded-md bg-slate-900 px-6 py-3 text-sm font-medium text-white shadow-sm hover:bg-slate-800 transition-colors"
          >
            Get started <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            href="/login"
            className="inline-flex items-center justify-center rounded-md border border-slate-200 bg-white px-6 py-3 text-sm font-medium text-slate-900 hover:bg-slate-50 transition-colors"
          >
            Sign in
          </Link>
        </div>
        <div className="mt-16 grid grid-cols-2 sm:grid-cols-4 gap-6 text-sm text-slate-500 max-w-3xl mx-auto">
          <Stat value="12" label="features shipped" />
          <Stat value="<20m" label="to draft a BCP" />
          <Stat value="768-dim" label="embeddings for RAG" />
          <Stat value="0" label="hard-coded secrets" />
        </div>
      </div>
    </section>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <div className="text-2xl font-semibold text-slate-900">{value}</div>
      <div className="text-xs uppercase tracking-wider text-slate-500 mt-1">
        {label}
      </div>
    </div>
  );
}

const GROUPS = [
  {
    title: "Planning & analysis",
    blurb:
      "Define the things that have to keep running and what it costs when they don't.",
    items: [
      {
        icon: Briefcase,
        title: "Business functions",
        desc: "Catalogue every critical capability with owner, criticality, RTO and RPO targets. The whole rest of the app pivots off this list.",
      },
      {
        icon: FileText,
        title: "BCP generation",
        desc: "AI drafts a full continuity plan — objectives, activation triggers, step-by-step procedures, communication plan, recovery targets — in under 20 minutes. Re-run gap analysis on demand.",
      },
      {
        icon: AlertTriangle,
        title: "Impact analysis",
        desc: "Model disruption scenarios. Get quantified revenue impact in USD plus operational and reputation scores on a 0-10 scale, with stakeholder and timeline breakdowns.",
      },
      {
        icon: LifeBuoy,
        title: "Recovery strategies",
        desc: "Recommend three cost-balanced strategies per function, spanning the cost / RTO / RPO trade-off — hot site, warm site, remote, third-party, manual workaround.",
      },
    ],
  },
  {
    title: "Operations",
    blurb:
      "Run drills and respond to real incidents with one consistent system of record.",
    items: [
      {
        icon: ClipboardCheck,
        title: "Exercise management",
        desc: "AI generates realistic scenarios per BCP, scores team responses against measurable objectives, and feeds findings back into the plan.",
      },
      {
        icon: AlertCircle,
        title: "Crisis activations",
        desc: "Activate a BCP manually or via webhook from DClaw Crisis. Track status transitions on an append-only timeline that auditors can read end to end.",
      },
      {
        icon: Megaphone,
        title: "Communication plans",
        desc: "Pre-draft stakeholder messaging across email, SMS, status page, intranet, and press — tone-tuned for the audience, escalation path included.",
      },
      {
        icon: Shield,
        title: "Vendor continuity",
        desc: "Score third-party readiness on a 0-100 scale with risk drivers, monitoring indicators, and concrete strengths and weaknesses.",
      },
    ],
  },
  {
    title: "Resilience & compliance",
    blurb:
      "The infrastructure-shaped pieces of continuity — sites, systems, suppliers, regulators.",
    items: [
      {
        icon: Building2,
        title: "Work area recovery",
        desc: "Plan alternate sites and remote-work fallback. The Copilot allocates seats across your registered sites, flags shortfalls, and drafts the remote-access test plan.",
      },
      {
        icon: ServerCog,
        title: "IT DR planning",
        desc: "Per-system DR procedures aligned to RTO and RPO targets, with cron-style test schedules and pass/fail recording. Built for the systems that recover the rest.",
      },
      {
        icon: Network,
        title: "Supply chain continuity",
        desc: "Predict supplier disruption probability with named risk drivers. Get alternative suppliers ranked by qualification effort and capacity fit.",
      },
      {
        icon: ScrollText,
        title: "Regulatory reporting",
        desc: "Auto-populate continuity compliance reports from your live workspace evidence. Local validation runs before submission and blocks anything incomplete.",
      },
    ],
  },
];

function FeatureGroups() {
  return (
    <section className="py-24 bg-slate-50 border-y border-slate-100">
      <div className="max-w-6xl mx-auto px-6 space-y-24">
        {GROUPS.map((group) => (
          <div key={group.title}>
            <div className="max-w-2xl">
              <h2 className="text-3xl md:text-4xl font-bold text-slate-900">
                {group.title}
              </h2>
              <p className="mt-3 text-lg text-slate-600">{group.blurb}</p>
            </div>
            <div className="mt-10 grid grid-cols-1 md:grid-cols-2 gap-6">
              {group.items.map((item) => (
                <FeatureCard key={item.title} {...item} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function FeatureCard({
  icon: Icon,
  title,
  desc,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  desc: string;
}) {
  return (
    <div className="group relative rounded-xl border border-slate-200 bg-white p-6 shadow-sm hover:shadow-md hover:border-slate-300 transition-all">
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600 mb-4">
        <Icon className="h-5 w-5" />
      </div>
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 text-sm text-slate-600 leading-relaxed">{desc}</p>
    </div>
  );
}

function CopilotSection() {
  return (
    <section className="py-24 bg-white">
      <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
            <Sparkles className="h-3 w-3" />
            AI Copilot
          </div>
          <h2 className="mt-4 text-3xl md:text-4xl font-bold text-slate-900">
            Citations that come from your own plans.
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Every BCP, impact assessment, exercise evaluation, vendor score
            and IT DR plan you generate is indexed into a pgvector knowledge
            base. The Copilot retrieves the most relevant chunks before it
            answers — and cites them inline.
          </p>
          <ul className="mt-8 space-y-3">
            <CopilotBullet
              icon={Search}
              title="Retrieval-augmented"
              text="Cosine-similarity search over a vector index of every artifact you've created. No hallucinated citations."
            />
            <CopilotBullet
              icon={Zap}
              title="Floating, on every page"
              text="Open from anywhere — the chat carries workspace context with it and suggests next actions tied to the page you're on."
            />
            <CopilotBullet
              icon={GitBranch}
              title="OpenRouter primary, Ollama fallback"
              text="Cloud LLM for quality, local LLM for sovereignty. Embeddings cached in Redis so re-indexing is free."
            />
          </ul>
        </div>
        <div className="rounded-xl border border-slate-200 bg-gradient-to-br from-slate-50 to-white p-6 shadow-sm">
          <div className="flex items-center gap-2 text-xs text-slate-500 mb-4">
            <span className="h-2 w-2 rounded-full bg-blue-500" />
            Continuity Copilot · just now
          </div>
          <div className="space-y-4 text-sm">
            <div className="rounded-lg bg-blue-600 text-white px-4 py-3 ml-12">
              What recovery strategies do I have for Payments, and what's the
              financial impact during Black Friday?
            </div>
            <div className="rounded-lg bg-white border border-slate-200 px-4 py-3 mr-12">
              <p className="font-medium text-slate-900 mb-2">
                Recovery strategies for Payments (per evidence):
              </p>
              <ul className="text-slate-700 space-y-1">
                <li>
                  ⭐ <strong>Active-active multi-region</strong> — RTO 5m /
                  $240k/yr — recommended
                </li>
                <li>
                  • <strong>Warm standby</strong> — RTO 30m / $120k/yr
                </li>
                <li>
                  • <strong>Cold DR + manual</strong> — RTO 8h / $25k/yr
                </li>
              </ul>
              <p className="font-medium text-slate-900 mt-3">
                Financial impact (8h Black Friday outage):
              </p>
              <p className="text-slate-700">
                $2.4M revenue loss · operational 10/10 · reputation 9/10
              </p>
            </div>
            <div className="flex gap-2 mr-12 flex-wrap">
              <SuggestionChip>Run gap analysis</SuggestionChip>
              <SuggestionChip>Schedule an exercise</SuggestionChip>
              <SuggestionChip>Draft customer comms</SuggestionChip>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function CopilotBullet({
  icon: Icon,
  title,
  text,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  text: string;
}) {
  return (
    <li className="flex gap-3">
      <Icon className="h-5 w-5 text-blue-500 shrink-0 mt-0.5" />
      <div>
        <div className="font-semibold text-slate-900">{title}</div>
        <div className="text-sm text-slate-600">{text}</div>
      </div>
    </li>
  );
}

function SuggestionChip({ children }: { children: React.ReactNode }) {
  return (
    <span className="text-xs px-2 py-1 rounded-full bg-white border border-slate-200 text-slate-700">
      {children}
    </span>
  );
}

const STACK = [
  { label: "Next.js 14", desc: "App Router, Tailwind, shadcn" },
  { label: "FastAPI", desc: "Pydantic v2, SQLAlchemy 2.0, asyncpg" },
  { label: "PostgreSQL 16", desc: "with pgvector for RAG" },
  { label: "Redis 7", desc: "embedding + session cache" },
  { label: "MinIO / S3", desc: "BCP attachments + report exports" },
  { label: "Prometheus + Grafana", desc: "metrics + dashboards" },
  { label: "OpenRouter", desc: "Kimi K2 / Claude / GPT — your pick" },
  { label: "Ollama", desc: "local LLM fallback for sovereignty" },
];

function StackSection() {
  return (
    <section className="py-24 bg-slate-50 border-y border-slate-100">
      <div className="max-w-6xl mx-auto px-6">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600">
            <Database className="h-3 w-3" />
            Engineered for production
          </div>
          <h2 className="mt-4 text-3xl md:text-4xl font-bold text-slate-900">
            Open-source stack, ship-anywhere helm chart.
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            JWT auth with bcrypt-hashed passwords, structlog JSON logging,
            CloudNativePG-managed Postgres, optional TLS via cert-manager.
            One <code className="text-sm bg-slate-200 px-1.5 py-0.5 rounded">helm install</code>{" "}
            puts every piece in your cluster.
          </p>
        </div>
        <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-4">
          {STACK.map((s) => (
            <div
              key={s.label}
              className="rounded-lg border border-slate-200 bg-white p-4"
            >
              <div className="font-semibold text-slate-900">{s.label}</div>
              <div className="text-xs text-slate-500 mt-1">{s.desc}</div>
            </div>
          ))}
        </div>
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <Tile
            icon={Lock}
            title="Secure by default"
            text="bcrypt passwords. JWT-signed sessions. Pre-flight warnings if you forget to rotate the dev SECRET_KEY."
          />
          <Tile
            icon={CheckCircle2}
            title="48 passing tests"
            text="Every feature has end-to-end tests. Lint enforced. CI on every PR."
          />
          <Tile
            icon={Gauge}
            title="Observable"
            text="Prometheus /metrics, Grafana dashboards, structlog JSON. Failures are loud."
          />
        </div>
      </div>
    </section>
  );
}

function Tile({
  icon: Icon,
  title,
  text,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6">
      <Icon className="h-6 w-6 text-blue-500" />
      <h3 className="mt-3 font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 text-sm text-slate-600">{text}</p>
    </div>
  );
}

function CTASection() {
  return (
    <section className="py-24 bg-slate-900 text-white">
      <div className="max-w-4xl mx-auto px-6 text-center">
        <h2 className="text-4xl md:text-5xl font-bold tracking-tight">
          Ready to draft your first BCP?
        </h2>
        <p className="mt-4 text-lg text-slate-300">
          Sign up, register a critical function, and let the Copilot draft a
          ready-to-review plan in under twenty minutes.
        </p>
        <div className="mt-10 flex flex-col sm:flex-row justify-center gap-3">
          <Link
            href="/signup"
            className="inline-flex items-center justify-center gap-2 rounded-md bg-white px-6 py-3 text-sm font-medium text-slate-900 hover:bg-slate-100 transition-colors"
          >
            Create an account <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            href="https://github.com/dclawstack/dclaw-continuity"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center justify-center rounded-md border border-slate-700 bg-slate-800 px-6 py-3 text-sm font-medium text-white hover:bg-slate-700 transition-colors"
          >
            View on GitHub
          </Link>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400 border-t border-slate-800">
      <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <div
            className="h-5 w-5 rounded"
            style={{ backgroundColor: "#3B82F6" }}
          />
          <span className="text-sm">DClaw Continuity</span>
        </div>
        <div className="text-xs">
          Part of the{" "}
          <a
            href="https://github.com/dclawstack"
            className="text-slate-300 hover:text-white"
          >
            DClaw Stack
          </a>
          .
        </div>
      </div>
    </footer>
  );
}
