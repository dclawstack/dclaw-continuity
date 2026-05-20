"use client";

import { useEffect, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  Check,
  Copy,
  ExternalLink,
  PlayCircle,
  RotateCcw,
  Sparkles,
} from "lucide-react";

import { api } from "@/lib/api";
import { setStoredSession } from "@/lib/auth";

const STORAGE_KEY = "dclaw_demo_session";

interface DemoSession {
  user_id: string;
  email: string;
  password: string;
}

export function DemoSection() {
  const [session, setSession] = useState<DemoSession | null>(null);
  const [hydrated, setHydrated] = useState(false);
  const [loading, setLoading] = useState<"seed" | "clear" | null>(null);
  const [err, setErr] = useState<string | null>(null);

  // Read any existing demo session on mount.
  useEffect(() => {
    setHydrated(true);
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try {
        setSession(JSON.parse(raw) as DemoSession);
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
  }, []);

  async function seed() {
    setLoading("seed");
    setErr(null);
    try {
      const result = await api.demo.seed();
      const s: DemoSession = {
        user_id: result.user_id,
        email: result.email,
        password: result.password,
      };
      // Stash credentials for "Clear demo" + a re-seed prompt on revisit.
      localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
      // Also persist the auth token so a new tab opened on /dashboard
      // is already signed in.
      setStoredSession(result.access_token, {
        id: result.user_id,
        email: result.email,
        is_superuser: false,
      });
      setSession(s);
    } catch (e) {
      setErr(
        e instanceof Error
          ? `Couldn't reach the API: ${e.message}. The landing site needs the backend running at NEXT_PUBLIC_API_URL.`
          : "Demo seed failed",
      );
    } finally {
      setLoading(null);
    }
  }

  async function clear() {
    if (!session) return;
    setLoading("clear");
    setErr(null);
    try {
      await api.demo.clear(session.user_id);
    } catch {
      // Clear is idempotent server-side; tolerate transient errors.
    }
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem("dclaw_token");
    localStorage.removeItem("dclaw_user");
    setSession(null);
    setLoading(null);
  }

  return (
    <section
      id="demo"
      className="py-24 bg-white border-t border-slate-100 scroll-mt-8"
    >
      <div className="max-w-6xl mx-auto px-6">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
            <PlayCircle className="h-3 w-3" />
            Try the live app
          </div>
          <h2 className="mt-4 text-3xl md:text-4xl font-bold text-slate-900">
            Spin up a real demo workspace.
          </h2>
          <p className="mt-4 text-lg text-slate-600">
            Click below and we'll create a throwaway account with a
            pre-populated BCP, impact analysis, recovery strategies, and a
            scored exercise. Open the app in a new tab and click around.
            When you're done, clear the data and the account disappears.
          </p>
        </div>

        <div className="mt-10">
          {!hydrated ? (
            <Skeleton />
          ) : session ? (
            <ActiveCard session={session} loading={loading} onClear={clear} />
          ) : (
            <SeedCard loading={loading === "seed"} onSeed={seed} err={err} />
          )}
        </div>
      </div>
    </section>
  );
}

function Skeleton() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 h-48 animate-pulse" />
  );
}

function SeedCard({
  loading,
  onSeed,
  err,
}: {
  loading: boolean;
  onSeed: () => void;
  err: string | null;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-slate-50 to-white p-8 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <Sparkles className="h-4 w-4 text-blue-500" />
            <span className="font-medium text-slate-900">
              No demo workspace yet
            </span>
          </div>
          <p className="mt-2 text-sm text-slate-600 max-w-xl">
            We'll create a fresh user and seed it with a critical Payments
            function, an AI-style BCP, a $2.4M Black Friday impact
            scenario, three recovery strategies (one starred), a scored
            ransomware drill, and a Stripe vendor assessment.
          </p>
        </div>
        <button
          onClick={onSeed}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-md bg-blue-600 text-white px-5 py-2.5 text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors whitespace-nowrap"
        >
          {loading ? (
            <>Seeding…</>
          ) : (
            <>
              <Sparkles className="h-4 w-4" /> Seed demo data
            </>
          )}
        </button>
      </div>
      {err && (
        <div className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700 flex items-start gap-2">
          <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
          <span>{err}</span>
        </div>
      )}
    </div>
  );
}

function ActiveCard({
  session,
  loading,
  onClear,
}: {
  session: DemoSession;
  loading: "seed" | "clear" | null;
  onClear: () => void;
}) {
  return (
    <div className="rounded-2xl border border-blue-200 bg-gradient-to-br from-blue-50 to-white p-8 shadow-sm">
      <div className="flex items-center gap-2 text-sm">
        <span className="inline-flex h-2 w-2 rounded-full bg-green-500" />
        <span className="font-medium text-slate-900">Demo workspace ready</span>
        <span className="text-slate-500">
          · auto-deletes when you click Clear
        </span>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-3">
        <CredField label="Email" value={session.email} />
        <CredField label="Password" value={session.password} mask />
      </div>

      <p className="mt-4 text-sm text-slate-600">
        Opening the app in a new tab signs you in automatically — the
        credentials above are just for your records. Come back to this tab
        to clear everything.
      </p>

      <div className="mt-6 flex flex-col sm:flex-row gap-3">
        <a
          href="/dashboard"
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center justify-center gap-2 rounded-md bg-slate-900 text-white px-5 py-2.5 text-sm font-medium hover:bg-slate-800 transition-colors"
        >
          Open the app
          <ExternalLink className="h-4 w-4" />
        </a>
        <button
          onClick={onClear}
          disabled={loading === "clear"}
          className="inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white text-slate-700 px-5 py-2.5 text-sm font-medium hover:bg-slate-50 disabled:opacity-50 transition-colors"
        >
          {loading === "clear" ? (
            <>Clearing…</>
          ) : (
            <>
              <RotateCcw className="h-4 w-4" />
              Clear demo data
            </>
          )}
        </button>
      </div>
    </div>
  );
}

function CredField({
  label,
  value,
  mask = false,
}: {
  label: string;
  value: string;
  mask?: boolean;
}) {
  const [revealed, setRevealed] = useState(!mask);
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* ignore — older browsers without clipboard */
    }
  }

  const display = revealed ? value : "•".repeat(Math.min(value.length, 18));

  return (
    <div className="rounded-md border border-slate-200 bg-white p-3">
      <div className="flex items-center justify-between">
        <span className="text-[10px] uppercase tracking-wider text-slate-500">
          {label}
        </span>
        <div className="flex items-center gap-1">
          {mask && (
            <button
              type="button"
              onClick={() => setRevealed((r) => !r)}
              className="text-xs text-slate-500 hover:text-slate-900 px-1.5"
            >
              {revealed ? "hide" : "show"}
            </button>
          )}
          <button
            type="button"
            onClick={copy}
            className="text-slate-500 hover:text-slate-900 p-1"
            aria-label={`Copy ${label}`}
          >
            {copied ? (
              <Check className="h-3.5 w-3.5 text-green-600" />
            ) : (
              <Copy className="h-3.5 w-3.5" />
            )}
          </button>
        </div>
      </div>
      <div className="mt-1 font-mono text-sm text-slate-900 truncate">
        {display}
      </div>
    </div>
  );
}

// Hint chip used elsewhere on the page if needed.
export function DemoHintChip() {
  return (
    <a
      href="#demo"
      className="inline-flex items-center gap-1 text-sm text-slate-600 hover:text-slate-900"
    >
      Or try the demo first <ArrowRight className="h-3.5 w-3.5" />
    </a>
  );
}
