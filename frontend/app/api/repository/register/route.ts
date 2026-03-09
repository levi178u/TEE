import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

// POST /api/repository/register
export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { repoName, amount, code } = body;
    if (!repoName || !amount || !code) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 });
    }

    // Store in Code table
    const newCode = await prisma.code.create({
      data: {
        repoName,
        amount: parseFloat(amount),
        code,
      },
    });
    return NextResponse.json({ success: true, code: newCode });
  } catch (error) {
    return NextResponse.json({ error: "Failed to register repository" }, { status: 500 });
  }
}
