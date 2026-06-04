<script lang="ts">
	import { matchesApi } from '$lib/api/matches';
	import { ApiClientError } from '$lib/api/client';
	import type { Match } from '$lib/types';
	import Ticker from '$lib/components/Ticker.svelte';
	import MatchCard from '$lib/components/MatchCard.svelte';
	import OddsTable from '$lib/components/OddsTable.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Loading from '$lib/components/Loading.svelte';
	import Tabs from '$lib/components/ui/Tabs.svelte';
	import { RefreshCw } from 'lucide-svelte';

	let {
		data
	}: {
		data: {
			matches: Match[];
		};
	} = $props();

	const initialMatches = data.matches;
	let matches = $state<Match[]>(initialMatches);
	let loading = $state(false);
	let error = $state('');
	let activeTab = $state('grid');
	let pollInterval = $state<ReturnType<typeof setInterval> | null>(null);

	async function refresh() {
		loading = true;
		try {
			matches = await matchesApi.getMatches();
		} catch (err) {
			error = err instanceof ApiClientError ? err.message : 'Failed to refresh';
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		pollInterval = setInterval(refresh, 10000);
		return () => {
			if (pollInterval) clearInterval(pollInterval);
		};
	});

	const upcomingMatches = $derived(
		matches.filter((m) => m.status === 'scheduled' || m.status === 'live')
	);

	const tabs = [
		{ id: 'grid', label: 'Match Grid' },
		{ id: 'table', label: 'Odds Table' }
	];
</script>

<div class="space-y-4">
	<div>
		<h1 class="text-2xl font-extrabold font-sport" style="color: var(--text-primary);">ODDS BOARD</h1>
		<p class="mt-1" style="color: var(--text-secondary);">Live odds ticker and match board</p>
	</div>

	<Ticker matches={upcomingMatches} />

	<div class="flex items-center justify-between">
		<Tabs bind:activeTab {tabs} />

		<div class="flex items-center space-x-2">
			{#if loading}
				<div
					class="w-4 h-4 rounded-full animate-spin"
					style="border: 2px solid var(--border-subtle); border-top-color: var(--accent-green);"
				></div>
			{/if}
			<Button onclick={refresh} variant="ghost" size="sm">
				<RefreshCw class="w-3.5 h-3.5 mr-1.5" />
				Refresh
			</Button>
		</div>
	</div>

	{#if error}
		<div class="p-3 text-sm border" style="background-color: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3); color: var(--danger); border-radius: 0;">{error}</div>
	{/if}

	{#if activeTab === 'grid'}
		{#if upcomingMatches.length === 0}
			<div class="text-center py-12" style="color: var(--text-secondary);">
				<p class="text-lg">No matches available</p>
				<p class="text-sm mt-1">Check back later for upcoming fixtures</p>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
				{#each upcomingMatches as match (match.id)}
					<MatchCard {match} />
				{/each}
			</div>
		{/if}
	{:else}
		<OddsTable matches={upcomingMatches} />
	{/if}
</div>
