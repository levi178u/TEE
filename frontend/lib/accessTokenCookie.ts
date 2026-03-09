import { serialize } from "cookie";
import { NextResponse } from "next/server";

export function setAccessTokenCookie(token: string) {
  console.log("[setAccessTokenCookie] Setting github_access_token cookie with token:", token);
  return serialize("github_access_token", token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7, // 1 week
  });
}

export function getAccessTokenFromRequest(req: Request) {
  const cookie = req.headers.get("cookie");
  console.log("[getAccessTokenFromRequest] Retrieving github_access_token from request cookie:", cookie);
  if (!cookie) return null;
  const match = cookie.match(/github_access_token=([^;]+)/);
  return match ? match[1] : null;
}
