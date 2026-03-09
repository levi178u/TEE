"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { AlertCircle, ArrowLeft } from "lucide-react";

const errorMessages: Record<string, string> = {
  Configuration: "There is a problem with the server configuration.",
  AccessDenied: "Access was denied. Please try again.",
  Verification: "The verification link was invalid or expired.",
  OAuthSignin: "Error connecting to the OAuth provider.",
  OAuthCallback: "Error in the OAuth callback.",
  OAuthCreateAccount: "Could not create user account.",
  EmailCreateAccount: "Could not create user account.",
  Callback: "Error in callback handler route.",
  EmailSignInError: "Email could not be sent.",
  SessionCallback: "Error in the session callback.",
  Default: "An error occurred. Please try again.",
};

export default function ErrorPage() {
  const searchParams = useSearchParams();
  const error = searchParams.get("error") || "Default";
  const errorMessage =
    errorMessages[error as keyof typeof errorMessages] || errorMessages.Default;

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/10 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-destructive/20 rounded-full blur-3xl opacity-20" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-destructive/20 rounded-full blur-3xl opacity-20" />
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Error card */}
        <div className="backdrop-blur-xl bg-card/40 border border-destructive/30 rounded-2xl p-8 shadow-2xl">
          {/* Error icon */}
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-destructive/20 rounded-full flex items-center justify-center">
              <AlertCircle className="w-8 h-8 text-destructive" />
            </div>
          </div>

          {/* Error content */}
          <h1 className="text-2xl font-bold text-foreground text-center mb-2">
            Authentication Error
          </h1>
          <p className="text-foreground/60 text-center mb-6">{errorMessage}</p>

          {/* Error code */}
          <div className="bg-background/50 border border-border rounded-lg p-4 mb-6">
            <p className="text-foreground/50 text-xs font-mono">
              Error Code: {error}
            </p>
          </div>

          {/* Back button */}
          <Link href="/auth/login" className="w-full block">
            <button className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-primary hover:bg-primary/90 text-foreground font-semibold transition-colors">
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Login</span>
            </button>
          </Link>

          {/* Help text */}
          <p className="text-center text-foreground/40 text-sm mt-6">
            If the problem persists, please contact support or try again later.
          </p>
        </div>
      </div>
    </div>
  );
}
