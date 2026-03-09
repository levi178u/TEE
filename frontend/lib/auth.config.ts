
import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import { PrismaAdapter } from "@auth/prisma-adapter";
import { prisma } from "./prisma";


export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  session: { strategy: "jwt" },
  providers: [
    GitHub({
      clientId: process.env.AUTH_GITHUB_ID!,
      clientSecret: process.env.AUTH_GITHUB_SECRET!,
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
      // Step 1: Capture token from the initial login
      if (account) {
        token.accessToken = account.access_token;
      }
      return token;
    },
    async session({ session, token, user }) {
      // Step 2: Transfer token from JWT to Session object
      if (token?.accessToken) {
        session.accessToken = token.accessToken as string;
      }
      // Add user id to session
      if (user && user.id) {
        session.user.id = user.id;
      } else if (token && token.sub) {
        session.user.id = token.sub as string;
      }
      return session;
    },
  },
});