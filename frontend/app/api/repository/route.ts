import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

// Get all repositories
export async function GET(req: NextRequest) {
	try {
		const repositories = await prisma.repository.findMany({
			include: { owner: true },
			orderBy: { updated: "desc" },
		});
		return NextResponse.json(repositories);
	} catch (error) {
		return NextResponse.json({ error: "Failed to fetch repositories" }, { status: 500 });
	}
}

// Register a new repository
export async function POST(req: NextRequest) {
	try {
		const body = await req.json();
        console.log("Received repository data:", body); // Debug log
		const { name, description, url, license, language, stars, forks, issues, ownerId } = body;
		if (!name || !ownerId) {
			return NextResponse.json({ error: "Name and ownerId are required" }, { status: 400 });
		}
		const repository = await prisma.repository.create({
			data: {
				name,
				description,
				url,
				license,
				language,
				stars: stars ?? 0,
				forks: forks ?? 0,
				issues: issues ?? 0,
				ownerId,
			},
		});
		return NextResponse.json(repository, { status: 201 });
	} catch (error) {
		return NextResponse.json({ error: "Failed to register repository" }, { status: 500 });
	}
}
