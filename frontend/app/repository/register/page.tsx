"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import Link from "next/link";
import { Github, PlusCircle, MessageSquare } from "lucide-react";



function RegisterRepositoryPageInner() {
	const { data: session } = useSession();
	// Ensure github_access_token cookie is set for API routes
	useEffect(() => {
		if (typeof window === 'undefined') return;
		if (session?.user?.accessToken) {
			// Call backend to set httpOnly cookie
			fetch("/api/auth/post-login", {
				method: "POST",
				credentials: "include"
			});
		}
	}, [session?.user?.accessToken]);
	const [repos, setRepos] = useState([]);
	const [selectedRepo, setSelectedRepo] = useState("");
	const [description, setDescription] = useState("");
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [success, setSuccess] = useState(false);

	useEffect(() => {
		async function fetchRepos() {
			console.log("Session object:", session);
			setLoading(true);
			setError("");
			try {
				const res = await fetch("/api/github/repos", { credentials: "include" });
				console.log("GitHub API fetch response:", res);
				if (!res.ok) {
					setError("Failed to fetch repositories");
					setRepos([]);
					const errorText = await res.text();
					console.error("GitHub API error response:", errorText);
				} else {
					const data = await res.json();
					setRepos(data);
					console.log("Fetched repositories:", data);
				}
			} catch (err) {
				setError("Network error");
				setRepos([]);
				console.error("Network error while fetching repos:", err);
			} finally {
				setLoading(false);
			}
		}
		fetchRepos();
	}, [session]);

	async function handleSubmit(e) {
		e.preventDefault();
		setLoading(true);
		setError("");
		setSuccess(false);
		try {
			// TODO: Replace with real user ID from session or authentication context
			const ownerId = session?.user?.id;
			const repo = repos.find(r => r.full_name === selectedRepo);
			const name = repo ? repo.name : "";
			const res = await fetch("/api/repository", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ name, description, ownerId }),
			});
			if (!res.ok) {
				const data = await res.json();
				setError(data.error || "Failed to register repository");
			} else {
				setSuccess(true);
				setSelectedRepo("");
				setDescription("");
			}
		} catch (err) {
			setError("Network error");
		} finally {
			setLoading(false);
		}
	}

	return (
		<div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/10 relative overflow-hidden">
			<div className="absolute inset-0 overflow-hidden pointer-events-none">
				<div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/20 rounded-full blur-3xl opacity-20" />
				<div className="absolute -bottom-40 -left-40 w-80 h-80 bg-accent/20 rounded-full blur-3xl opacity-20" />
			</div>
			<main className="relative z-10 max-w-xl mx-auto px-4 py-16">
				<div className="backdrop-blur-xl bg-card/40 border border-card-foreground/10 rounded-2xl p-10">
					<div className="flex items-center gap-3 mb-6">
						<PlusCircle className="w-8 h-8 text-primary" />
						<h2 className="text-2xl font-bold text-foreground">Register New Repository</h2>
					</div>
					<form className="space-y-6" onSubmit={handleSubmit}>
						<div>
							<label className="block text-foreground/70 mb-1 font-medium">Select Repository</label>
							{/* Repository select input and other form elements go here */}
						</div>
						{/* ...other form fields... */}
						{/* You can add instructions or info here if needed */}
					</form>
						</div>
					</main>
				</div>
			);
}

export default function RegisterRepositoryPage(props) {
	return <RegisterRepositoryPageInner {...props} />;
}

