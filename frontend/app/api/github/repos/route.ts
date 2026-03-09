import { NextResponse } from "next/server";
import { auth } from "@/lib/auth.config";

export async function GET() {
  const session = await auth();
  const token = session?.accessToken;
  if (!token) {
    return NextResponse.json({ error: "Unauthorized: No GitHub token found" }, { status: 401 });
  }
  try {
    const response = await fetch("https://api.github.com/user/repos?sort=updated&per_page=100", {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.github.v3+json",
      },
    });
      const data = await response.json();
      console.log("GitHub repo data:", data);
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch GitHub repos" }, { status: 500 });
  }
}
