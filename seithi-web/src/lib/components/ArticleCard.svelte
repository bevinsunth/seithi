<script lang="ts">
	import type { Article } from "$lib/api";
	import ScoreBar from "./ScoreBar.svelte";

	export let article: Article;

	const formatDate = (dateString: string | undefined) => {
		if (!dateString) return "Unknown date";
		return new Date(dateString).toLocaleDateString("en-US", {
			year: "numeric",
			month: "short",
			day: "numeric",
			hour: "2-digit",
			minute: "2-digit",
		});
	};

	// Extract domain from URL
	const getDomain = (url: string) => {
		try {
			return new URL(url).hostname.replace("www.", "");
		} catch {
			return article.domain;
		}
	};
</script>

<div
	class="card bg-base-200 shadow-2xl hover:shadow-primary/20 transition-all duration-300 border border-base-300"
>
	<div class="card-body">
		<!-- Article Header -->
		<div class="flex items-start gap-4 mb-4">
			<div class="avatar placeholder">
				<div
					class="bg-primary text-primary-content rounded-full w-12 h-12"
				>
					<span class="text-xl">📰</span>
				</div>
			</div>
			<div class="flex-1">
				<h2
					class="card-title text-xl hover:text-primary transition-colors"
				>
					<a
						href={article.url}
						target="_blank"
						rel="noopener noreferrer"
						class="link link-hover"
					>
						{article.title}
					</a>
				</h2>
				<div class="flex flex-wrap gap-3 mt-2 text-sm opacity-70">
					<div class="badge badge-outline badge-primary gap-2">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							class="w-3 h-3 stroke-current"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
							></path>
						</svg>
						{getDomain(article.url)}
					</div>
					<div class="badge badge-outline gap-2">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							class="w-3 h-3 stroke-current"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
							></path>
						</svg>
						{formatDate(article.published_at)}
					</div>
				</div>
			</div>
		</div>

		<div class="divider my-2"></div>

		<!-- ML Scores Section -->
		<div class="bg-base-300 rounded-lg p-4">
			<div class="flex items-center gap-2 mb-4">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
					class="w-5 h-5 stroke-current text-primary"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
					></path>
				</svg>
				<h3 class="font-semibold text-sm">ML Quality Scores</h3>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-3 gap-3">
				<ScoreBar
					articleId={article.id}
					axis="epistemic"
					labels={["Opinionated", "Balanced", "Factual"]}
					scores={[
						article.epistemic_opinion_score,
						article.epistemic_mixed_score,
						article.epistemic_facts_score,
					]}
					colors={["error", "warning", "success"]}
				/>

				<ScoreBar
					articleId={article.id}
					axis="emotive"
					labels={["Triggering", "Neutral", "Calm"]}
					scores={[
						article.emotive_triggering_score,
						article.emotive_mixed_score,
						article.emotive_calm_score,
					]}
					colors={["error", "warning", "success"]}
				/>

				<ScoreBar
					articleId={article.id}
					axis="density"
					labels={["Fluff", "Standard", "Deep"]}
					scores={[
						article.density_fluff_score,
						article.density_standard_score,
						article.density_deep_score,
					]}
					colors={["error", "warning", "success"]}
				/>
			</div>
		</div>

		<!-- Card Actions -->
		<div class="card-actions justify-end mt-4">
			<a
				href={article.url}
				target="_blank"
				rel="noopener noreferrer"
				class="btn btn-primary btn-sm"
			>
				Read Article
				<svg
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
					class="w-4 h-4 stroke-current"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
					></path>
				</svg>
			</a>
		</div>
	</div>
</div>
