<script lang="ts">
	import { matchesApi } from '$lib/api/matches';
	import { ApiClientError } from '$lib/api/client';
	import type { Match } from '$lib/types';
	import Ticker from '$lib/components/Ticker.svelte';
	import MatchCard from '$lib/components/MatchCard.svelte';
	import MatchCardSkeleton from '$lib/components/MatchCardSkeleton.svelte';
	import OddsTable from '$lib/components/OddsTable.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Loading from '$lib/components/Loading.svelte';
	import Tabs from '$lib/components/ui/Tabs.svelte';
	import { RefreshCw } from 'lucide-svelte';
	import { fade } from 'svelte/transition';

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

<div class="space-y-4" transition:fade={{ duration: 200 }}>
	<div>
		<h1 class="text-2xl font-extrabold font-sport text-foreground">ODDS BOARD</h1>
		<p class="mt-1 text-muted-foreground">Live odds ticker and match board</p>
	</div>

	<Ticker matches={upcomingMatches} />

	<div class="flex items-center justify-between">
		<Tabs bind:activeTab {tabs} />

		<div class="flex items-center space-x-2">
			{#if loading}
				<div
					class="w-4 h-4  animate-spin border-2 border-border border-t-football-green"
				></div>
			{/if}
			<Button onclick={refresh} variant="ghost" size="sm">
				<RefreshCw class="w-3.5 h-3.5 mr-1.5" />
				Refresh
			</Button>
		</div>
	</div>

	{#if error}
		<div class="p-3 text-sm border bg-destructive/10 border-destructive/30 text-destructive ">{error}</div>
	{/if}

	{#if activeTab === 'grid'}
		{#if loading && matches.length === 0}
			<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
				{#each Array(6) as _}
					<MatchCardSkeleton />
				{/each}
			</div>
		{:else if upcomingMatches.length === 0}
			<div class="text-center py-12 text-muted-foreground">
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
