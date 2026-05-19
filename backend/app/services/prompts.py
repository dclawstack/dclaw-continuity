"""Prompt templates for the AI Continuity Copilot and feature services."""

from __future__ import annotations

COPILOT_SYSTEM_PROMPT = """You are the DClaw Continuity Copilot, an AI assistant
specialized in business continuity planning (BCP), business impact analysis (BIA),
and disaster recovery. You help users plan, test, and maintain continuity for
critical business functions.

Be concise, action-oriented, and concrete. When useful, suggest specific
next-actions the user could take in the app (e.g., "create a BCP", "model an
impact scenario", "generate a recovery strategy"). Prefer industry-standard
terminology (RTO, RPO, BIA, MTPD, MAO, MBCO)."""


BCP_GENERATION_PROMPT = """You are generating a Business Continuity Plan for the
following critical business function. Respond ONLY with valid JSON matching this
schema:

{{
  "title": string,
  "summary": string,
  "objectives": [string],
  "activation_triggers": [string],
  "roles": [{{"role": string, "responsibilities": string}}],
  "procedures": [{{"step": number, "action": string, "owner": string, "duration_minutes": number}}],
  "communication_plan": {{"internal": string, "external": string}},
  "recovery_targets": {{"rto_minutes": number, "rpo_minutes": number}},
  "dependencies_to_watch": [string]
}}

Business function:
- Name: {name}
- Description: {description}
- Owner: {owner}
- Criticality: {criticality}
- Current RTO target (minutes): {rto_minutes}
- Current RPO target (minutes): {rpo_minutes}
- Known dependencies: {dependencies}

Additional context from user:
{additional_context}
"""


BCP_GAP_ANALYSIS_PROMPT = """You are auditing a Business Continuity Plan for
gaps. Respond ONLY with valid JSON:

{{
  "gaps": [
    {{
      "severity": "low" | "medium" | "high" | "critical",
      "area": string,
      "issue": string,
      "recommendation": string
    }}
  ]
}}

BCP to audit:
{bcp_json}

Function context:
- Criticality: {criticality}
- RTO target: {rto_minutes}m
- RPO target: {rpo_minutes}m
"""


IMPACT_MODELING_PROMPT = """You are modeling the business impact of a disruption
scenario on a critical function. Respond ONLY with valid JSON:

{{
  "revenue_impact_usd": number,
  "operational_impact_score": number (0-10),
  "reputation_impact_score": number (0-10),
  "narrative": string,
  "timeline": {{
    "first_hour": string,
    "first_day": string,
    "first_week": string
  }},
  "stakeholders": [{{"name": string, "impact": string}}]
}}

Function:
- Name: {name}
- Description: {description}
- Criticality: {criticality}

Scenario:
{scenario}

Additional context:
{additional_context}
"""


WORK_AREA_PLAN_PROMPT = """You are planning alternate work locations for a
disrupted business function. Respond ONLY with valid JSON:

{{
  "summary": string (1-2 sentences),
  "assignments": [
    {{
      "site_id": string,
      "site_name": string,
      "seats": number,
      "rationale": string
    }}
  ],
  "shortfall_seats": number (0 if fully covered),
  "test_plan": string (how to validate remote access / readiness)
}}

Function: {function_name} (criticality: {criticality})
Required headcount: {headcount}
Available sites: {sites}
Additional context: {additional_context}
"""


IT_DR_PLAN_PROMPT = """You are generating an IT disaster recovery plan for the
following system. Respond ONLY with valid JSON:

{{
  "title": string,
  "summary": string,
  "prerequisites": [string],
  "procedure": [{{"step": number, "action": string, "owner": string, "duration_minutes": number}}],
  "validation": [string],
  "failback": [string],
  "test_plan": [
    {{
      "name": string,
      "schedule": string (cron-friendly description),
      "validates": string,
      "automation_hint": string
    }}
  ]
}}

System:
- Name: {name}
- Description: {description}
- Owner: {owner}
- Tier: {tier}
- RTO target: {rto_minutes}m
- RPO target: {rpo_minutes}m
- Current backup strategy: {backup_strategy}

Additional context:
{additional_context}
"""


SUPPLY_CHAIN_PROMPT = """You are predicting supply-chain disruption risk for a
critical supplier. Respond ONLY with valid JSON:

{{
  "disruption_probability": number (0-100),
  "risk_drivers": [string],
  "suggested_alternatives": [{{"name": string, "rationale": string}}],
  "summary": string,
  "monitoring_indicators": [string]
}}

Supplier:
- Name: {name}
- Category: {category}
- Region: {region}
- Criticality: {criticality}
- Description: {description}
- Known alternatives: {known_alternatives}

Additional context:
{additional_context}
"""


REGULATORY_REPORT_PROMPT = """You are drafting a business-continuity compliance
report for a regulator. Auto-populate from the evidence snapshot. Respond ONLY
with valid JSON that has these top-level keys at minimum:

{{
  "title": string,
  "executive_summary": string,
  "metrics": {{ "bcps_in_force": number, "exercises_completed": number, "vendor_coverage_pct": number, "avg_exercise_score": number }},
  "sections": [
    {{ "title": string, "body": string }}
  ],
  "attestation": string
}}

Framework: {framework}
Reporting period: {period}
Evidence snapshot: {snapshot}
Additional context: {additional_context}
"""


VENDOR_CONTINUITY_PROMPT = """You are assessing a vendor's business continuity
readiness. Respond ONLY with valid JSON:

{{
  "readiness_score": number (0-100),
  "risk_level": "low" | "medium" | "high" | "critical",
  "summary": string,
  "strengths": [string],
  "weaknesses": [string],
  "monitoring_indicators": [string] (specific signals to watch over time)
}}

Vendor:
- Name: {name}
- Description: {description}
- Services provided: {services}
- Tier: {tier}

Additional context:
{additional_context}
"""


COMMUNICATION_PLAN_PROMPT = """You are drafting a stakeholder communication plan
for a continuity scenario. Respond ONLY with valid JSON:

{{
  "audience": string,
  "channels": [string] (e.g. email, SMS, status page, intranet, press),
  "tone": string (e.g. formal, reassuring, urgent),
  "templates": [
    {{
      "channel": string,
      "trigger": string (when to send),
      "subject": string,
      "body": string
    }}
  ],
  "escalation_path": [string]
}}

Function: {function_name} ({criticality})
Scenario: {scenario}
Audience: {audience}
Additional context: {additional_context}
"""


EXERCISE_SCENARIO_PROMPT = """You are designing a realistic continuity exercise
for the following BCP. Respond ONLY with valid JSON:

{{
  "name": string,
  "scenario": string (a vivid 2-paragraph injection — what happens, when, who notices),
  "objectives": [string] (3-5 measurable outcomes)
}}

Context:
- Function: {function_name} (criticality: {criticality})
- BCP: {bcp_title}
- BCP summary: {bcp_summary}
- Exercise focus: {focus}
"""


EXERCISE_EVALUATION_PROMPT = """You are evaluating how a team performed during a
continuity exercise. Respond ONLY with valid JSON:

{{
  "score": number (0-100 — overall readiness),
  "strengths": [string],
  "weaknesses": [string],
  "missed_objectives": [string],
  "recommendations": [string]
}}

Exercise: {exercise_name}
Scenario: {scenario}
Objectives: {objectives}
Observations from operator: {observations}
Issues encountered: {issues}
Referenced BCP summary: {bcp_summary}
"""


RECOVERY_RECOMMENDATION_PROMPT = """You are recommending recovery strategies for
a business function. Recommend 3 distinct strategies that span cost/recovery-time
trade-offs. Respond ONLY with valid JSON:

{{
  "strategies": [
    {{
      "title": string,
      "kind": "hot_site" | "warm_site" | "cold_site" | "remote_work" | "third_party" | "manual_workaround" | "redundancy" | "other",
      "description": string,
      "estimated_cost_usd": number,
      "rto_minutes": number,
      "rpo_minutes": number,
      "is_recommended": boolean,
      "rationale": string
    }}
  ]
}}

Exactly one strategy must have is_recommended=true (the best balance for the
constraints).

Function:
- Name: {name}
- Description: {description}
- Criticality: {criticality}
- Current RTO target: {rto_minutes}m
- Current RPO target: {rpo_minutes}m
- Budget cap (USD, 0 = unconstrained): {budget_usd}

Additional context:
{additional_context}
"""
