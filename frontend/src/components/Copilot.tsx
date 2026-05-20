"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { MessageSquare, Send, Sparkles, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { api, type CopilotSuggestion } from "@/lib/api";
import { useAuth } from "@/lib/auth";

interface Message {
  role: "user" | "assistant";
  content: string;
  suggestions?: CopilotSuggestion[];
}

const GREETING: Message = {
  role: "assistant",
  content:
    "Hi! I'm your Continuity Copilot. Ask me about business continuity, " +
    "or tell me about a function and I'll help you draft a BCP, model impact, " +
    "or recommend recovery strategies.",
  suggestions: [
    { action: "create_function", label: "Add a business function", payload: {} },
    { action: "generate_bcp", label: "Draft a BCP", payload: {} },
    { action: "model_impact", label: "Model a scenario", payload: {} },
  ],
};

const SUGGESTION_ROUTES: Record<string, string> = {
  create_function: "/functions",
  generate_bcp: "/bcps",
  gap_analysis: "/bcps",
  model_impact: "/impact",
  recommend_recovery: "/recovery",
};

export function Copilot() {
  const router = useRouter();
  const pathname = usePathname() || "/";
  const { token } = useAuth();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([GREETING]);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, open]);

  async function send() {
    const text = input.trim();
    if (!text || sending) return;

    setInput("");
    setMessages((m) => [...m, { role: "user", content: text }]);
    setSending(true);

    try {
      const res = await api.copilot.chat(text, conversationId);
      setConversationId(res.conversation_id);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: res.reply,
          suggestions: res.suggestions,
        },
      ]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            e instanceof Error
              ? `Sorry, the Copilot is unavailable: ${e.message}`
              : "Sorry, the Copilot is unavailable.",
        },
      ]);
    } finally {
      setSending(false);
    }
  }

  function applySuggestion(s: CopilotSuggestion) {
    const route = SUGGESTION_ROUTES[s.action];
    if (route) {
      router.push(route);
      setOpen(false);
    }
  }

  // Don't render the Copilot on the auth pages or when not signed in.
  if (!token || pathname === "/login" || pathname === "/signup") {
    return null;
  }

  return (
    <>
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 flex items-center justify-center"
        aria-label="Open Copilot"
      >
        {open ? <X className="h-6 w-6" /> : <Sparkles className="h-6 w-6" />}
      </button>

      <div
        className={cn(
          "fixed bottom-24 right-6 w-[380px] max-h-[70vh] flex flex-col rounded-xl bg-white shadow-2xl border transition-all",
          open ? "opacity-100" : "opacity-0 pointer-events-none translate-y-2",
        )}
      >
        <div className="px-4 py-3 border-b flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-blue-500" />
          <span className="font-semibold text-sm">Continuity Copilot</span>
        </div>

        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-4 space-y-3 text-sm"
        >
          {messages.map((m, i) => (
            <div
              key={i}
              className={cn(
                "rounded-lg p-3 max-w-[85%]",
                m.role === "user"
                  ? "ml-auto bg-blue-600 text-white"
                  : "bg-slate-100",
              )}
            >
              <div className="whitespace-pre-wrap">{m.content}</div>
              {m.suggestions && m.suggestions.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {m.suggestions.map((s, j) => (
                    <button
                      key={j}
                      onClick={() => applySuggestion(s)}
                      className="text-xs px-2 py-1 rounded-full bg-white border border-slate-200 hover:bg-blue-50"
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
          {sending && (
            <div className="bg-slate-100 rounded-lg p-3 max-w-[85%]">
              <span className="inline-flex items-center gap-1 text-slate-500">
                <span className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-pulse" />
                <span
                  className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-pulse"
                  style={{ animationDelay: "0.2s" }}
                />
                <span
                  className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-pulse"
                  style={{ animationDelay: "0.4s" }}
                />
              </span>
            </div>
          )}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            send();
          }}
          className="p-3 border-t flex gap-2"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about continuity planning…"
            className="flex-1 h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
          />
          <Button type="submit" size="sm" disabled={sending}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </>
  );
}
