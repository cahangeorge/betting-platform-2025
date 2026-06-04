<script lang="ts">
	import type { PageData } from './$types';
	import Card from '$lib/components/ui/Card.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Loading from '$lib/components/Loading.svelte';
	import OddsMovement from '$lib/components/OddsMovement.svelte';

	let { data }: { data: PageData } = $props();

	let minEdge = $state(2);
	let selectedLeagues = $state<string[]>([]);
	let selectedMarket = $state<'1X2' | 'OU' | 'BTTS'>('1X2');
	let sortBy = $state<'edge' | 'time' | 'odds'>('edge');

	const allLeagues = ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1'];

	const filteredBets = $derived(() => {
		if (!data.valueBets) return [];
		let bets = data.valueBets.filter(b => b.edge >= minEdge);
		if (selectedLeagues.length > 0) {
			bets = bets.filter(b => selectedLeagues.includes(b.league));
		}
		if (selectedMarket !== '1X2') {
			bets = bets.filter(b => b.market === selectedMarket);
		}
		bets.sort((a, b) => {
			if (sortBy === 'edge') return b.edge - a.edge;
			if (sortBy === 'time') return new Date(a.kickoff).getTime() - new Date(b.kickoff).getTime();
			return a.odds - b.odds;
		});
		return bets;
	});

	const stats = $derived(() => {
		const bets = filteredBets();
		if (bets.length === 0) return { total: 0, avgEdge: 0, bestEdge: 0, avgOdds: 0 };
		const edges = bets.map(b => b.edge);
		const odds = bets.map(b => b.odds);
		return {
			total: bets.length,
			avgEdge: edges.reduce((a, b) => a + b, 0) / edges.length,
			bestEdge: Math.max(...edges),
			avgOdds: odds.reduce((a, b) => a + b, 0) / odds.length
		};
	});

	function toggleLeague(league: string) {
		if (selectedLeagues.includes(league)) {
			selectedLeagues = selectedLeagues.filter(l => l !== league);
		} else {
			selectedLeagues = [...selectedLeagues, league];
		}
	}

	function formatEdge(edge: number): string {
		const sign = edge > 0 ? '+' : '';
		return `${sign}${edge.toFixed(1)}%`;
	}

	function formatEV(edge: number, odds: number, stake = 10): string {
		const ev = stake * ((edge / 100) * odds);
		const sign = ev >= 0 ? '+' : '';
		return `${sign}£${ev.toFixed(2)}`;
	}

	function kellyStake(edge: number, odds: number, bankroll = 10000): number {
		const p = (edge / 100) + (1 / odds);
		const q = 1 - p;
		const fraction = (p * odds - 1) / (odds - 1);
		return Math.max(0, bankroll * fraction * 0.25); // Quarter Kelly
	}

	function timeUntil(kickoff: string): string {
		const now = new Date();
		const kick = new Date(kickoff);
		const diff = kick.getTime() - now.getTime();
		if (diff <= 0) return 'LIVE';
		const hours = Math.floor(diff / (1000 * 60 * 60));
		const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
		if (hours > 0) return `${hours}h ${mins}m`;
		return `${mins}m`;
	}
</script>

<svelte:head>
	<title>Value Bet Feed | Stadium Intel</title>
	<meta name="description" content="Edge opportunities detected by your predictive models" />
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="border-b pb-4" style="border-color: var(--border-subtle);">
		<div class="flex items-center gap-3 mb-2">
			<div class="w-1 h-8" style="background: var(--accent-green);"></div>
			<h1 class="text-2xl font-extrabold tracking-tight font-sport" style="color: var(--text-primary);">VALUE BET FEED</h1>
		</div>
		<p style="color: var(--text-secondary);">Edge opportunities detected by your predictive models</p>
	</div>

	<!-- Filters -->
	<Card>
		<div class="p-4 space-y-4">
			<div class="flex flex-wrap items-center gap-4">
				<!-- Min Edge -->
				<div class="space-y-1">
					<label class="text-xs font-medium uppercase tracking-wider" style="color: var(--text-secondary);">Min Edge</label>
					<div class="flex items-center gap-2">
						<input
							type="range"
							min="0"
							max="20"
							step="0.5"
							bind:value={minEdge}
							class="w-32 accent-green"
							style="accent-color: var(--accent-green);"
						/>
						<span class="text-sm font-mono font-bold" style="color: var(--accent-green); min-width: 3rem;">{minEdge}%</span>
					</div>
				</div>

				<!-- Leagues -->
				<div class="space-y-1">
					<label class="text-xs font-medium uppercase tracking-wider" style="color: var(--text-secondary);">Leagues</label>
					<div class="flex flex-wrap gap-2">
						{#each allLeagues as league}
							<button
								onclick={() => toggleLeague(league)}
								class="px-3 py-1 text-xs font-medium border transition-all duration-200"
								style="border-radius: 9999px; font-family: var(--font-mono);"
								style:background-color={selectedLeagues.includes(league) ? 'rgba(74, 222, 128, 0.1)' : 'transparent'}
								style:border-color={selectedLeagues.includes(league) ? 'var(--accent-green)' : 'var(--border-subtle)'}
								style:color={selectedLeagues.includes(league) ? 'var(--accent-green)' : 'var(--text-secondary)'}
							>
								{league}
							</button>
						{/each}
					</div>
				</div>

				<!-- Market -->
				<div class="space-y-1">
					<label class="text-xs font-medium uppercase tracking-wider" style="color: var(--text-secondary);">Market</label>
					<div class="flex gap-1">
						{#each [['1X2', '1X2'], ['OU', 'O/U'], ['BTTS', 'BTTS']] as [value, label]}
							<button
								onclick={() => selectedMarket = value as '1X2' | 'OU' | 'BTTS'}
								class="px-3 py-1 text-xs font-medium border transition-all duration-200"
								style="border-radius: 9999px; font-family: var(--font-mono);"
								style:background-color={selectedMarket === value ? 'rgba(74, 222, 128, 0.1)' : 'transparent'}
								style:border-color={selectedMarket === value ? 'var(--accent-green)' : 'var(--border-subtle)'}
								style:color={selectedMarket === value ? 'var(--accent-green)' : 'var(--text-secondary)'}
							>
								{label}
							</button>
						{/each}
					</div>
				</div>

				<!-- Sort -->
				<div class="space-y-1">
					<label class="text-xs font-medium uppercase tracking-wider" style="color: var(--text-secondary);">Sort</label>
					<select
						bind:value={sortBy}
						class="px-3 py-1 text-xs font-medium border"
						style="background-color: var(--bg-surface); border-color: var(--border-subtle); border-radius: 0; color: var(--text-primary); font-family: var(--font-mono);"
					>
						<option value="edge" style="background: var(--bg-surface);">Edge %</option>
						<option value="time" style="background: var(--bg-surface);">Kickoff</option>
						<option value="odds" style="background: var(--bg-surface);">Odds</option>
					</select>
				</div>
			</div>
		</div>
	</Card>

	<!-- Stats Row -->
	<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
		<Card>
			<div class="p-4 text-center">
				<div class="text-xs uppercase tracking-wider mb-1" style="color: var(--text-secondary);">Total Bets</div>
				<div class="text-2xl font-bold font-mono" style="color: var(--accent-green);">{stats().total}</div>
			</div>
		</Card>
		<Card>
			<div class="p-4 text-center">
				<div class="text-xs uppercase tracking-wider mb-1" style="color: var(--text-secondary);">Avg Edge</div>
				<div class="text-2xl font-bold font-mono" style="color: var(--accent-green);">{stats().avgEdge.toFixed(1)}%</div>
			</div>
		</Card>
		<Card>
			<div class="p-4 text-center">
				<div class="text-xs uppercase tracking-wider mb-1" style="color: var(--text-secondary);">Best Edge</div>
				<div class="text-2xl font-bold font-mono" style="color: var(--accent-green);">{stats().bestEdge.toFixed(1)}%</div>
			</div>
		</Card>
		<Card>
			<div class="p-4 text-center">
				<div class="text-xs uppercase tracking-wider mb-1" style="color: var(--text-secondary);">Avg Odds</div>
				<div class="text-2xl font-bold font-mono" style="color: var(--accent-blue);">{stats().avgOdds.toFixed(2)}</div>
			</div>
		</Card>
	</div>

	<!-- Value Bet List -->
	{#if data.loading}
		<div class="flex justify-center py-12">
			<Loading />
		</div>
	{:else if filteredBets().length === 0}
		<Card>
			<div class="p-12 text-center">
				<h3 class="text-lg font-semibold mb-2" style="color: var(--text-primary);">No value bets match your criteria</h3>
				<p style="color: var(--text-secondary);">Try lowering the minimum edge or selecting more leagues</p>
			</div>
		</Card>
	{:else}
		<div class="space-y-3">
			{#each filteredBets() as bet}
				<Card interactive>
					<div class="p-4">
						<div class="flex flex-wrap items-center justify-between gap-4">
							<!-- Match Info -->
							<div class="flex-1 min-w-[200px]">
								<div class="flex items-center gap-2 mb-2">
									<Badge variant="info">{bet.league}</Badge>
									<span class="text-xs font-mono" style="color: var(--text-secondary);">{timeUntil(bet.kickoff)}</span>
								</div>
								<div class="font-semibold font-sport" style="color: var(--text-primary);">
									<span style="color: var(--accent-blue);">{bet.home_team}</span>
									<span class="mx-2" style="color: var(--text-secondary);">vs</span>
									<span style="color: var(--accent-blue);">{bet.away_team}</span>
								</div>
							</div>

							<!-- Selection -->
							<div class="text-center min-w-[120px]">
								<div class="text-xs uppercase tracking-wider mb-1" style="color: var(--text-secondary);">{bet.market}</div>
								<div class="font-bold font-mono text-lg" style="color: var(--accent-green);">{bet.selection}</div>
							</div>

							<!-- Probabilities -->
							<div class="text-center min-w-[100px]">
								<div class="text-xs uppercase tracking-wider mb-1" style="color: var(--text-secondary);">Model</div>
								<div class="font-mono font-bold" style="color: var(--text-primary);">{(bet.model_prob * 100).toFixed(1)}%</div>
								<div class="w-full h-1 mt-1" style="background: var(--bg-elevated);">
									<div
										class="h-full transition-all duration-500"
										style="width: {bet.model_prob * 100}%; background: linear-gradient(90deg, var(--accent-green), var(--accent-blue));"
									></div>
								</div>
							</div>

							<!-- Odds -->
							<div class="text-center min-w-[80px]">
								<div class="text-xs uppercase tracking-wider mb-1" style="color: var(--text-secondary);">Odds</div>
								<div class="font-mono font-bold text-lg" style="color: var(--accent-blue);">{bet.odds.toFixed(2)}</div>
								<div class="text-xs font-mono" style="color: var(--text-muted);">
									Implied: {(100 / bet.odds).toFixed(1)}%
								</div>
							</div>

							<!-- Edge -->
							<div class="min-w-[100px]">
								<div class="text-xs uppercase tracking-wider mb-1" style="color: var(--text-secondary);">Edge</div>
								<div
									class="font-mono font-bold text-lg"
									style="color: {bet.edge > 0 ? 'var(--accent-green)' : 'var(--danger)'}"
								>
									{formatEdge(bet.edge)}
								</div>
								<div class="w-full h-2 mt-1" style="background: var(--bg-elevated);">
									<div
										class="h-full transition-all duration-500"
										style="width: {Math.min(Math.abs(bet.edge) * 3, 100)}%; background: {bet.edge > 0 ? 'var(--accent-green)' : 'var(--danger)'}"
									></div>
								</div>
							</div>

							<!-- EV & Kelly -->
							<div class="text-right min-w-[120px]">
								<div class="text-xs font-mono mb-1" style="color: var(--accent-green);">
									EV {formatEV(bet.edge, bet.odds)}
								</div>
								<div class="text-xs font-mono mb-2" style="color: var(--text-muted);">
									Kelly: £{kellyStake(bet.edge, bet.odds).toFixed(0)}
								</div>
								<Button variant="primary" class="w-full text-xs">ADD TO SLIP</Button>
							</div>
						</div>
					</div>
				</Card>
			{/each}
		</div>
	{/if}
</div>
