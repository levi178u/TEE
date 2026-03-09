
import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { setAccessTokenCookie } from "@/lib/accessTokenCookie";

// POST /api/auth/post-login
export async function POST(request: NextRequest) {
  const token = await getToken({ req: request, secret: process.env.AUTH_SECRET });
  if (!token || !token.accessToken) {
    return NextResponse.json({ error: "No access token found" }, { status: 401 });
  }
  const response = NextResponse.json({ success: true });
  response.headers.append("Set-Cookie", setAccessTokenCookie(token.accessToken));
  return response;
}
