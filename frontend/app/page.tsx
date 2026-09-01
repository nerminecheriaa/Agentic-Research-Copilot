import ChatPanel from "./chat-panel";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center bg-zinc-50 px-6 py-16 dark:bg-black">
      <main className="flex w-full max-w-2xl flex-col items-center gap-6">
        <div className="flex flex-col items-center gap-1 text-center">
          <h1 className="text-2xl font-semibold text-black dark:text-zinc-50">
            🔎 Agentic Research Copilot
          </h1>
          <p className="text-sm text-zinc-500">
            Corrective RAG sur un corpus de papers arXiv (retrieval-augmented generation)
          </p>
        </div>
        <ChatPanel />
      </main>
    </div>
  );
}
