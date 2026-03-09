import { NextResponse } from "next/server";
import { auth } from "@/lib/auth.config";
import { prisma } from "@/lib/prisma";
import path from "path";

export async function GET(req: Request, context: { params: { repo: string } } | { params: Promise<{ repo: string }> }) {
  const session = await auth();
  const token = session?.accessToken;

  if (!token) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const resolvedParams = context.params instanceof Promise ? await context.params : context.params;
  const repo = resolvedParams.repo;

  const { searchParams } = new URL(req.url);
  const owner = searchParams.get("owner");
  const filePath = searchParams.get("path") || "";
  const ref = searchParams.get("ref") || "main";

  if (!owner) return NextResponse.json({ error: "Missing owner" }, { status: 400 });

  const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${encodeURIComponent(filePath)}?ref=${encodeURIComponent(ref)}`;

  try {
    const response = await fetch(apiUrl, {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      const err = await response.json();
      return NextResponse.json({ error: err.message }, { status: response.status });
    }

    const data = await response.json();

    if (data.type === "file") {
      const decodedContent = Buffer.from(data.content, "base64").toString("utf8");

      // Ensure a parent 'Code' record exists for this repo to maintain the relationship
      let codeRecord = await prisma.code.findFirst({
        where: { repoName: `${owner}/${repo}` }
      });

      if (!codeRecord) {
        codeRecord = await prisma.code.create({
          data: {
            repoName: `${owner}/${repo}`,
            amount: 0, // Default or placeholder amount
          }
        });
      }

      const storedFile = await prisma.codeBase.create({
        data: {
          filename: data.name,
          language: path.extname(data.name).slice(1) || "text",
          route: data.path,
          text: decodedContent,
          codeId: codeRecord.id,
        }
      });

      return NextResponse.json({
        type: "file",
        dbId: storedFile.id,
        content: decodedContent,
      });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("GitHub Fetch Error:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}