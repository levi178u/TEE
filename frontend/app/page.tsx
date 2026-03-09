import Link from "next/link";
import { auth } from "@/lib/auth.config";
import { Github, ArrowRight } from "lucide-react";

export default async function Home() {
  const session = await auth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/10 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/20 rounded-full blur-3xl opacity-30" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-accent/20 rounded-full blur-3xl opacity-30" />
      </div>

      <div className="relative z-10 max-w-2xl text-center">
        {/* Logo/Brand */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
            <Github className="w-7 h-7 text-foreground" />
          </div>
          <h1 className="text-4xl font-bold text-foreground">DevHub</h1>
        </div>

        {/* Main heading */}
        <h2 className="text-5xl md:text-6xl font-bold text-foreground mb-4 tracking-tight text-pretty">
          A Front-End Environment Made For Testing And Sharing
        </h2>

        {/* Description */}
        <p className="text-xl text-foreground/60 mb-12 leading-relaxed max-w-lg mx-auto text-pretty">
          Browse and share work from world-class designers and developers in the
          front-end community. Securely authenticated with GitHub OAuth.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
          {session ? (
            <Link href="/dashboard">
              <button className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-primary to-accent/80 p-0.5 transition-all duration-300 hover:shadow-lg hover:shadow-primary/50">
                <div className="relative bg-background rounded-[10px] px-8 py-4 flex items-center justify-center gap-2 group-hover:bg-background/80 transition-colors">
                  <span className="text-foreground font-semibold">
                    Go to Dashboard
                  </span>
                  <ArrowRight className="w-5 h-5 text-foreground group-hover:translate-x-1 transition-transform" />
                </div>
              </button>
            </Link>
          ) : (
            <Link href="/auth/login">
              <button className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-primary to-accent/80 p-0.5 transition-all duration-300 hover:shadow-lg hover:shadow-primary/50">
                <div className="relative bg-background rounded-[10px] px-8 py-4 flex items-center justify-center gap-2 group-hover:bg-background/80 transition-colors">
                  <span className="text-foreground font-semibold">
                    Sign In with GitHub
                  </span>
                  <ArrowRight className="w-5 h-5 text-foreground group-hover:translate-x-1 transition-transform" />
                </div>
              </button>
            </Link>
          )}
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Feature 1 */}
          <div className="group backdrop-blur-xl bg-card/40 border border-card-foreground/10 rounded-2xl p-8 hover:border-primary/30 transition-all duration-300">
            <div className="mb-4">
              <div className="inline-block w-10 h-10 bg-primary/20 rounded-lg flex items-center justify-center">
                <span className="text-primary font-bold">1</span>
              </div>
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2 text-left">
              Find inspiration from 1.8M+ developers
            </h3>
            <p className="text-foreground/60 text-sm text-left">
              Explore designs and code from the world-class front-end community
            </p>
          </div>

          {/* Feature 2 */}
          <div className="group backdrop-blur-xl bg-card/40 border border-card-foreground/10 rounded-2xl p-8 hover:border-primary/30 transition-all duration-300">
            <div className="mb-4">
              <div className="inline-block w-10 h-10 bg-accent/20 rounded-lg flex items-center justify-center">
                <span className="text-accent font-bold">2</span>
              </div>
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2 text-left">
              Browse and share world-class work
            </h3>
            <p className="text-foreground/60 text-sm text-left">
              Showcase your projects and discover new techniques from other developers
            </p>
          </div>
        </div>

        {/* Trust badges */}
        <div className="mt-16 pt-12 border-t border-foreground/10">
          <p className="text-foreground/50 text-sm mb-6">
            Trusted by developers worldwide
          </p>
          <div className="flex items-center justify-center gap-8 flex-wrap">
            <div className="backdrop-blur-xl bg-card/30 border border-card-foreground/10 rounded-lg px-4 py-2">
              <p className="text-foreground font-semibold">✓ OAuth 2.0</p>
            </div>
            <div className="backdrop-blur-xl bg-card/30 border border-card-foreground/10 rounded-lg px-4 py-2">
              <p className="text-foreground font-semibold">✓ Secure Session</p>
            </div>
            <div className="backdrop-blur-xl bg-card/30 border border-card-foreground/10 rounded-lg px-4 py-2">
              <p className="text-foreground font-semibold">✓ Encrypted Cookies</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
