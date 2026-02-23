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
			lowLabel: "Opinion",
			highLabel: "Factual",
			color: "primary",
		},
		calm: {
			label: "Calm",
			icon: "😌",
			lowLabel: "Rage",
			highLabel: "Calm",
			color: "success",
		},
		depth: {
			label: "Depth",
			icon: "🔍",
			lowLabel: "Fluff",
			highLabel: "Deep",
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

<div class="p-2 bg-base-100 rounded-lg border border-base-content/10 min-w-0">
	<!-- Header: icon + label + badge -->
	<div class="flex-col items-center justify-between gap-1 mb-1.5 min-w-0">
		<span
			class="text-xs font-bold flex items-center gap-1 truncate min-w-0"
		>
			<span class="shrink-0">{config.icon}</span>
			<span class="truncate">{config.label}</span>
		</span>
		<span class="badge badge-{config.color} badge-xs font-semibold shrink-0"
			>{pct}%</span
		>
	</div>

	<!-- Progress bar -->
	<progress
		class="progress progress-{config.color} w-full h-1.5"
		value={pct}
		max="100"
	></progress>

	<!-- Low / High labels below the bar -->
	<div class="flex justify-between mt-0.5">
		<span class="text-[9px] opacity-50 truncate">{config.lowLabel}</span>
		<span class="text-[9px] opacity-50 truncate text-right"
			>{config.highLabel}</span
		>
	</div>
</div>
