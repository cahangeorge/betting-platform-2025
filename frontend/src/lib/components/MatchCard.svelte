<script lang="ts">
	import type { Match } from '$lib/types';
	import Badge from './ui/Badge.svelte';

	let {
		match
	}: {
		match: Match;
	} = $props();

	const bestHomeOdds = $derived(
		match.odds.length > 0 ? Math.max(...match.odds.map((o) => o.home_odds)) : 0
	);
	const bestDrawOdds = $derived(
		match.odds.length > 0 ? Math.max(...match.odds.map((o) => o.draw_odds ?? 0)) : 0
	);
	const bestAwayOdds = $derived(
		match.odds.length > 0 ? Math.max(...match.odds.map((o) => o.away_odds)) : 0
	);

	const bestBookmaker = $derived(
		match.odds.length > 0
			? match.odds.reduce((a, b) => (a.home_odds > b.home_odds ? a : b)).bookmaker
			: ''
	);

	const matchDate = $derived(new Date(match.start_time).toLocaleDateString('en-GB', {
		weekday: 'short',
		day: 'numeric',
		month: 'short',
		hour: '2-digit',
		minute: '2-digit'
	}));

	const statusVariant: Record<string, 'live' | 'success' | 'warning' | 'danger' | 'info'> = {
		scheduled: 'info',
		live: 'live',
		finished: 'success',
		postponed: 'warning',
		cancelled: 'danger'
	};

	const statusBorder: Record<string, string> = {
		scheduled: 'var(--accent-blue)',
		live: 'var(--accent-green)',
		finished: 'var(--border-subtle)',
		postponed: 'var(--accent-gold)',
		cancelled: 'var(--danger)'
	};
</script>

<div class="card p-4 card-interactive" style="border-top: 2px solid {statusBorder[match.status] || 'var(--border-subtle)'};">
	<div class="flex items-center justify-between mb-3">
		<div class="flex items-center space-x-2">
			<span class="text-xs font-mono" style="color: var(--text-secondary);">{match.league}</span>
			<Badge variant={statusVariant[match.status] || 'default'}>{match.status}</Badge>
			{#if match.status === 'live'}
				<span class="relative flex h-2 w-2">
					<span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" style="background-color: var(--accent-green);"></span>
					<span class="relative inline-flex rounded-full h-2 w-2" style="background-color: var(--accent-green);"></span>
				</span>
			{/if}
		</div>
		<span class="text-xs font-mono" style="color: var(--text-muted);">{matchDate}</span>
	</div>

	<div class="space-y-2">
		<div class="flex items-center justify-between">
			<div class="flex items-center space-x-2">
				<div
					class="w-6 h-6 flex items-center justify-center text-[10px] font-bold"
					style="background-color: var(--bg-elevated); color: var(--accent-green); border: 1px solid var(--border-subtle); border-radius: 0;"
				>
					H
				</div>
				<span class="text-sm font-medium font-sport" style="color: var(--text-primary);">{match.home_team}</span>
			</div>
			{#if match.home_score !== null}
				<span class="text-lg font-bold font-mono" style="color: var(--text-primary);">{match.home_score}</span>
			{/if}
			<div class="flex items-center space-x-1">
				{#if bestHomeOdds > 0}
					<span
						class="text-sm font-mono font-semibold px-2 py-0.5"
						style="background-color: rgba(74, 222, 128, 0.1); color: var(--accent-green); border: 1px solid rgba(74, 222, 128, 0.2); border-radius: 0; font-family: 'JetBrains Mono', monospace;"
					>
						{bestHomeOdds.toFixed(2)}
					</span>
				{/if}
			</div>
		</div>

		<div class="flex items-center justify-between">
			<div class="flex items-center space-x-2">
				<div
					class="w-6 h-6 flex items-center justify-center text-[10px] font-bold"
					style="background-color: var(--bg-elevated); color: var(--accent-blue); border: 1px solid var(--border-subtle); border-radius: 0;"
				>
					A
				</div>
				<span class="text-sm font-medium font-sport" style="color: var(--text-primary);">{match.away_team}</span>
			</div>
			{#if match.away_score !== null}
				<span class="text-lg font-bold font-mono" style="color: var(--text-primary);">{match.away_score}</span>
			{/if}
			<div class="flex items-center space-x-1">
				{#if bestAwayOdds > 0}
					<span
						class="text-sm font-mono font-semibold px-2 py-0.5"
						style="background-color: rgba(56, 189, 248, 0.1); color: var(--accent-blue); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 0; font-family: 'JetBrains Mono', monospace;"
					>
						{bestAwayOdds.toFixed(2)}
					</span>
				{/if}
			</div>
		</div>

		{#if match.odds.length > 1}
			<div class="pt-2 border-t" style="border-color: var(--border-subtle);">
				<p class="text-xs font-mono" style="color: var(--text-muted);">Best odds from <span style="color: var(--accent-green);">{bestBookmaker}</span></p>
			</div>
		{/if}
	</div>
</div>
