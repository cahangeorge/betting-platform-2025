<script lang="ts">
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import type { Match } from '$lib/types';

	let {
		data
	}: {
		data: {
			matches: Match[];
		};
	} = $props();

	const stats = $derived({
		activeMatches: data.matches.length,
		predictionsToday: 0,
		winRate: 0
	});

	const features = [
		{
			title: 'Live Odds',
			description: 'Real-time odds comparison across multiple bookmakers for the best value bets.',
			icon: 'chart',
			accent: 'var(--accent-blue)'
		},
		{
			title: 'AI Predictions',
			description: 'Advanced statistical models including Poisson, Bivariate Poisson, and Ensemble methods.',
			icon: 'robot',
			accent: 'var(--accent-green)'
		},
		{
			title: 'Portfolio Tracking',
			description: 'Track your bankrolls, bookmaker accounts, and betting performance over time.',
			icon: 'wallet',
			accent: 'var(--accent-gold)'
		},
		{
			title: 'Backtesting',
			description: 'Validate strategies against historical data with comprehensive performance metrics.',
			icon: 'beaker',
			accent: 'var(--accent-violet)'
		}
	];

	function iconFor(name: string): string {
		const icons: Record<string, string> = {
			chart: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
			robot: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
			wallet: 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z',
			beaker: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z'
		};
		return icons[name] || icons.chart;
	}
</script>

<div class="space-y-8">
	<div class="text-center py-12 lg:py-20 animate-slide-up">
		<div class="inline-flex items-center space-x-2 px-3 py-1 text-xs font-medium mb-6 badge-live">
			<span class="w-1.5 h-1.5 animate-pulse-dot" style="background-color: var(--accent-green); border-radius: 50%;"></span>
			System Online — Real-time Data
		</div>
		<h1 class="text-4xl lg:text-6xl font-extrabold mb-4 tracking-tight font-sport" style="color: var(--text-primary); letter-spacing: 0.05em;">
			STADIUM INTEL
			<span class="text-gradient-green">Platform</span>
		</h1>
		<p class="text-lg max-w-2xl mx-auto mb-8" style="color: var(--text-secondary);">
			AI-powered football betting analytics, real-time odds comparison, and portfolio tracking
			for data-driven bettors.
		</p>
		<div class="flex items-center justify-center space-x-4">
			<a href="/predict">
				<Button variant="glow" size="lg">View Predictions</Button>
			</a>
			<a href="/board">
				<Button variant="secondary" size="lg">Explore Board</Button>
			</a>
		</div>
	</div>

	<!-- Animated pitch-line pattern -->
	<div class="h-px w-full animate-shimmer" style="background: linear-gradient(90deg, transparent, var(--border-subtle), transparent); background-size: 200% 100%;"></div>

	<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
		<Card variant="active">
			<div class="text-center py-4">
				<p class="text-3xl font-bold font-mono" style="color: var(--accent-green);">{stats.activeMatches}</p>
				<p class="text-sm mt-1" style="color: var(--text-secondary);">Active Matches</p>
			</div>
		</Card>
		<Card variant="data">
			<div class="text-center py-4">
				<p class="text-3xl font-bold font-mono" style="color: var(--accent-blue);">{stats.predictionsToday}</p>
				<p class="text-sm mt-1" style="color: var(--text-secondary);">Predictions Today</p>
			</div>
		</Card>
		<Card variant="prediction">
			<div class="text-center py-4">
				<p class="text-3xl font-bold font-mono" style="color: var(--accent-gold);">{stats.winRate}%</p>
				<p class="text-sm mt-1" style="color: var(--text-secondary);">Win Rate</p>
			</div>
		</Card>
	</div>

	<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
		{#each features as feature (feature.title)}
			<Card interactive>
				<div class="flex items-start space-x-4">
					<div
						class="w-12 h-12 flex items-center justify-center flex-shrink-0"
						style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid rgba(74, 222, 128, 0.2); border-radius: 0;"
					>
						<svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" style="color: {feature.accent};" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
							<path stroke-linecap="round" stroke-linejoin="round" d={iconFor(feature.icon)} />
						</svg>
					</div>
					<div>
						<h3 class="text-lg font-semibold mb-1 font-sport" style="color: var(--text-primary);">{feature.title}</h3>
						<p class="text-sm" style="color: var(--text-secondary);">{feature.description}</p>
					</div>
				</div>
			</Card>
		{/each}
	</div>
</div>
