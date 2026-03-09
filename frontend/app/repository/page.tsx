import { auth, signOut } from "@/lib/auth.config";
import { redirect } from "next/navigation";
import { ArrowLeft, Github, LogOut } from "lucide-react";
import Link from "next/link";

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

export default async function RepositoryPage() {
  const session = await auth();

  if (!session) {
    redirect("/auth/login");
  }

  async function handleSignOut() {
    "use server";
    await signOut();
    redirect("/auth/login");
  }

  // Fetch repositories from API (SSR-safe absolute URL)
  let baseUrl = "";
  if (typeof window === "undefined") {
    // On server, use headers to get absolute URL (headers() is async)
    const { headers } = await import("next/headers");
    const h = await headers();
    const host = h.get("host");
    const protocol = process.env.NODE_ENV === "production" ? "https" : "http";
    baseUrl = `${protocol}://${host}`;
  }
  const res = await fetch(`${baseUrl}/api/repository`, { cache: "no-store" });
  const repositories: Repository[] = res.ok ? await res.json() : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/10 relative overflow-hidden">
      {/* Decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/20 rounded-full blur-3xl opacity-20" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-accent/20 rounded-full blur-3xl opacity-20" />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-foreground/10 backdrop-blur-xl bg-background/40">
        <div className="max-w-7xl mx-auto px-4 py-6 flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-2 text-foreground/60 hover:text-foreground transition-colors">
            <ArrowLeft className="w-5 h-5" />
            <span>Back</span>
          </Link>

          <h1 className="text-xl font-bold text-foreground">Repositories</h1>

          <form action={handleSignOut}>
            <button
              type="submit"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-foreground/10 hover:bg-foreground/20 text-foreground transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Sign Out</span>
            </button>
          </form>
        </div>
      </header>

      {/* Main content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 py-12">
        <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h2 className="text-3xl font-bold text-foreground mb-2">
              Your Repositories
            </h2>
            <p className="text-foreground/60">
              Manage and explore your GitHub repositories
            </p>
          </div>
          <Link
            href="/repository/register"
            className="inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-primary text-foreground hover:bg-primary/90 transition-colors font-medium shadow"
          >
            <span>＋</span> Register a Repository
          </Link>
        </div>

        {/* Repository list from API */}
        <div className="backdrop-blur-xl bg-card/40 border border-card-foreground/10 rounded-2xl p-12">
          <div className="flex flex-col items-center justify-center text-center mb-10">
            <div className="w-16 h-16 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center mb-6 opacity-50">
              <Github className="w-8 h-8 text-foreground" />
            </div>
            <h3 className="text-xl font-semibold text-foreground/50 mb-2">
              Your Registered Repositories
            </h3>
            <p className="text-foreground/40 max-w-md">
              Below is a list of repositories you have registered.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {repositories.length === 0 ? (
              <div className="col-span-full text-center text-foreground/40">No repositories found.</div>
            ) : (
              repositories.map((repo) => (
                <Link
                  key={repo.id}
                  href={`/repository/${repo.id}`}
                  className="block bg-background/80 border border-card-foreground/10 rounded-xl p-6 shadow-sm hover:shadow-lg transition-shadow group"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Github className="w-5 h-5 text-foreground/60 group-hover:text-primary transition-colors" />
                    <span className="font-semibold text-foreground group-hover:text-primary transition-colors">
                      {repo.name}
                    </span>
                  </div>
                  <p className="text-foreground/60 text-sm mb-2">{repo.description}</p>
                  <div className="flex items-center gap-4 text-xs text-foreground/40">
                    <span>⭐ {repo.stars}</span>
                    <span>{repo.language}</span>
                    <span>Updated: {repo.updated?.toString().slice(0, 10)}</span>
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>

        {/* Info cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <div className="backdrop-blur-xl bg-card/30 border border-card-foreground/10 rounded-xl p-6">
            <h4 className="text-foreground font-semibold mb-2">
              GitHub Integration
            </h4>
            <p className="text-foreground/60 text-sm leading-relaxed">
              Your OAuth token is securely stored in the session cookie,
              enabling seamless API interactions with GitHub.
            </p>
          </div>

          <div className="backdrop-blur-xl bg-card/30 border border-card-foreground/10 rounded-xl p-6">
            <h4 className="text-foreground font-semibold mb-2">
              Data Security
            </h4>
            <p className="text-foreground/60 text-sm leading-relaxed">
              All sensitive data is encrypted with HTTPS and stored securely in
              httpOnly cookies to prevent XSS attacks.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
