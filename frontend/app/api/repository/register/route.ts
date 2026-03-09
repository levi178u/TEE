import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { repoName, amount, code } = body;

    if (!repoName || !amount || !code) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 });
    }

    // Parse the 'code' field if it was sent as a stringified JSON
    let parsedFiles = [];
    try {
      parsedFiles = typeof code === 'string' ? JSON.parse(code) : code;
    } catch (e) {
      return NextResponse.json({ error: "Invalid JSON in code field" }, { status: 400 });
    }

    // Prepare the data for the CodeBase relation
    // We map 'download_url' to 'text' to satisfy the schema's requirement for file content
    const codebaseData = parsedFiles
      .filter((file: any) => file.type === "file")
      .map((file: any) => ({
        filename: file.name,
        language: file.name.split('.').pop() || "text",
        route: file.path,
        text: file.download_url || "No content available", // 'text' is required in your schema
      }));

    // Create the record without the non-existent 'code' field
    const newCode = await prisma.code.create({
      data: {
        repoName,
        amount: parseFloat(amount), // Ensure amount is a Float as per schema
        codeBases: {
          create: codebaseData,
        },
      },
      include: {
        codeBases: true,
      },
    });

    return NextResponse.json({ success: true, code: newCode });
  } catch (error) {
    console.error("Registration Error:", error);
    return NextResponse.json({ error: "Failed to register repository" }, { status: 500 });
  }
}