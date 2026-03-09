
import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import { PrismaAdapter } from "@auth/prisma-adapter";
import { prisma } from "./prisma";
import { setAccessTokenCookie } from "./accessTokenCookie";

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    GitHub({
      clientId: process.env.AUTH_GITHUB_ID!,
      clientSecret: process.env.AUTH_GITHUB_SECRET!,
      allowSignup: true,
      authorization: {
        params: {
          // 'repo' scope grants access to public and private repositories
          scope: "read:user user:email repo",
          prompt: "consent",
        },
      },
    }),
  ],
  callbacks: {
    async jwt({ token, account }) {
      // Store accessToken in token on sign in
      if (account && account.provider === "github" && account.access_token) {
        token.accessToken = account.access_token;
        console.log("[NextAuth jwt callback] Storing access token in JWT:", token.accessToken);
      }
      return token;
    },
    async session({ session, token, user }) {
      // Always ensure session.user exists
      if (!session.user) session.user = {};
      if (user && user.id) {
        session.user.id = user.id;
      }
      // Attach accessToken to session and session.user for client use
      if (token && token.accessToken) {
        session.accessToken = token.accessToken;
        session.user.accessToken = token.accessToken;
        console.log("[NextAuth session callback] Session object before setting cookie:", session);
      }
      if (process.env.NODE_ENV !== 'production') {
        // eslint-disable-next-line no-console
        console.log('[NextAuth session callback] session:', JSON.stringify(session));
      }
      return session;
    },
  },
});