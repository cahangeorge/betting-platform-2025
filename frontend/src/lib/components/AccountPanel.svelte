<script lang="ts">
	import { bankrollApi } from '$lib/api/bankroll';
	import { ApiClientError } from '$lib/api/client';
	import type { Bankroll, BookmakerAccount, LedgerEntry } from '$lib/types';
	import Button from './ui/Button.svelte';
	import Card from './ui/Card.svelte';
	import Input from './ui/Input.svelte';
	import Tabs from './ui/Tabs.svelte';
	import Select from './ui/Select.svelte';
	import Badge from './ui/Badge.svelte';
	import Loading from './Loading.svelte';

	let bankrolls = $state<Bankroll[]>([]);
	let accounts = $state<BookmakerAccount[]>([]);
	let ledger = $state<LedgerEntry[]>([]);
	let loading = $state(true);
	let error = $state('');
	let activeTab = $state('bankrolls');

	// New bankroll form
	let showNewBankroll = $state(false);
	let newBankrollName = $state('');
	let newBankrollType = $state<'paper' | 'real'>('paper');
	let newBankrollBalance = $state('1000');
	let newBankrollCurrency = $state('USD');

	// New account form
	let showNewAccount = $state(false);
	let newAccountBookmaker = $state('');
	let newAccountName = $state('');
	let newAccountBalance = $state('0');
	let selectedBankrollId = $state<number | null>(null);

	let formError = $state('');

	async function loadData() {
		loading = true;
		error = '';
		try {
			const [b, a, l] = await Promise.all([
				bankrollApi.getBankrolls(),
				bankrollApi.getAccounts(),
				bankrollApi.getLedger()
			]);
			bankrolls = b;
			accounts = a;
			ledger = l;
		} catch (err) {
			error = err instanceof ApiClientError ? err.message : 'Failed to load account data';
		} finally {
			loading = false;
		}
	}

	async function createBankroll() {
		if (!newBankrollName.trim()) return;
		formError = '';
		try {
			const br = await bankrollApi.createBankroll({
				name: newBankrollName,
				type: newBankrollType,
				currency: newBankrollCurrency,
				initial_balance: parseFloat(newBankrollBalance)
			});
			bankrolls = [...bankrolls, br];
			showNewBankroll = false;
			newBankrollName = '';
			newBankrollBalance = '1000';
		} catch (err) {
			formError = err instanceof ApiClientError ? err.message : 'Failed to create bankroll';
		}
	}

	async function createAccount() {
		if (!newAccountBookmaker.trim() || !newAccountName.trim()) return;
		formError = '';
		try {
			const acct = await bankrollApi.createAccount({
				bookmaker_name: newAccountBookmaker,
				account_name: newAccountName,
				balance: parseFloat(newAccountBalance),
				bankroll_id: selectedBankrollId || bankrolls[0]?.id || 0
			});
			accounts = [...accounts, acct];
			showNewAccount = false;
			newAccountBookmaker = '';
			newAccountName = '';
		} catch (err) {
			formError = err instanceof ApiClientError ? err.message : 'Failed to create account';
		}
	}

	$effect(() => {
		loadData();
	});

	const tabs = $derived([
		{ id: 'bankrolls', label: 'Bankrolls', count: bankrolls.length },
		{ id: 'accounts', label: 'Bookmaker Accounts', count: accounts.length },
		{ id: 'ledger', label: 'Ledger', count: ledger.length }
	]);

	const ledgerCols = [
		{ key: 'created_at', label: 'Date' },
		{ key: 'entry_type', label: 'Type' },
		{ key: 'description', label: 'Description' },
		{ key: 'amount', label: 'Amount' },
		{ key: 'balance_after', label: 'Balance' }
	];

	const ledgerRows = $derived(
		ledger.map((e) => ({
			created_at: new Date(e.created_at).toLocaleDateString(),
			entry_type: e.entry_type.replace('_', ' '),
			description: e.description,
			amount: e.amount > 0 ? `+${e.amount.toFixed(2)}` : e.amount.toFixed(2),
			balance_after: e.balance_after.toFixed(2)
		}))
	);

	const bankrollOptions = $derived(
		bankrolls.map((b) => ({ value: String(b.id), label: b.name }))
	);
</script>

<div class="space-y-6">
	{#if loading}
		<Loading message="Loading account data..." />
	{:else if error}
		<div class="p-4 border text-sm" style="background-color: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3); color: var(--danger); border-radius: 0;">{error}</div>
		<Button onclick={loadData}>Retry</Button>
	{:else}
		<Tabs bind:activeTab {tabs}>
			{#if activeTab === 'bankrolls'}
				<div class="space-y-4">
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
						{#each bankrolls as br (br.id)}
							<Card>
								<div class="space-y-2">
									<div class="flex items-center justify-between">
										<h4 class="font-medium" style="color: var(--text-primary);">{br.name}</h4>
										<Badge variant={br.type === 'real' ? 'info' : 'default'}>{br.type}</Badge>
									</div>
									<p class="text-2xl font-bold font-mono" style="color: var(--accent-green);">
										{br.currency} {br.balance.toFixed(2)}
									</p>
									<p class="text-xs" style="color: var(--text-muted);">
										Initial: {br.currency} {br.initial_balance.toFixed(2)}
									</p>
								</div>
							</Card>
						{/each}

						{#if showNewBankroll}
							<Card>
								<form onsubmit={(e) => { e.preventDefault(); createBankroll(); }} class="space-y-3">
									<h4 class="font-medium" style="color: var(--text-primary);">New Bankroll</h4>
									<Input label="Name" bind:value={newBankrollName} placeholder="My Bankroll" />
									<Select
										label="Type"
										bind:value={newBankrollType}
										options={[
											{ value: 'paper', label: 'Paper (Virtual)' },
											{ value: 'real', label: 'Real Money' }
										]}
									/>
									<Input label="Initial Balance" type="number" bind:value={newBankrollBalance} />
									<div class="flex space-x-2">
										<Button type="submit" size="sm">Create</Button>
										<Button variant="ghost" size="sm" onclick={() => (showNewBankroll = false)}>Cancel</Button>
									</div>
								</form>
							</Card>
						{/if}
					</div>

					{#if !showNewBankroll}
						<Button onclick={() => (showNewBankroll = true)} variant="secondary">
							+ Add Bankroll
						</Button>
					{/if}
				</div>

			{:else if activeTab === 'accounts'}
				<div class="space-y-4">
					<div class="overflow-x-auto">
						<table class="w-full text-sm">
							<thead class="text-xs uppercase" style="background-color: var(--bg-surface); border-bottom: 1px solid var(--border-subtle); color: var(--text-secondary); font-family: var(--font-body);">
								<tr>
									<th class="px-4 py-3 text-left">Bookmaker</th>
									<th class="px-4 py-3 text-left">Account</th>
									<th class="px-4 py-3 text-left">Balance</th>
									<th class="px-4 py-3 text-left">Currency</th>
								</tr>
							</thead>
							<tbody>
								{#each accounts as acct (acct.id)}
									<tr class="transition-colors duration-200" style="border-bottom: 1px solid var(--border-subtle);">
										<td class="px-4 py-3 font-medium" style="color: var(--text-primary);">{acct.bookmaker_name}</td>
										<td class="px-4 py-3" style="color: var(--text-secondary);">{acct.account_name}</td>
										<td class="px-4 py-3 font-mono" style="color: var(--accent-green);">{acct.balance.toFixed(2)}</td>
										<td class="px-4 py-3 font-mono" style="color: var(--text-muted);">{acct.currency}</td>
									</tr>
								{:else}
									<tr>
										<td colspan="4" class="px-4 py-8 text-center" style="color: var(--text-muted);">No accounts linked yet</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>

					{#if showNewAccount}
						<Card title="Link Bookmaker Account">
							<form onsubmit={(e) => { e.preventDefault(); createAccount(); }} class="space-y-3">
								<Input label="Bookmaker Name" bind:value={newAccountBookmaker} placeholder="Bet365" />
								<Input label="Account Name" bind:value={newAccountName} placeholder="Main Account" />
								<Input label="Current Balance" type="number" bind:value={newAccountBalance} />
								{#if bankrollOptions.length > 0}
									<Select
										label="Bankroll"
										bind:value={selectedBankrollId as unknown as string}
										options={bankrollOptions}
									/>
								{/if}
								<div class="flex space-x-2">
									<Button type="submit" size="sm">Link Account</Button>
									<Button variant="ghost" size="sm" onclick={() => (showNewAccount = false)}>Cancel</Button>
								</div>
							</form>
						</Card>
					{:else}
						<Button onclick={() => (showNewAccount = true)} variant="secondary">
							+ Link Bookmaker Account
						</Button>
					{/if}
				</div>

			{:else if activeTab === 'ledger'}
				<div class="overflow-x-auto">
					<table class="w-full text-sm">
						<thead class="text-xs uppercase" style="background-color: var(--bg-surface); border-bottom: 1px solid var(--border-subtle); color: var(--text-secondary); font-family: var(--font-body);">
							<tr>
								{#each ledgerCols as col (col.key)}
									<th class="px-4 py-3 text-left">{col.label}</th>
								{/each}
							</tr>
						</thead>
						<tbody>
							{#each ledgerRows as row (String(row.created_at) + row.entry_type + row.amount)}
								<tr class="transition-colors duration-200" style="border-bottom: 1px solid var(--border-subtle);">
									<td class="px-4 py-3" style="color: var(--text-muted);">{row.created_at}</td>
									<td class="px-4 py-3">
										<Badge variant={row.entry_type.includes('won') || row.entry_type === 'deposit' ? 'success' : row.entry_type.includes('lost') || row.entry_type === 'withdrawal' ? 'danger' : 'default'}>
											{row.entry_type}
										</Badge>
									</td>
									<td class="px-4 py-3" style="color: var(--text-secondary);">{row.description}</td>
									<td class="px-4 py-3 font-mono" style={row.amount.startsWith('+') ? 'color: var(--accent-green);' : 'color: var(--danger);'}>
										{row.amount}
									</td>
									<td class="px-4 py-3 font-mono" style="color: var(--text-secondary);">{row.balance_after}</td>
								</tr>
							{:else}
								<tr>
									<td colspan={ledgerCols.length} class="px-4 py-8 text-center" style="color: var(--text-muted);">No ledger entries yet</td>
								</tr>
							{/each}
						</tbody>
					</table>
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
