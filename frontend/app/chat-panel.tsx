"use client";

import { useState } from "react";

type ChatResponse = {
  answer: string;
  sources: string[];
  grounded: boolean;
  retries: number;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ChatPanel() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ChatResponse | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim() || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (!res.ok) throw new Error(`Erreur serveur (${res.status})`);
      const data: ChatResponse = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex w-full max-w-2xl flex-col gap-4">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Pose une question, ex : What is corrective RAG?"
          rows={3}
          className="w-full rounded-lg border border-zinc-300 bg-white p-3 text-base dark:border-zinc-700 dark:bg-zinc-900"
        />
        <button
          type="submit"
          disabled={loading}
          className="w-fit rounded-full bg-blue-600 px-6 py-2 font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Recherche en cours..." : "Demander"}
        </button>
      </form>

      {loading && (
        <p className="text-sm italic text-zinc-500">
          Recherche, évaluation, génération... (30s à 1min)
        </p>
      )}

      {error && <p className="text-sm text-red-500">❌ {error}</p>}

      {result && (
        <div className="flex flex-col gap-3 rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
          <p className="whitespace-pre-wrap leading-relaxed">{result.answer}</p>
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-zinc-500">
            <span>Fondée sur le contexte : {result.grounded ? "✅" : "⚠️"}</span>
            <span>Retries : {result.retries}</span>
          </div>
          {result.sources.length > 0 && (
            <div className="text-xs text-zinc-500">
              Sources :{" "}
              {result.sources.map((s, i) => (
                <span key={s}>
                  {i > 0 && ", "}
                  {s.startsWith("http") ? (
                    <a
                      href={s}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline dark:text-blue-400"
                    >
                      {s}
                    </a>
                  ) : (
                    s
                  )}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
