<script lang="ts">
	import { submitFeedback } from "$lib/api";

	export let articleId: string;
	export let axis: string;
	export let labels: string[];
	export let scores: number[];
	export let colors: string[] = ["error", "warning", "success"];

	let showFeedback = false;
	let feedbackSubmitted = false;

	const axisLabels: Record<string, string> = {
		epistemic: "Epistemic (Truth)",
		emotive: "Emotive (Tone)",
		density: "Density (Depth)",
	};

	const axisIcons: Record<string, string> = {
		epistemic: "📊",
		emotive: "😌",
		density: "🔍",
	};

	async function handleFeedback(scoreIndex: number) {
		try {
			await submitFeedback({
				article_id: articleId,
				axis: axis,
				user_score: scoreIndex,
			});
			feedbackSubmitted = true;
			showFeedback = false;
			setTimeout(() => {
				feedbackSubmitted = false;
			}, 3000);
		} catch (error) {
			console.error("Failed to submit feedback:", error);
		}
	}
</script>

<div class="p-3 bg-base-100 rounded-lg border border-base-content/10">
	<div class="flex justify-between items-center mb-2">
		<h4 class="text-xs font-bold flex items-center gap-1">
			<span>{axisIcons[axis]}</span>
			<span class="hidden sm:inline">{axisLabels[axis]}</span>
			<span class="sm:hidden"
				>{axis === "epistemic"
					? "Truth"
					: axis === "emotive"
						? "Tone"
						: "Depth"}</span
			>
		</h4>
		{#if !feedbackSubmitted}
			<button
				on:click={() => (showFeedback = !showFeedback)}
				class="btn btn-xs {showFeedback ? 'btn-error' : 'btn-ghost'}"
			>
				{#if showFeedback}
					✕
				{:else}
					✏️
				{/if}
			</button>
		{:else}
			<div class="badge badge-success badge-xs gap-1">✓</div>
		{/if}
	</div>

	{#if showFeedback}
		<div class="mb-2 p-2 bg-base-200 rounded border border-primary/30">
			<p class="text-xs mb-1 opacity-70">Select correct:</p>
			<div class="flex flex-col gap-1">
				{#each labels as label, i}
					<button
						class="btn btn-xs btn-outline hover:btn-{colors[i]}"
						on:click={() => handleFeedback(i)}
					>
						{label}
					</button>
				{/each}
			</div>
		</div>
	{/if}

	<div class="space-y-2">
		{#each labels as label, i}
			<div class="space-y-1">
				<div class="flex items-center justify-between text-xs">
					<span
						class="font-medium opacity-80 truncate text-[10px] sm:text-xs"
						>{label}</span
					>
					<span class="badge badge-{colors[i]} badge-xs">
						{(scores[i] * 100).toFixed(0)}%
					</span>
				</div>
				<progress
					class="progress progress-{colors[i]} w-full h-2"
					value={scores[i] * 100}
					max="100"
				></progress>
			</div>
		{/each}
	</div>
</div>
