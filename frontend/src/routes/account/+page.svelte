<script lang="ts">
	import AccountPanel from '$lib/components/AccountPanel.svelte';
	import type { BackendLoadStatus } from '$lib/types/backend';

	let { data }: import('./$types').PageProps = $props();
	const backendStatus = $derived(((data as { backendStatus?: BackendLoadStatus }).backendStatus as BackendLoadStatus | undefined) ?? {
		state: 'ready',
		message: null,
		failedEndpoints: []
	});

	// SSR-safe: use optional chaining since data may not have page server data during SSR
	const bankrolls = $derived((data as any)?.bankrolls ?? []);
	const accounts = $derived((data as any)?.accounts ?? []);
	const ledger = $derived((data as any)?.ledger ?? []);
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-extrabold font-sport text-foreground">ACCOUNT</h1>
		<p class="mt-1 text-muted-foreground">Manage bankrolls, bookmaker accounts, and view transaction history</p>
	</div>

	{#if backendStatus.state === 'degraded' && backendStatus.message}
		<div class="border border-yellow-500/30 bg-yellow-500/10 p-4 text-sm text-yellow-200">
			<span class="font-medium">Partial backend data.</span> {backendStatus.message}
		</div>
	{/if}

	<!-- SSR: render bankroll cards directly if data available -->
	{#if bankrolls.length > 0}
		<div class="space-y-4">
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each bankrolls as br (br.id)}
					<div class="p-4 border border-border">
						<div class="flex items-center justify-between mb-2">
							<h4 class="font-medium text-foreground">{br.name}</h4>
							<span class="text-xs px-2 py-0.5 border border-border text-muted-foreground">{br.type}</span>
						</div>
						<p class="text-2xl font-bold font-mono text-football-green">
							{br.currency} {br.balance.toFixed(2)}
						</p>
						<p class="text-xs text-muted-foreground">
							Initial: {br.currency} {br.initial_balance.toFixed(2)}
						</p>
					</div>
				{/each}
			</div>
		</div>
	{:else}
		<p class="text-sm text-muted-foreground">No bankrolls found. Create one to get started.</p>
	{/if}

	{#if accounts.length > 0}
		<div class="mt-6">
			<h3 class="text-lg font-semibold text-foreground mb-3">Bookmaker Accounts</h3>
			<div class="overflow-x-auto">
				<table class="w-full text-sm">
					<thead class="text-xs uppercase bg-muted border-b border-border text-muted-foreground">
						<tr>
							<th class="px-4 py-3 text-left">Bookmaker</th>
							<th class="px-4 py-3 text-left">Account</th>
							<th class="px-4 py-3 text-left">Balance</th>
							<th class="px-4 py-3 text-left">Context</th>
						</tr>
					</thead>
					<tbody>
						{#each accounts as acct (acct.id)}
							<tr class="border-b border-border hover:bg-muted">
								<td class="px-4 py-3 font-medium text-foreground">{acct.bookmaker}</td>
								<td class="px-4 py-3 text-muted-foreground">{acct.account_name}</td>
								<td class="px-4 py-3 font-mono text-football-green">{acct.balance.toFixed(2)}</td>
								<td class="px-4 py-3 font-mono text-muted-foreground">Bankroll-linked</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/if}

	{#if ledger.length > 0}
		<div class="mt-6">
			<h3 class="text-lg font-semibold text-foreground mb-3">Ledger</h3>
			<div class="overflow-x-auto">
				<table class="w-full text-sm">
					<thead class="text-xs uppercase bg-muted border-b border-border text-muted-foreground">
						<tr>
							<th class="px-4 py-3 text-left">Date</th>
							<th class="px-4 py-3 text-left">Type</th>
							<th class="px-4 py-3 text-left">Description</th>
							<th class="px-4 py-3 text-left">Amount</th>
							<th class="px-4 py-3 text-left">Balance</th>
						</tr>
					</thead>
					<tbody>
						{#each ledger as entry (entry.id)}
							<tr class="border-b border-border hover:bg-muted">
								<td class="px-4 py-3 text-muted-foreground">{new Date(entry.created_at).toLocaleDateString()}</td>
								<td class="px-4 py-3">{entry.entry_type.replace('_', ' ')}</td>
								<td class="px-4 py-3 text-muted-foreground">{entry.description}</td>
								<td class="px-4 py-3 font-mono {entry.amount > 0 ? 'text-football-green' : 'text-destructive'}">
									{entry.amount > 0 ? '+' : ''}{entry.amount.toFixed(2)}
								</td>
								<td class="px-4 py-3 font-mono text-muted-foreground">{entry.balance_after.toFixed(2)}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/if}

	<!-- Client-side: full interactive AccountPanel for JS-enabled browsers -->
	<AccountPanel
		serverBankrolls={bankrolls}
		serverAccounts={accounts}
		serverLedger={ledger}
	/>
</div>
