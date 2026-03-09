import { auth, destroySession } from "@/lib/auth.config";
import { redirect } from "next/navigation";
import { ArrowLeft, MessageSquare, LogOut } from "lucide-react";
import Link from "next/link";

export default async function ChatPage() {
  const session = await auth();

  if (!session) {
    redirect("/auth/login");
  }

  async function handleSignOut() {
    "use server";
    await destroySession();
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
          <Link href="/dashboard" className="flex items-center gap-2 text-foreground/60 hover:text-foreground transition-colors">
            <ArrowLeft className="w-5 h-5" />
            <span>Back</span>
          </Link>

          <h1 className="text-xl font-bold text-foreground">Chat</h1>

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
      <main className="relative z-10 max-w-4xl mx-auto px-4 py-12">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-foreground mb-2">
            Chat Interface
          </h2>
          <p className="text-foreground/60">
            Start a conversation powered by AI
          </p>
        </div>

        {/* Chat container */}
        <div className="backdrop-blur-xl bg-card/40 border border-card-foreground/10 rounded-2xl overflow-hidden flex flex-col h-[600px]">
          {/* Messages area */}
          <div className="flex-1 overflow-y-auto p-6 flex items-center justify-center">
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-accent to-primary rounded-full flex items-center justify-center mx-auto mb-6 opacity-50">
                <MessageSquare className="w-8 h-8 text-foreground" />
              </div>
              <h3 className="text-xl font-semibold text-foreground/50 mb-2">
                Chat Feature
              </h3>
              <p className="text-foreground/40 max-w-md">
                This is a protected page that only authenticated users can access.
                The chat functionality would be implemented here.
              </p>
            </div>
          </div>

          {/* Input area */}
          <div className="border-t border-card-foreground/10 p-4 bg-background/20">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Type a message..."
                disabled
                className="flex-1 bg-input border border-border rounded-lg px-4 py-2 text-foreground placeholder:text-foreground/40 disabled:opacity-50 focus:outline-none"
              />
              <button
                disabled
                className="px-4 py-2 bg-primary text-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        {/* Info section */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="backdrop-blur-xl bg-card/30 border border-card-foreground/10 rounded-xl p-6">
            <h4 className="text-foreground font-semibold mb-2">
              Protected Route
            </h4>
            <p className="text-foreground/60 text-sm leading-relaxed">
              This page is protected by Next.js middleware. Only authenticated
              users can access it. Unauthenticated users are redirected to the
              login page.
            </p>
          </div>

          <div className="backdrop-blur-xl bg-card/30 border border-card-foreground/10 rounded-xl p-6">
            <h4 className="text-foreground font-semibold mb-2">
              Session Verification
            </h4>
            <p className="text-foreground/60 text-sm leading-relaxed">
              Your session is verified server-side using Auth.js. Your user ID
              is: <span className="text-primary">{session.user.id}</span>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
