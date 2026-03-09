
import { Github } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";

interface Repository {
  id: string;
  name: string;
  description?: string;
  url?: string;
  stars: number;
  language?: string;
  updated: string;
  owner: { name: string };
  license?: string;
  forks: number;
  issues: number;
}

export default async function RepositoryDetailPage({ params }: { params: { id: string } }) {
  // Fetch repository from API (SSR-safe absolute URL)
  let baseUrl = "";
  if (typeof window === "undefined") {
    // On server, use headers to get absolute URL (headers() is async)
    const { headers } = await import("next/headers");
    const h = await headers();
    const host = h.get("host");
    const protocol = process.env.NODE_ENV === "production" ? "https" : "http";
    baseUrl = `${protocol}://${host}`;
  }
  const res = await fetch(`${baseUrl}/api/repository/${params.id}`, { cache: "no-store" });
  if (!res.ok) return notFound();
  const repo: Repository = await res.json();

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/10 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/20 rounded-full blur-3xl opacity-20" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-accent/20 rounded-full blur-3xl opacity-20" />
      </div>
      <header className="relative z-10 border-b border-foreground/10 backdrop-blur-xl bg-background/40">
        <div className="max-w-3xl mx-auto px-4 py-6 flex items-center justify-between">
          <Link href="/repository" className="flex items-center gap-2 text-foreground/60 hover:text-foreground transition-colors">
            <span className="text-lg">←</span>
            <span>Back to Repositories</span>
          </Link>
        </div>
      </header>
      <main className="relative z-10 max-w-3xl mx-auto px-4 py-12">
        <div className="backdrop-blur-xl bg-card/40 border border-card-foreground/10 rounded-2xl p-10">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-14 h-14 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center opacity-60">
              <Github className="w-8 h-8 text-foreground" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-foreground mb-1">{repo.name}</h2>
              {repo.url && (
                <a href={repo.url} target="_blank" rel="noopener noreferrer" className="text-primary underline text-sm">View on GitHub</a>
              )}
            </div>
            <Link
              href={`/repository/${repo.id}/chat`}
              className="ml-auto flex items-center gap-2 px-4 py-2 rounded-lg bg-accent text-foreground hover:bg-accent/90 transition-colors font-medium"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.77 9.77 0 0 1-4-.8L3 20l.8-4A8.96 8.96 0 0 1 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8Z" /></svg>
              Go to Chat
            </Link>
          </div>
          <p className="text-foreground/70 mb-6">{repo.description}</p>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-background/80 rounded-lg p-4 border border-card-foreground/10">
              <div className="text-xs text-foreground/40 mb-1">Owner</div>
              <div className="text-foreground font-semibold">{repo.owner?.name || "-"}</div>
            </div>
            <div className="bg-background/80 rounded-lg p-4 border border-card-foreground/10">
              <div className="text-xs text-foreground/40 mb-1">License</div>
              <div className="text-foreground font-semibold">{repo.license || "-"}</div>
            </div>
            <div className="bg-background/80 rounded-lg p-4 border border-card-foreground/10">
              <div className="text-xs text-foreground/40 mb-1">Language</div>
              <div className="text-foreground font-semibold">{repo.language || "-"}</div>
            </div>
            <div className="bg-background/80 rounded-lg p-4 border border-card-foreground/10">
              <div className="text-xs text-foreground/40 mb-1">Last Updated</div>
              <div className="text-foreground font-semibold">{repo.updated?.toString().slice(0, 10) || "-"}</div>
            </div>
            <div className="bg-background/80 rounded-lg p-4 border border-card-foreground/10">
              <div className="text-xs text-foreground/40 mb-1">Stars</div>
              <div className="text-foreground font-semibold">⭐ {repo.stars}</div>
            </div>
            <div className="bg-background/80 rounded-lg p-4 border border-card-foreground/10">
              <div className="text-xs text-foreground/40 mb-1">Forks</div>
              <div className="text-foreground font-semibold">{repo.forks}</div>
            </div>
            <div className="bg-background/80 rounded-lg p-4 border border-card-foreground/10">
              <div className="text-xs text-foreground/40 mb-1">Open Issues</div>
              <div className="text-foreground font-semibold">{repo.issues}</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}