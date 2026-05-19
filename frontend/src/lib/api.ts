const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";
const DEV_TOKEN = process.env.NEXT_PUBLIC_DEV_AUTH_TOKEN || "dev-token";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${DEV_TOKEN}`,
      ...(init.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new ApiError(`API ${res.status}: ${body}`, res.status);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export type Criticality = "low" | "medium" | "high" | "critical";

export interface BusinessFunction {
  id: string;
  name: string;
  description: string;
  owner: string;
  criticality: Criticality;
  rto_minutes: number;
  rpo_minutes: number;
  created_at: string;
  updated_at: string;
}

export interface BCP {
  id: string;
  function_id: string;
  title: string;
  summary: string;
  status: "draft" | "review" | "approved" | "retired";
  content: Record<string, unknown>;
  gaps: Array<Record<string, unknown>>;
  created_at: string;
  updated_at: string;
}

export interface ImpactAssessment {
  id: string;
  function_id: string;
  scenario: string;
  description: string;
  revenue_impact_usd: number;
  operational_impact_score: number;
  reputation_impact_score: number;
  details: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export type StrategyKind =
  | "hot_site"
  | "warm_site"
  | "cold_site"
  | "remote_work"
  | "third_party"
  | "manual_workaround"
  | "redundancy"
  | "other";

export interface RecoveryStrategy {
  id: string;
  function_id: string;
  title: string;
  kind: StrategyKind;
  description: string;
  estimated_cost_usd: number;
  rto_minutes: number;
  rpo_minutes: number;
  is_recommended: boolean;
  details: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CopilotSuggestion {
  action: string;
  label: string;
  payload: Record<string, unknown>;
}

export interface CopilotChatResponse {
  conversation_id: string;
  reply: string;
  suggestions: CopilotSuggestion[];
}

export type ExerciseStatus = "planned" | "running" | "completed" | "cancelled";

export interface Exercise {
  id: string;
  bcp_id: string;
  name: string;
  scenario: string;
  objectives: string[];
  status: ExerciseStatus;
  score: number;
  evaluation: Record<string, unknown>;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export type ActivationStatus =
  | "activated"
  | "recovering"
  | "stabilized"
  | "closed";

export interface CrisisActivation {
  id: string;
  bcp_id: string;
  external_crisis_id: string | null;
  source: string;
  title: string;
  description: string;
  status: ActivationStatus;
  activated_at: string;
  closed_at: string | null;
  timeline: Array<{ at: string; status: string; note: string }>;
  created_at: string;
  updated_at: string;
}

export interface Vendor {
  id: string;
  name: string;
  description: string;
  contact: string;
  services_provided: string;
  tier: string;
  readiness_score: number;
  created_at: string;
  updated_at: string;
}

export interface VendorAssessment {
  id: string;
  vendor_id: string;
  readiness_score: number;
  risk_level: string;
  summary: string;
  details: Record<string, unknown>;
  created_at: string;
}

export interface CommunicationTemplate {
  id: string;
  plan_id: string;
  channel: string;
  trigger: string;
  subject: string;
  body: string;
  created_at: string;
}

export interface CommunicationPlan {
  id: string;
  function_id: string;
  audience: string;
  scenario: string;
  tone: string;
  channels: string[];
  escalation_path: string[];
  notes: string;
  templates: CommunicationTemplate[];
  created_at: string;
  updated_at: string;
}


export const api = {
  health: () => request<{ status: string }>("/health/"),

  functions: {
    list: () => request<BusinessFunction[]>("/api/v1/functions/"),
    get: (id: string) => request<BusinessFunction>(`/api/v1/functions/${id}`),
    create: (body: Partial<BusinessFunction>) =>
      request<BusinessFunction>("/api/v1/functions/", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    update: (id: string, body: Partial<BusinessFunction>) =>
      request<BusinessFunction>(`/api/v1/functions/${id}`, {
        method: "PATCH",
        body: JSON.stringify(body),
      }),
    delete: (id: string) =>
      request<void>(`/api/v1/functions/${id}`, { method: "DELETE" }),
  },

  bcps: {
    list: (functionId?: string) =>
      request<BCP[]>(
        functionId ? `/api/v1/bcps/?function_id=${functionId}` : "/api/v1/bcps/",
      ),
    get: (id: string) => request<BCP>(`/api/v1/bcps/${id}`),
    create: (body: Partial<BCP> & { function_id: string; title: string }) =>
      request<BCP>("/api/v1/bcps/", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    generate: (functionId: string, additionalContext = "") =>
      request<BCP>("/api/v1/bcps/generate", {
        method: "POST",
        body: JSON.stringify({
          function_id: functionId,
          additional_context: additionalContext,
        }),
      }),
    gapAnalysis: (bcpId: string) =>
      request<BCP>(`/api/v1/bcps/${bcpId}/gap-analysis`, { method: "POST" }),
  },

  impact: {
    list: (functionId?: string) =>
      request<ImpactAssessment[]>(
        functionId
          ? `/api/v1/impact/?function_id=${functionId}`
          : "/api/v1/impact/",
      ),
    model: (functionId: string, scenario: string, additionalContext = "") =>
      request<ImpactAssessment>("/api/v1/impact/model", {
        method: "POST",
        body: JSON.stringify({
          function_id: functionId,
          scenario,
          additional_context: additionalContext,
        }),
      }),
  },

  recovery: {
    list: (functionId?: string) =>
      request<RecoveryStrategy[]>(
        functionId
          ? `/api/v1/recovery/?function_id=${functionId}`
          : "/api/v1/recovery/",
      ),
    recommend: (functionId: string, budgetUsd?: number, ctx = "") =>
      request<RecoveryStrategy[]>("/api/v1/recovery/recommend", {
        method: "POST",
        body: JSON.stringify({
          function_id: functionId,
          budget_usd: budgetUsd ?? null,
          additional_context: ctx,
        }),
      }),
  },

  copilot: {
    chat: (message: string, conversationId?: string) =>
      request<CopilotChatResponse>("/api/v1/copilot/chat", {
        method: "POST",
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
        }),
      }),
  },

  exercises: {
    list: (bcpId?: string) =>
      request<Exercise[]>(
        bcpId
          ? `/api/v1/exercises/?bcp_id=${bcpId}`
          : "/api/v1/exercises/",
      ),
    generate: (bcpId: string, focus = "") =>
      request<Exercise>("/api/v1/exercises/generate", {
        method: "POST",
        body: JSON.stringify({ bcp_id: bcpId, focus }),
      }),
    start: (id: string) =>
      request<Exercise>(`/api/v1/exercises/${id}/start`, { method: "POST" }),
    evaluate: (
      id: string,
      observations: string,
      issues_encountered: string[] = [],
    ) =>
      request<Exercise>(`/api/v1/exercises/${id}/evaluate`, {
        method: "POST",
        body: JSON.stringify({ observations, issues_encountered }),
      }),
  },

  crisis: {
    list: (onlyOpen = false) =>
      request<CrisisActivation[]>(
        `/api/v1/crisis/?only_open=${onlyOpen ? "true" : "false"}`,
      ),
    activate: (body: {
      bcp_id?: string;
      function_id?: string;
      external_crisis_id?: string;
      source?: string;
      title: string;
      description?: string;
    }) =>
      request<CrisisActivation>("/api/v1/crisis/activate", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    updateStatus: (id: string, status: ActivationStatus, note = "") =>
      request<CrisisActivation>(`/api/v1/crisis/${id}/status`, {
        method: "POST",
        body: JSON.stringify({ status, note }),
      }),
  },

  vendors: {
    list: () => request<Vendor[]>("/api/v1/vendors/"),
    create: (body: Partial<Vendor> & { name: string }) =>
      request<Vendor>("/api/v1/vendors/", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    assessments: (vendorId: string) =>
      request<VendorAssessment[]>(`/api/v1/vendors/${vendorId}/assessments`),
    assess: (vendorId: string, additionalContext = "") =>
      request<VendorAssessment>("/api/v1/vendors/assess", {
        method: "POST",
        body: JSON.stringify({
          vendor_id: vendorId,
          additional_context: additionalContext,
        }),
      }),
  },

  communications: {
    list: (functionId?: string) =>
      request<CommunicationPlan[]>(
        functionId
          ? `/api/v1/communications/?function_id=${functionId}`
          : "/api/v1/communications/",
      ),
    draft: (
      functionId: string,
      audience: string,
      scenario: string,
      additionalContext = "",
    ) =>
      request<CommunicationPlan>("/api/v1/communications/draft", {
        method: "POST",
        body: JSON.stringify({
          function_id: functionId,
          audience,
          scenario,
          additional_context: additionalContext,
        }),
      }),
  },
};
