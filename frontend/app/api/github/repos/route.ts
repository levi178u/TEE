

import { NextRequest, NextResponse } from "next/server";
import { getAccessTokenFromRequest } from "@/lib/accessTokenCookie";

export async function GET(request: NextRequest) {
  const accessToken = getAccessTokenFromRequest(request);
  if (!accessToken) {
    return NextResponse.json({ error: "Missing access token (cookie)" }, { status: 401 });
  }
  const res = await fetch("https://api.github.com/user/repos?per_page=100", {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      Accept: "application/vnd.github+json",
    },
  });
  if (!res.ok) {
    return NextResponse.json({ error: "Failed to fetch repositories" }, { status: 500 });
  }
  const repos = await res.json();
  return NextResponse.json(repos);
}
