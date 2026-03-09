"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import Link from "next/link";
import { Github, PlusCircle, MessageSquare } from "lucide-react";
import { JSX } from "react/jsx-runtime";


interface Repository {
	id: number;
	name: string;
	full_name: string;
	[key: string]: any;
}

function RegisterRepositoryPageInner() {
const { data: session } = useSession();
const [repos, setRepos] = useState<Repository[]>([]);
	const [selectedRepo, setSelectedRepo] = useState("");
	const [price, setPrice] = useState("");
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [success, setSuccess] = useState(false);

	useEffect(() => {
		async function fetchRepos() {
			setLoading(true);
			setError("");
			try {
				// The API route now uses the session for the access token
				const res = await fetch("/api/github/repos");
				console.log("Response from /api/github/repos:", res);
				if (!res.ok) {
					setError("Failed to fetch repositories");
					setRepos([]);
				} else {
					const data = await res.json();
					setRepos(data);
				}
			} catch (err) {
				setError("Network error");
				setRepos([]);
			} finally {
				setLoading(false);
			}
		}
		fetchRepos();
	}, [session]);

	async function handleSubmit(e: { preventDefault: () => void }) {
		e.preventDefault();
		setLoading(true);
		setError("");
		setSuccess(false);
		try {
			const repo = repos.find(r => r.full_name === selectedRepo);
			if (!repo) {
				setError("No repository selected");
				setLoading(false);
				return;
			}
			// Fetch code from GitHub API route
			const [owner, repoName] = repo.full_name.split("/");
			const codeRes = await fetch(`/api/github/repos/${repoName}?owner=${owner}`);
			if (!codeRes.ok) {
				const errData = await codeRes.json();
				setError(errData.error || "Failed to fetch repository code");
				setLoading(false);
				return;
			}
			const codeData = await codeRes.json();
			let code = "";
			if (codeData.type === "file") {
				code = codeData.content;
			} else if (codeData.type === "dir" && Array.isArray(codeData.contents)) {
				// For MVP, concatenate all file names in root (or extend to fetch each file's content)
				code = codeData.contents.map((f: any) => f.name).join(", ");
			} else {
				code = JSON.stringify(codeData);
			}
			// Send to register API
			const registerRes = await fetch("/api/repository/register", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					repoName: repo.full_name,
					amount: price,
					code,
				}),
			});
			if (!registerRes.ok) {
				const err = await registerRes.json();
				setError(err.error || "Failed to register repository");
			} else {
				setSuccess(true);
				setSelectedRepo("");
				setPrice("");
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
							<select
								className="w-full mt-1 p-2 border rounded bg-background text-foreground"
								value={selectedRepo}
								onChange={e => setSelectedRepo(e.target.value)}
								required
								disabled={loading || repos.length === 0}
							>
								<option value="" disabled>
									{loading ? "Loading repositories..." : "Select a repository"}
								</option>
								{repos.map(repo => (
									<option key={repo.id} value={repo.full_name}>
										{repo.full_name}
									</option>
								))}
							</select>
						</div>
						<div>
							<label className="block text-foreground/70 mb-1 font-medium">Repository Price</label>
							<input
								type="number"
								className="w-full mt-1 p-2 border rounded bg-background text-foreground"
								placeholder="Enter price"
								min="0"
								step="0.01"
								value={price}
								onChange={e => setPrice(e.target.value)}
								required
								disabled={loading}
							/>
						</div>
						{/* ...other form fields... */}
						{/* You can add instructions or info here if needed */}
							<button
								type="submit"
								className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded font-semibold hover:bg-primary/90 disabled:opacity-50"
								disabled={loading || !selectedRepo}
							>
								{loading ? (
									<span>Registering...</span>
								) : (
									<>
										<PlusCircle className="w-5 h-5" /> Register Repository
									</>
								)}
							</button>
						</form>
				</div>
			</main>
		</div>
	);
}

export default function RegisterRepositoryPage(props: JSX.IntrinsicAttributes) {
	return <RegisterRepositoryPageInner {...props} />;
}

