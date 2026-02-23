<script lang="ts">
	import { onMount } from "svelte";
	import { getArticles, type Article } from "$lib/api";
	import ArticleCard from "$lib/components/ArticleCard.svelte";

	let articles: Article[] = [];
	let loading = true;
	let error = "";
	let total = 0;

	// Filter state — one min/max pair per axis
	let minObjectivity = 0,
		maxObjectivity = 1;
	let minCalm = 0,
		maxCalm = 1;
	let minDepth = 0,
		maxDepth = 1;

	$: hasActiveFilters =
		minObjectivity > 0 ||
		maxObjectivity < 1 ||
		minCalm > 0 ||
		maxCalm < 1 ||
		minDepth > 0 ||
		maxDepth < 1;

	async function loadArticles() {
		loading = true;
		error = "";
		try {
			const response = await getArticles(
				20,
				0,
				minObjectivity,
				minCalm,
				minDepth,
			);

			// Client-side max filtering
			articles = (response.articles || []).filter(
				(a) =>
					a.objectivity_score >= minObjectivity &&
					a.objectivity_score <= maxObjectivity &&
					a.calm_score >= minCalm &&
					a.calm_score <= maxCalm &&
					a.depth_score >= minDepth &&
					a.depth_score <= maxDepth,
			);
			total = articles.length;
		} catch (e) {
			error =
				"Failed to load articles. Make sure the backend server is running.";
			articles = [];
			total = 0;
			console.error(e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadArticles();
	});
</script>

<svelte:head>
	<title>Seithi - Quality News Aggregator</title>
</svelte:head>

<div
	class="min-h-screen bg-gradient-to-br from-base-100 via-base-200 to-base-300"
>
	<!-- Hero Header -->
	<div
		class="hero bg-gradient-to-r from-primary to-secondary text-primary-content py-12 shadow-2xl"
	>
		<div class="hero-content text-center">
			<div class="max-w-2xl">
				<h1 class="text-5xl font-bold mb-4">🧠 Seithi</h1>
				<p class="text-xl opacity-90">
					Quality news aggregation powered by ML scoring
				</p>
				<p class="text-sm opacity-70 mt-2">
					Filtering truth from noise, one article at a time
				</p>
			</div>
		</div>
	</div>

	<!-- Main Content -->
	<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Stats Overview -->
		<div
			class="stats stats-vertical lg:stats-horizontal shadow-xl mb-8 w-full bg-base-200"
		>
			<div class="stat">
				<div class="stat-figure text-primary">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						class="inline-block w-8 h-8 stroke-current"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
						></path>
					</svg>
				</div>
				<div class="stat-title">Total Articles</div>
				<div class="stat-value text-primary">{total}</div>
				<div class="stat-desc">Analyzed and scored</div>
			</div>

			<div class="stat">
				<div class="stat-figure text-secondary">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						class="inline-block w-8 h-8 stroke-current"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
						></path>
					</svg>
				</div>
				<div class="stat-title">Active Filters</div>
				<div class="stat-value text-secondary">
					{hasActiveFilters ? "✓" : "—"}
				</div>
				<div class="stat-desc">
					{hasActiveFilters
						? "Filtering enabled"
						: "No filters applied"}
				</div>
			</div>

			<div class="stat">
				<div class="stat-figure text-accent">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						class="inline-block w-8 h-8 stroke-current"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M5 13l4 4L19 7"
						></path>
					</svg>
				</div>
				<div class="stat-title">Showing</div>
				<div class="stat-value text-accent">
					{articles?.length || 0}
				</div>
				<div class="stat-desc">Matching articles</div>
			</div>
		</div>

		<!-- Filters Card -->
		<div class="card bg-base-200 shadow-2xl mb-8 border border-base-300">
			<div class="card-body">
				<h2 class="card-title text-2xl mb-4">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						class="w-6 h-6 stroke-current"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
						></path>
					</svg>
					Filter Articles (Min – Max Range)
				</h2>

				<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
					<!-- Objectivity -->
					<div class="space-y-3">
						<h3 class="font-bold text-base flex items-center gap-2">
							📊 Objectivity
						</h3>
						<p class="text-xs opacity-60">Opinionated → Factual</p>
						<div class="form-control">
							<label class="label py-1" for="obj-min">
								<span class="label-text text-xs font-semibold"
									>Min</span
								>
								<span class="label-text-alt text-xs"
									>{(minObjectivity * 100).toFixed(0)}%</span
								>
							</label>
							<input
								id="obj-min"
								type="range"
								min="0"
								max="1"
								step="0.05"
								bind:value={minObjectivity}
								class="range range-primary range-xs"
							/>
						</div>
						<div class="form-control">
							<label class="label py-1" for="obj-max">
								<span class="label-text text-xs font-semibold"
									>Max</span
								>
								<span class="label-text-alt text-xs"
									>{(maxObjectivity * 100).toFixed(0)}%</span
								>
							</label>
							<input
								id="obj-max"
								type="range"
								min="0"
								max="1"
								step="0.05"
								bind:value={maxObjectivity}
								class="range range-primary range-xs"
							/>
						</div>
					</div>

					<!-- Calm -->
					<div class="space-y-3">
						<h3 class="font-bold text-base flex items-center gap-2">
							😌 Calm
						</h3>
						<p class="text-xs opacity-60">Rage-bait → Calm</p>
						<div class="form-control">
							<label class="label py-1" for="calm-min">
								<span class="label-text text-xs font-semibold"
									>Min</span
								>
								<span class="label-text-alt text-xs"
									>{(minCalm * 100).toFixed(0)}%</span
								>
							</label>
							<input
								id="calm-min"
								type="range"
								min="0"
								max="1"
								step="0.05"
								bind:value={minCalm}
								class="range range-success range-xs"
							/>
						</div>
						<div class="form-control">
							<label class="label py-1" for="calm-max">
								<span class="label-text text-xs font-semibold"
									>Max</span
								>
								<span class="label-text-alt text-xs"
									>{(maxCalm * 100).toFixed(0)}%</span
								>
							</label>
							<input
								id="calm-max"
								type="range"
								min="0"
								max="1"
								step="0.05"
								bind:value={maxCalm}
								class="range range-success range-xs"
							/>
						</div>
					</div>

					<!-- Depth -->
					<div class="space-y-3">
						<h3 class="font-bold text-base flex items-center gap-2">
							🔍 Depth
						</h3>
						<p class="text-xs opacity-60">Fluff → Deep Dive</p>
						<div class="form-control">
							<label class="label py-1" for="depth-min">
								<span class="label-text text-xs font-semibold"
									>Min</span
								>
								<span class="label-text-alt text-xs"
									>{(minDepth * 100).toFixed(0)}%</span
								>
							</label>
							<input
								id="depth-min"
								type="range"
								min="0"
								max="1"
								step="0.05"
								bind:value={minDepth}
								class="range range-info range-xs"
							/>
						</div>
						<div class="form-control">
							<label class="label py-1" for="depth-max">
								<span class="label-text text-xs font-semibold"
									>Max</span
								>
								<span class="label-text-alt text-xs"
									>{(maxDepth * 100).toFixed(0)}%</span
								>
							</label>
							<input
								id="depth-max"
								type="range"
								min="0"
								max="1"
								step="0.05"
								bind:value={maxDepth}
								class="range range-info range-xs"
							/>
						</div>
					</div>
				</div>

				<div class="card-actions justify-end mt-6">
					<button
						class="btn btn-primary btn-wide"
						on:click={loadArticles}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							class="w-5 h-5 stroke-current"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
							></path>
						</svg>
						Apply Filters
					</button>
				</div>
			</div>
		</div>

		<!-- Articles Section -->
		{#if loading}
			<div class="flex flex-col justify-center items-center py-20">
				<span class="loading loading-spinner loading-lg text-primary"
				></span>
				<p class="mt-4 text-lg opacity-70">Loading articles...</p>
			</div>
		{:else if error}
			<div class="alert alert-error shadow-lg">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="stroke-current shrink-0 h-6 w-6"
					fill="none"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				<div>
					<h3 class="font-bold">Connection Error</h3>
					<div class="text-sm">{error}</div>
				</div>
			</div>
		{:else if articles.length === 0}
			<div class="alert alert-warning shadow-lg">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="stroke-current shrink-0 h-6 w-6"
					fill="none"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
					/>
				</svg>
				<div>
					<h3 class="font-bold">No Articles Found</h3>
					<div class="text-sm">
						No articles match your current filters. Try adjusting
						the filter values.
					</div>
				</div>
			</div>
		{:else}
			<div class="space-y-6">
				{#each articles as article (article.id)}
					<ArticleCard {article} />
				{/each}
			</div>
		{/if}
	</main>

	<!-- Footer -->
	<footer
		class="footer footer-center p-10 bg-base-300 text-base-content mt-20"
	>
		<aside>
			<p class="font-bold text-lg">Seithi News Aggregator</p>
			<p class="opacity-70">
				ML-powered quality scoring for better news consumption
			</p>
			<p class="text-sm opacity-50 mt-2">
				Built with SvelteKit and Cloudflare D1
			</p>
		</aside>
	</footer>
</div>
