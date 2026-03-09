
import { auth, signOut } from "@/lib/auth.config";
import { redirect } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Github, LogOut, BarChart3, FileText, MessageSquare } from "lucide-react";
import Link from "next/link";

export default async function DashboardPage() {
  const session = await auth();
  console.log('DASHBOARD SESSION', session);

  // Redirect to login if not authenticated
  if (!session) {
    redirect("/auth/login");
  }

  async function handleSignOut() {
    "use server";
    await signOut();
    redirect("/auth/login");
  }

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
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
              <Github className="w-6 h-6 text-foreground" />
            </div>
            <h1 className="text-xl font-bold text-foreground">DevHub</h1>
          </div>

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
        {/* Welcome section */}
        <div className="mb-12">
          <h2 className="text-4xl font-bold text-foreground mb-2">
            Welcome, {session.user.name}!
          </h2>
          <p className="text-foreground/60 text-lg">
            {session.user.email}
          </p>
        </div>

        {/* Navigation cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {/* Repository card */}
          <Link href="/repository">
            <div className="group backdrop-blur-xl bg-card/40 border border-card-foreground/10 rounded-2xl p-6 hover:border-primary/30 transition-all duration-300 cursor-pointer hover:shadow-lg hover:shadow-primary/10">
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <FileText className="w-6 h-6 text-foreground" />
                </div>
                <div className="w-2 h-2 rounded-full bg-primary/50" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Repository
              </h3>
              <p className="text-foreground/60 text-sm">
                Browse your repositories and manage your projects
              </p>
            </div>
          </Link>

          {/* Chat card */}
          <Link href="/chat">
            <div className="group backdrop-blur-xl bg-card/40 border border-card-foreground/10 rounded-2xl p-6 hover:border-primary/30 transition-all duration-300 cursor-pointer hover:shadow-lg hover:shadow-primary/10">
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-accent to-primary rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <MessageSquare className="w-6 h-6 text-foreground" />
                </div>
                <div className="w-2 h-2 rounded-full bg-accent/50" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Chat
              </h3>
              <p className="text-foreground/60 text-sm">
                Start a conversation with AI assistance
              </p>
            </div>
          </Link>

          {/* Analytics card */}
          <div className="group backdrop-blur-xl bg-card/40 border border-card-foreground/10 rounded-2xl p-6 opacity-60 cursor-not-allowed">
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-primary/50 to-accent/50 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-foreground/50" />
              </div>
              <div className="px-2 py-1 bg-muted rounded text-xs text-foreground/60">
                Coming Soon
              </div>
            </div>
            <h3 className="text-lg font-semibold text-foreground/50 mb-2">
              Analytics
            </h3>
            <p className="text-foreground/40 text-sm">
              Track your statistics and insights
            </p>
          </div>
        </div>

        {/* Stats section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="backdrop-blur-xl bg-card/30 border border-card-foreground/10 rounded-xl p-4">
            <p className="text-foreground/60 text-sm mb-1">Account Status</p>
            <p className="text-2xl font-bold text-foreground">Active</p>
          </div>
          <div className="backdrop-blur-xl bg-card/30 border border-card-foreground/10 rounded-xl p-4">
            <p className="text-foreground/60 text-sm mb-1">Session</p>
            <p className="text-2xl font-bold text-foreground">Secure</p>
          </div>
          <div className="backdrop-blur-xl bg-card/30 border border-card-foreground/10 rounded-xl p-4">
            <p className="text-foreground/60 text-sm mb-1">Authentication</p>
            <p className="text-2xl font-bold text-foreground">OAuth 2.0</p>
          </div>
        </div>
      </main>
    </div>
  );
}
