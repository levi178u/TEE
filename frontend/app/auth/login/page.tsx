
"use client";
import { signIn } from "next-auth/react";

export default function LoginPage() {
  console.log('LOGIN PAGE RENDERED');
  return (
    <button
      type="button"
      onClick={() => signIn("github", { callbackUrl: "/dashboard" })}
    >
      Sign in with GitHub
    </button>
  );
}