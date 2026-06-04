<script lang="ts">
	import type { PageData } from './$types';
	import Card from '$lib/components/ui/Card.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Loading from '$lib/components/Loading.svelte';
	import { onMount } from 'svelte';

	let { data }: { data: PageData } = $props();

	let statusFilter = $state<'All' | 'Live' | 'Halftime' | 'Finished'>('All');
	let selectedLeague = $state<string>('All');
	let sortBy = $state<'time' | 'momentum' | 'score'>('time');
	let lastUpdated = $state(data.lastUpdated || new Date().toISOString());

	const allLeagues = ['All', 'Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1'];

	const filteredMatches = $derived(() => {
		if (!data.matches) return [];
		let matches = [...data.matches];
		if (statusFilter !== 'All') {
			matches = matches.filter(m => m.status === statusFilter.toLowerCase());
		}
		if (selectedLeague !== 'All') {
			matches = matches.filter(m => m.league === selectedLeague);
		}
		matches.sort((a, b) => {
			if (sortBy === 'time') return (b.minute || 0) - (a.minute || 0);
			if (sortBy === 'momentum') {
				const mA = a.momentum_intensity === 'overwhelming' ? 4 : a.momentum_intensity === 'strong' ? 3 : a.momentum_intensity === 'moderate' ? 2 : 1;
				const mB = b.momentum_intensity === 'overwhelming' ? 4 : b.momentum_intensity === 'strong' ? 3 : b.momentum_intensity === 'moderate' ? 2 : 1;
				return mB - mA;
			}
			return (b.home_score || 0 + (b.away_score || 0)) - (a.home_score || 0 + (a.away_score || 0));
		});
		return matches;
	});

	// Auto-refresh every 10 seconds
	onMount(() => {
		const interval = setInterval(() => {
			lastUpdated = new Date().toISOString();
			// In real implementation, trigger a data refresh here
		}, 10000);
		return () => clearInterval(interval);
	});

	function getStatusBadge(status: string): { variant: string; label: string } {
		switch (status) {
			case 'live': return { variant: 'live', label: 'LIVE' };
			case 'halftime': return { variant: 'warning', label: 'HT' };
			case 'finished': return { variant: 'info', label: 'FT' };
			default: return { variant: 'default', label: status.toUpperCase() };
		}
	}

	function formatMinute(minute: number | undefined): string {
		if (minute === undefined) return '-';
		return `${minute}'`;
	}

	function timeAgo(iso: string): string {
		const date = new Date(iso);
		const now = new Date();
		const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
		if (seconds < 60) return `${seconds}s ago`;
		const mins = Math.floor(seconds / 60);
		return `${mins}m ago`;
	}
</script>

<svelte:head>
	<title>Live Matches | Stadium Intel</title>
	<meta name="description" content="Real-time match scores, stats, and momentum indicators" />
</svelte:head>

<div class="space-y-6">
	<!-- Header with pulsing live indicator -->
	<div class="flex items-center gap-3 border-b pb-4" style="border-color: var(--border-subtle);">
		<div class="relative">
			<div class="w-3 h-3 rounded-full" style="background: var(--accent-green);"></div>
			<div
				class="absolute inset-0 w-3 h-3 rounded-full animate-ping"
				style="background: var(--accent-green); opacity: 0.5;"
			></div>
		</div>
		<div>
			<h1 class="text-2xl font-extrabold tracking-tight font-sport" style="color: var(--text-primary);">LIVE MATCHES</h1>
			<p style="color: var(--text-secondary);">Real-time odds, stats, and momentum</p>
		</div>
		<div class="ml-auto text-xs font-mono" style="color: var(--text-muted);">
			Updated {timeAgo(lastUpdated)}
		</div>
	</div>

	<!-- Filters -->
	<Card>
		<div class="p-4 flex flex-wrap items-center gap-4">
			<div class="flex items-center gap-2">
				<span class="text-xs uppercase tracking-wider" style="color: var(--text-secondary);">Status:</span>
				{#each ['All', 'Live', 'Halftime', 'Finished'] as status}
					<button
						onclick={() => statusFilter = status as 'All' | 'Live' | 'Halftime' | 'Finished'}
						class="px-3 py-1 text-xs font-medium border transition-all duration-200"
						style="border-radius: 0; font-family: var(--font-mono);"
						style:background-color={statusFilter === status ? 'rgba(74, 222, 128, 0.1)' : 'transparent'}
						style:border-color={statusFilter === status ? 'var(--accent-green)' : 'var(--border-subtle)'}
						style:color={statusFilter === status ? 'var(--accent-green)' : 'var(--text-secondary)'}
					>
						{status}
					</button>
				{/each}
			</div>
			<div class="flex items-center gap-2">
				<span class="text-xs uppercase tracking-wider" style="color: var(--text-secondary);">League:</span>
				<select
					bind:value={selectedLeague}
					class="px-3 py-1 text-xs font-medium border"
					style="background-color: var(--bg-surface); border-color: var(--border-subtle); border-radius: 0; color: var(--text-primary); font-family: var(--font-mono);"
				>
					{#each allLeagues as league}
						<option value={league} style="background: var(--bg-surface);">{league}</option>
					{/each}
				</select>
			</div>
			<div class="flex items-center gap-2 ml-auto">
				<span class="text-xs uppercase tracking-wider" style="color: var(--text-secondary);">Sort:</span>
				{#each [['time', 'Time'], ['momentum', 'Momentum'], ['score', 'Score']] as [value, label]}
					<button
						onclick={() => sortBy = value as 'time' | 'momentum' | 'score'}
						class="px-3 py-1 text-xs font-medium border transition-all duration-200"
						style="border-radius: 0; font-family: var(--font-mono);"
						style:background-color={sortBy === value ? 'rgba(74, 222, 128, 0.1)' : 'transparent'}
						style:border-color={sortBy === value ? 'var(--accent-green)' : 'var(--border-subtle)'}
						style:color={sortBy === value ? 'var(--accent-green)' : 'var(--text-secondary)'}
					>
						{label}
					</button>
					{/each}
				</div>
			</div>
		</Card>

		<!-- Match Grid -->
		{#if data.loading}
			<div class="flex justify-center py-12">
				<Loading />
			</div>
		{:else if filteredMatches().length === 0}
			<Card>
				<div class="p-12 text-center">
					<h3 class="text-lg font-semibold mb-2" style="color: var(--text-primary);">No matches found</h3>
					<p style="color: var(--text-secondary);">Try adjusting your filters</p>
				</div>
			</Card>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
				{#each filteredMatches() as match}
					<Card
						interactive
						class={match.status === 'live' ? 'card-glow-cyan-subtle' : ''}
						style={match.status === 'live'
							? `border-color: rgba(74, 222, 128, 0.3); box-shadow: 0 0 15px rgba(74, 222, 128, 0.05);`
							: ''}
					>
						<div class="p-4 space-y-4">
							<!-- Header: League + Status -->
							<div class="flex items-center justify-between">
								<Badge variant="info">{match.league}</Badge>
								<div class="flex items-center gap-2">
									{#if match.status === 'live'}
										<div class="relative">
											<div class="w-2 h-2 rounded-full" style="background: var(--accent-green);"></div>
											<div class="absolute inset-0 w-2 h-2 rounded-full animate-ping" style="background: var(--accent-green); opacity: 0.5;"></div>
										</div>
									{/if}
									<span class="text-xs font-mono font-bold" style="color: {match.status === 'live' ? 'var(--accent-green)' : 'var(--text-secondary)'};">
										{match.status === 'live' ? `LIVE ${formatMinute(match.minute)}` : getStatusBadge(match.status).label}
									</span>
								</div>
							</div>

							<!-- Scoreboard -->
							<div class="flex items-center justify-between py-2">
								<div class="flex-1 text-left">
									<div class="font-semibold text-sm font-sport" style="color: var(--accent-blue);">{match.home_team}</div>
									<div class="text-xs mt-1" style="color: var(--text-secondary);">Home</div>
								</div>
								<div class="text-center px-4">
									<div class="text-3xl font-bold font-mono tracking-wider" style="color: var(--text-primary);">
										{match.home_score ?? 0} - {match.away_score ?? 0}
									</div>
									{#if match.status === 'live'}
										<div class="text-xs font-mono mt-1" style="color: var(--accent-green);">{formatMinute(match.minute)}</div>
									{/if}
								</div>
								<div class="flex-1 text-right">
									<div class="font-semibold text-sm font-sport" style="color: var(--accent-blue);">{match.away_team}</div>
									<div class="text-xs mt-1" style="color: var(--text-secondary);">Away</div>
								</div>
							</div>

							<!-- Stats Bar -->
							<div class="space-y-2">
								<!-- Possession -->
								<div class="flex items-center gap-2">
									<span class="text-xs font-mono w-8" style="color: var(--accent-green);">{match.possession_home}%</span>
									<div class="flex-1 h-1.5 flex" style="background: var(--bg-elevated);">
										<div
											class="h-full transition-all duration-1000"
											style="width: {match.possession_home}%; background: var(--accent-green);"
										></div>
										<div
											class="h-full transition-all duration-1000"
											style="width: {match.possession_away}%; background: var(--accent-blue);"
										></div>
									</div>
									<span class="text-xs font-mono w-8 text-right" style="color: var(--accent-blue);">{match.possession_away}%</span>
								</div>

								<!-- Shots & xG -->
								<div class="flex justify-between text-xs font-mono">
									<div style="color: var(--accent-green);">Shots: {match.shots_home}</div>
									<div style="color: var(--text-secondary);">xG: {match.xg_home?.toFixed(2)} | {match.xg_away?.toFixed(2)}</div>
									<div style="color: var(--accent-blue);">Shots: {match.shots_away}</div>
								</div>
							</div>

								<!-- Momentum Indicator -->
								{#if match.status === 'live' && match.momentum !== 'neutral'}
									<div class="flex items-center gap-2 pt-2 border-t" style="border-color: var(--border-subtle);">
										<span class="text-xs uppercase tracking-wider" style="color: var(--text-secondary);">Momentum:</span>
										<div class="flex items-center gap-1">
											{#if match.momentum === 'home'}
												<span class="text-lg">◄</span>
												<div class="h-1" style="width: 60px; background: linear-gradient(90deg, var(--accent-green), transparent);"></div>
											{:else}
												<div class="h-1" style="width: 60px; background: linear-gradient(90deg, transparent, var(--accent-blue));"></div>
												<span class="text-lg">▶</span>
											{/if}
											<span class="text-xs font-mono capitalize" style="color: var(--accent-green);">{match.momentum_intensity || 'neutral'}</span>
										</div>
									</div>
								{/if}

								<!-- Odds -->
								{#if match.odds && match.odds.length > 0}
									<div class="grid grid-cols-3 gap-2 pt-2 border-t" style="border-color: var(--border-subtle);">
										<div class="text-center">
											<div class="text-xs" style="color: var(--text-secondary);">1</div>
											<div class="font-mono font-bold text-sm" style="color: var(--accent-green);">{match.odds[0].home_odds.toFixed(2)}</div>
										</div>
										<div class="text-center">
											<div class="text-xs" style="color: var(--text-secondary);">X</div>
											<div class="font-mono font-bold text-sm" style="color: var(--text-primary);">{match.odds[0].draw_odds?.toFixed(2) ?? '-'}</div>
										</div>
										<div class="text-center">
											<div class="text-xs" style="color: var(--text-secondary);">2</div>
											<div class="font-mono font-bold text-sm" style="color: var(--accent-blue);">{match.odds[0].away_odds.toFixed(2)}</div>
										</div>
									</div>
								{/if}

								<!-- Action -->
								{#if match.status === 'live'}
									<Button variant="primary" class="w-full text-xs mt-2">BET NOW</Button>
								{/if}
							</div>
						</Card>
					{/each}
				</div>
			{/if}
		</div>
