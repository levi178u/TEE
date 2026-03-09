import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
	try {
		const repository = await prisma.repository.findUnique({
			where: { id: params.id },
			include: { owner: true },
		});
		if (!repository) {
			return NextResponse.json({ error: "Repository not found" }, { status: 404 });
		}
		return NextResponse.json(repository);
	} catch (error) {
		return NextResponse.json({ error: "Failed to fetch repository" }, { status: 500 });
	}
}
