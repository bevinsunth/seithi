<script lang="ts">
	import { submitFeedback } from "$lib/api";

	export let articleId: string;
	export let axis: string; // 'objectivity' | 'calm' | 'depth'
	export let score: number; // 0.0 – 1.0

	let feedbackSubmitted = false;

	const axisConfig: Record<
		string,
		{
			label: string;
			icon: string;
			lowLabel: string;
			highLabel: string;
			color: string;
		}
	> = {
		objectivity: {
			label: "Objectivity",
			icon: "📊",
			lowLabel: "Opinionated",
			highLabel: "Factual",
			color: "primary",
		},
		calm: {
			label: "Calm",
			icon: "😌",
			lowLabel: "Rage-bait",
			highLabel: "Calm",
			color: "success",
		},
		depth: {
			label: "Depth",
			icon: "🔍",
			lowLabel: "Fluff",
			highLabel: "Deep Dive",
			color: "info",
		},
	};

	$: config = axisConfig[axis] ?? {
		label: axis,
		icon: "📈",
		lowLabel: "Low",
		highLabel: "High",
		color: "neutral",
	};
	$: pct = Math.round(score * 100);

	async function handleFeedback(correctedScore: number) {
		try {
			await submitFeedback({
				article_id: articleId,
				axis,
				user_score: correctedScore,
			});
			feedbackSubmitted = true;
		} catch (error) {
			console.error("Failed to submit feedback:", error);
		}
	}
</script>

<div class="p-3 bg-base-100 rounded-lg border border-base-content/10">
	<div class="flex justify-between items-center mb-2">
		<h4 class="text-xs font-bold flex items-center gap-1">
			<span>{config.icon}</span>
			<span>{config.label}</span>
		</h4>
		{#if feedbackSubmitted}
			<div class="badge badge-success badge-xs gap-1">✓</div>
		{/if}
	</div>

	<!-- Score bar -->
	<div class="space-y-1">
		<div class="flex items-center justify-between text-[10px] opacity-60">
			<span>{config.lowLabel}</span>
			<span class="badge badge-{config.color} badge-xs font-semibold"
				>{pct}%</span
			>
			<span>{config.highLabel}</span>
		</div>
		<progress
			class="progress progress-{config.color} w-full h-2"
			value={pct}
			max="100"
		></progress>
	</div>
</div>
