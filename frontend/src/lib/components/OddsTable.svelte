<script lang="ts">
	import type { Match } from '$lib/types';
	import Badge from './ui/Badge.svelte';

	let {
		matches
	}: {
		matches: Match[];
	} = $props();

	let selectedLeague = $state('all');

	const leagues = $derived([...new Set(matches.map((m) => m.league))]);

	const filteredMatches = $derived(
		selectedLeague === 'all'
			? matches
			: matches.filter((m) => m.league === selectedLeague)
	);

	const bookmakers = $derived(
		matches.length > 0
			? [...new Set(matches.flatMap((m) => m.odds.map((o) => o.bookmaker)))]
			: []
	);
</script>

<div class="space-y-4">
	<div class="flex items-center space-x-3 overflow-x-auto pb-2">
		<button
			class="px-3 py-1.5 text-xs font-medium transition-all duration-200 ease-out"
			style={selectedLeague === 'all'
				? 'background-color: rgba(74, 222, 128, 0.1); color: var(--accent-green); border: 1px solid rgba(74, 222, 128, 0.3); border-radius: 0;'
				: 'background-color: var(--bg-elevated); color: var(--text-secondary); border: 1px solid var(--border-subtle); border-radius: 0;'}
			onclick={() => (selectedLeague = 'all')}
		>
			All Leagues
		</button>
		{#each leagues as league (league)}
			<button
				class="px-3 py-1.5 text-xs font-medium transition-all duration-200 ease-out whitespace-nowrap"
				style={selectedLeague === league
					? 'background-color: rgba(74, 222, 128, 0.1); color: var(--accent-green); border: 1px solid rgba(74, 222, 128, 0.3); border-radius: 0;'
					: 'background-color: var(--bg-elevated); color: var(--text-secondary); border: 1px solid var(--border-subtle); border-radius: 0;'}
				onclick={() => (selectedLeague = league)}
			>
				{league}
			</button>
		{/each}
	</div>

	<div class="overflow-x-auto border" style="border-color: var(--border-subtle); border-radius: 0;">
		<table class="w-full text-sm">
			<thead>
				<tr style="background-color: var(--bg-elevated);">
					<th class="px-3 py-3 text-left text-xs uppercase tracking-wider" style="color: var(--text-secondary); font-family: var(--font-body);">Match</th>
					<th class="px-3 py-3 text-left text-xs uppercase tracking-wider" style="color: var(--text-secondary); font-family: var(--font-body);">League</th>
					<th class="px-3 py-3 text-center text-xs uppercase tracking-wider" style="color: var(--text-secondary); font-family: var(--font-body);">Date</th>
					{#each bookmakers as bm (bm)}
						<th class="px-3 py-3 text-center text-xs uppercase tracking-wider" colspan="3" style="color: var(--text-secondary); font-family: var(--font-body);">
							{bm}
						</th>
					{/each}
					<th class="px-3 py-3 text-center text-xs uppercase tracking-wider" colspan="3" style="color: var(--accent-green); font-family: var(--font-body);">
						Best
					</th>
				</tr>
					{#if bookmakers.length > 0}
						<tr class="text-xs" style="color: var(--text-secondary); background-color: var(--bg-surface);">
							<th colspan="3"></th>
							{#each bookmakers as bm (bm)}
								<th class="px-1 py-1 text-center font-normal font-mono">1</th>
								<th class="px-1 py-1 text-center font-normal font-mono">X</th>
								<th class="px-1 py-1 text-center font-normal font-mono">2</th>
							{/each}
							<th class="px-1 py-1 text-center font-normal font-mono" style="color: var(--accent-green);">1</th>
							<th class="px-1 py-1 text-center font-normal font-mono" style="color: var(--accent-gold);">X</th>
							<th class="px-1 py-1 text-center font-normal font-mono" style="color: var(--accent-blue);">2</th>
						</tr>
					{/if}
			</thead>
			<tbody>
				{#each filteredMatches as match (match.id)}
					<tr class="transition-colors duration-200 odds-row" style="border-bottom: 1px solid var(--border-subtle);">
						<td class="px-3 py-3">
							<div style="color: var(--text-primary); font-weight: 500; font-family: var(--font-sport);">{match.home_team}</div>
							<div style="color: var(--text-secondary);">{match.away_team}</div>
						</td>
						<td class="px-3 py-3 text-xs font-mono" style="color: var(--text-secondary);">{match.league}</td>
						<td class="px-3 py-3 text-xs text-center font-mono" style="color: var(--text-secondary);">
							{new Date(match.start_time).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
						</td>
						{#each bookmakers as bm (bm)}
							{@const odds = match.odds.find((o) => o.bookmaker === bm)}
							{@const maxHome = Math.max(...match.odds.map((o) => o.home_odds), 0)}
							{@const maxAway = Math.max(...match.odds.map((o) => o.away_odds), 0)}
							<td class="px-3 py-3 text-center font-mono text-sm" style={odds && odds.home_odds === maxHome ? 'color: var(--accent-green); font-weight: 600;' : 'color: var(--text-primary);'}>
								{odds ? odds.home_odds.toFixed(2) : '-'}
							</td>
							<td class="px-3 py-3 text-center font-mono text-sm" style="color: var(--text-secondary);">
								{odds && odds.draw_odds ? odds.draw_odds.toFixed(2) : '-'}
							</td>
							<td class="px-3 py-3 text-center font-mono text-sm" style={odds && odds.away_odds === maxAway ? 'color: var(--accent-blue); font-weight: 600;' : 'color: var(--text-primary);'}>
								{odds ? odds.away_odds.toFixed(2) : '-'}
							</td>
						{/each}
						<td class="px-3 py-3 text-center font-mono font-bold" style="color: var(--accent-green);">
							{Math.max(...match.odds.map(o => o.home_odds), 0) > 0 ? Math.max(...match.odds.map(o => o.home_odds), 0).toFixed(2) : '-'}
						</td>
						<td class="px-3 py-3 text-center font-mono font-bold" style="color: var(--accent-gold);">
							{Math.max(...match.odds.filter(o => o.draw_odds).map(o => o.draw_odds as number), 0) > 0 ? Math.max(...match.odds.filter(o => o.draw_odds).map(o => o.draw_odds as number), 0).toFixed(2) : '-'}
						</td>
						<td class="px-3 py-3 text-center font-mono font-bold" style="color: var(--accent-blue);">
							{Math.max(...match.odds.map(o => o.away_odds), 0) > 0 ? Math.max(...match.odds.map(o => o.away_odds), 0).toFixed(2) : '-'}
						</td>
					</tr>
				{:else}
					<tr>
						<td colspan={3 + bookmakers.length * 3 + 3} class="px-4 py-12 text-center" style="color: var(--text-secondary);">
							No matches available
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>

<style>
	.odds-row:hover {
		background-color: var(--bg-elevated);
	}
</style>
