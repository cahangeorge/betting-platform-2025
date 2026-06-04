<script lang="ts">
	import { ticketsApi } from '$lib/api/tickets';
	import { matchesApi } from '$lib/api/matches';
	import { ApiClientError } from '$lib/api/client';
	import type { Ticket, Match, PlaceBetRequest, TicketType } from '$lib/types';
	import Button from './ui/Button.svelte';
	import Card from './ui/Card.svelte';
	import Tabs from './ui/Tabs.svelte';
	import Select from './ui/Select.svelte';
	import Input from './ui/Input.svelte';
	import Badge from './ui/Badge.svelte';
	import Loading from './Loading.svelte';

	let tickets = $state<Ticket[]>([]);
	let matches = $state<Match[]>([]);
	let loading = $state(true);
	let error = $state('');
	let activeTab = $state('active');
	let pollInterval = $state<ReturnType<typeof setInterval> | null>(null);

	// Place bet form
	let betMatchId = $state('');
	let betMarket = $state('1x2');
	let betSelection = $state('home');
	let betOdds = $state('2.00');
	let betStake = $state('10');
	let betType = $state<TicketType>('single');
	let betError = $state('');
	let betSubmitting = $state(false);
	let showPlaceBet = $state(false);

	// Stats
	let stats = $state({ total: 0, won: 0, lost: 0, profit_loss: 0 });

	const statusBadge: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
		won: 'success',
		open: 'info',
		lost: 'danger',
		cashed_out: 'warning',
		void: 'default'
	};

	async function loadTickets() {
		try {
			const [t, m, s] = await Promise.all([
				ticketsApi.getTickets(),
				matchesApi.getMatches({ status: 'scheduled' }),
				ticketsApi.getStats()
			]);
			tickets = t;
			matches = m;
			stats = s;
		} catch (err) {
			error = err instanceof ApiClientError ? err.message : 'Failed to load tickets';
		} finally {
			loading = false;
		}
	}

	async function placeBet() {
		if (!betMatchId || !betStake) {
			betError = 'Select a match and enter a stake';
			return;
		}
		betSubmitting = true;
		betError = '';
		try {
			const req: PlaceBetRequest = {
				legs: [{
					match_id: parseInt(betMatchId),
					market: betMarket,
					selection: betSelection,
					odds: parseFloat(betOdds)
				}],
				stake: parseFloat(betStake),
				type: betType,
				bankroll_id: 1
			};
			const ticket = await ticketsApi.placeBet(req);
			tickets = [...tickets, ticket];
			showPlaceBet = false;
			activeTab = 'active';
		} catch (err) {
			betError = err instanceof ApiClientError ? err.message : 'Failed to place bet';
		} finally {
			betSubmitting = false;
		}
	}

	$effect(() => {
		loadTickets();
		pollInterval = setInterval(loadTickets, 5000);
		return () => {
			if (pollInterval) clearInterval(pollInterval);
		};
	});

	const activeTickets = $derived(tickets.filter((t) => t.status === 'open'));

	const tabs = $derived([
		{ id: 'active', label: 'Active', count: activeTickets.length },
		{ id: 'history', label: 'History', count: tickets.length },
		{ id: 'place', label: 'Place Bet' }
	]);

	const matchOptions = $derived(
		matches.map((m) => ({ value: String(m.id), label: `${m.home_team} vs ${m.away_team}` }))
	);
</script>

<div class="space-y-6">
	{#if loading && tickets.length === 0}
		<Loading message="Loading tickets..." />
	{:else if error}
		<div class="p-4 border text-sm" style="background-color: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3); color: var(--danger); border-radius: 0;">{error}</div>
		<Button onclick={loadTickets}>Retry</Button>
	{:else}
		<!-- Stats row -->
		<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
			<Card>
				<p class="text-xs uppercase tracking-wider" style="color: var(--text-muted);">Total Bets</p>
				<p class="text-2xl font-bold font-mono" style="color: var(--text-primary);">{stats.total}</p>
			</Card>
			<Card>
				<p class="text-xs uppercase tracking-wider" style="color: var(--text-muted);">Won</p>
				<p class="text-2xl font-bold font-mono" style="color: var(--accent-green);">{stats.won}</p>
			</Card>
			<Card>
				<p class="text-xs uppercase tracking-wider" style="color: var(--text-muted);">Lost</p>
				<p class="text-2xl font-bold font-mono" style="color: var(--danger);">{stats.lost}</p>
			</Card>
			<Card>
				<p class="text-xs uppercase tracking-wider" style="color: var(--text-muted);">P/L</p>
				<p class="text-2xl font-bold font-mono" style="color: {stats.profit_loss >= 0 ? 'var(--accent-green)' : 'var(--danger)'};">{stats.profit_loss > 0 ? '+' : ''}{stats.profit_loss.toFixed(2)}</p>
			</Card>
		</div>

		<Tabs bind:activeTab {tabs}>
			{#if activeTab === 'active'}
				{#if activeTickets.length === 0}
					<div class="text-center py-12" style="color: var(--text-muted);">
						<p>No active tickets</p>
						<Button variant="secondary" class="mt-4" onclick={() => (activeTab = 'place')}>Place a Bet</Button>
					</div>
				{:else}
					<div class="space-y-4">
						{#each activeTickets as ticket (ticket.id)}
							<div class="card p-4" style="border-left: 3px solid var(--accent-green);">
								<div class="flex items-center justify-between mb-3">
									<div class="flex items-center space-x-3">
										<span class="text-sm font-mono" style="color: var(--text-muted);">#{ticket.reference}</span>
										<Badge variant="info">{ticket.type}</Badge>
										<Badge variant="warning">open</Badge>
									</div>
									<span class="text-xs" style="color: var(--text-muted);">{new Date(ticket.created_at).toLocaleString()}</span>
								</div>

								<div class="grid grid-cols-3 gap-4 mb-3">
									<div>
										<p class="text-xs" style="color: var(--text-muted);">Stake</p>
										<p class="text-sm font-medium font-mono" style="color: var(--text-primary);">{ticket.stake.toFixed(2)}</p>
									</div>
									<div>
										<p class="text-xs" style="color: var(--text-muted);">Odds</p>
										<p class="text-sm font-medium font-mono" style="color: var(--accent-green);">x{ticket.total_odds.toFixed(2)}</p>
									</div>
									<div>
										<p class="text-xs" style="color: var(--text-muted);">Potential Return</p>
										<p class="text-sm font-medium font-mono" style="color: var(--text-primary);">{ticket.potential_return.toFixed(2)}</p>
									</div>
								</div>

								<div class="space-y-1">
									{#each ticket.legs as leg (leg.id)}
										<div class="flex items-center space-x-2 text-xs" style="color: var(--text-muted);">
											<span>{leg.match?.home_team ?? 'Match'} vs {leg.match?.away_team ?? '?'}</span>
											<span style="color: var(--border-subtle);">|</span>
											<span>{leg.market}</span>
											<span style="color: var(--border-subtle);">|</span>
											<span>{leg.selection} @ {leg.odds.toFixed(2)}</span>
										</div>
									{/each}
								</div>
							</div>
						{/each}
					</div>
				{/if}

			{:else if activeTab === 'history'}
				{#if tickets.length === 0}
					<p class="text-center py-12" style="color: var(--text-muted);">No ticket history</p>
				{:else}
					<div class="overflow-x-auto">
						<table class="w-full text-sm">
							<thead class="text-xs uppercase" style="background-color: var(--bg-surface); border-bottom: 1px solid var(--border-subtle); color: var(--text-secondary); font-family: var(--font-body);">
								<tr>
									<th class="px-4 py-3 text-left">Reference</th>
									<th class="px-4 py-3 text-left">Type</th>
									<th class="px-4 py-3 text-left">Status</th>
									<th class="px-4 py-3 text-right">Stake</th>
									<th class="px-4 py-3 text-right">Odds</th>
									<th class="px-4 py-3 text-right">Return</th>
									<th class="px-4 py-3 text-left">Date</th>
								</tr>
							</thead>
							<tbody>
								{#each tickets as ticket (ticket.id)}
									<tr class="transition-colors duration-200" style="border-bottom: 1px solid var(--border-subtle);">
										<td class="px-4 py-3 font-mono" style="color: var(--text-muted);">#{ticket.reference}</td>
										<td class="px-4 py-3">
											<Badge>{ticket.type}</Badge>
										</td>
										<td class="px-4 py-3">
											<Badge variant={statusBadge[ticket.status] || 'default'}>{ticket.status}</Badge>
										</td>
										<td class="px-4 py-3 text-right font-mono">{ticket.stake.toFixed(2)}</td>
										<td class="px-4 py-3 text-right font-mono" style="color: var(--accent-green);">x{ticket.total_odds.toFixed(2)}</td>
										<td class="px-4 py-3 text-right font-mono" style="color: {ticket.actual_return !== null && ticket.actual_return > 0 ? 'var(--accent-green)' : ticket.actual_return !== null ? 'var(--danger)' : 'var(--text-muted)'};">{ticket.actual_return !== null ? ticket.actual_return.toFixed(2) : '-'}</td>
										<td class="px-4 py-3 text-xs" style="color: var(--text-muted);">{new Date(ticket.created_at).toLocaleDateString()}</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{/if}

			{:else if activeTab === 'place'}
				<div class="card p-4" style="border-top: 2px solid var(--accent-green);">
					<h3 class="text-lg font-semibold mb-4" style="color: var(--text-primary);">Place Bet</h3>
					<form onsubmit={(e) => { e.preventDefault(); placeBet(); }} class="space-y-4">
						{#if betError}
							<div class="p-3 text-sm border" style="background-color: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3); color: var(--danger); border-radius: 0;">{betError}</div>
						{/if}

						<Select
							label="Match"
							bind:value={betMatchId}
							options={matchOptions}
							placeholder="Select a match..."
						/>

						<div class="grid grid-cols-2 gap-4">
							<Select
								label="Market"
								bind:value={betMarket}
								options={[
									{ value: '1x2', label: '1X2 (Match Result)' },
									{ value: 'over_under', label: 'Over/Under' },
									{ value: 'both_score', label: 'Both to Score' }
								]}
							/>
							<Select
								label="Selection"
								bind:value={betSelection}
								options={[
									{ value: 'home', label: 'Home' },
									{ value: 'draw', label: 'Draw' },
									{ value: 'away', label: 'Away' }
								]}
							/>
						</div>

						<div class="grid grid-cols-2 gap-4">
							<Input label="Odds" type="number" step="0.01" bind:value={betOdds} />
							<Input label="Stake" type="number" step="0.50" bind:value={betStake} />
						</div>

						<div class="p-3" style="background-color: var(--bg-deep); border: 1px solid var(--border-subtle);">
							<div class="flex justify-between text-sm">
								<span style="color: var(--text-muted);">Potential Return:</span>
								<span class="font-mono font-medium" style="color: var(--accent-green);">
									{(parseFloat(betStake || '0') * parseFloat(betOdds || '1')).toFixed(2)}
								</span>
							</div>
							<div class="flex justify-between text-sm mt-1">
								<span style="color: var(--text-muted);">Profit:</span>
								<span class="font-mono" style="color: var(--accent-green);">
									{(parseFloat(betStake || '0') * parseFloat(betOdds || '1') - parseFloat(betStake || '0')).toFixed(2)}
								</span>
							</div>
						</div>

						<Button type="submit" disabled={betSubmitting || !betMatchId}>
							{betSubmitting ? 'Placing...' : 'Place Bet'}
						</Button>
					</form>
				</div>
			{/if}
		</Tabs>
	{/if}
</div>

<style>
	tbody tr:hover {
		background-color: var(--bg-elevated);
	}
</style>
