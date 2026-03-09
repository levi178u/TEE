import { NextResponse } from "next/server";
import { auth } from "@/lib/auth.config";

// For Next.js Route Handlers, the context includes route params
export async function GET(req: Request, context: { params: { repo: string } } | { params: Promise<{ repo: string }> }) {
  const session = await auth();
  const token = session?.accessToken;

  if (!token) {
    return NextResponse.json({ error: "Unauthorized: No GitHub token found" }, { status: 401 });
  }

  // Unwrap params if it's a Promise (Next.js 14+)
  let repo: string;
  if (context.params instanceof Promise) {
    const params = await context.params;
    repo = params.repo;
  } else {
    repo = context.params.repo;
  }

  // Parse query params: owner (required), path (optional), ref (optional)
  const { searchParams } = new URL(req.url);
  const owner = searchParams.get("owner");
  const path = searchParams.get("path") || ""; // Empty path means repo root
  const ref = searchParams.get("ref") || "main";

  if (!owner) {
    return NextResponse.json({ error: "Missing ?owner=OWNER in query" }, { status: 400 });
  }

  // Construct the GitHub API URL
  const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${encodeURIComponent(path)}?ref=${encodeURIComponent(ref)}`;

  try {
    const response = await fetch(apiUrl, {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.github.v3+json",
      },
    });
    if (!response.ok) {
      const err = await response.json();
      return NextResponse.json({ error: err.message || "Failed to fetch content" }, { status: response.status });
    }

    const data = await response.json();

    // If it's a file, decode base64. If it's an array (folder), return as is.
    if (Array.isArray(data)) {
      return NextResponse.json({ type: "dir", contents: data });
    } else if (data.type === "file") {
      let decodedContent = "";
      if (data.content) {
        decodedContent = Buffer.from(data.content, "base64").toString("utf8");
      }
      return NextResponse.json({
        type: "file",
        name: data.name,
        path: data.path,
        encoding: data.encoding,
        content: decodedContent,
      });
    } else {
      // Could be symlink, submodule, etc.
      return NextResponse.json(data);
    }
  } catch (error) {
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}