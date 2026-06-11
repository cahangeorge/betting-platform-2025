<script lang="ts">
	import { X, ShoppingCart } from 'lucide-svelte';
	import { cn } from '$lib/utils';
	import Button from './ui/Button.svelte';
	import Input from './ui/Input.svelte';
	import Badge from './ui/Badge.svelte';
	import { Separator } from './ui/separator';

	interface BetLeg {
		id: string;
		matchId: number;
		matchName: string;
		selection: 'Home' | 'Draw' | 'Away';
		odds: number;
		stake: number;
	}

	let {
		open = $bindable(false),
		initialLegs = [],
		onPlaceBet
	}: {
		open?: boolean;
		initialLegs?: BetLeg[];
		onPlaceBet?: (legs: BetLeg[], totalStake: number, isAccumulator: boolean) => void;
	} = $props();

	let legs = $state<BetLeg[]>(initialLegs);
	let isAccumulator = $state(false);
	let quickStakes = $state([5, 10, 25, 50, 100]);

	const totalOdds = $derived(
		isAccumulator ? legs.reduce((acc, l) => acc * l.odds, 1) : legs.reduce((acc, l) => acc + l.odds, 0)
	);

	const totalStake = $derived(legs.reduce((acc, l) => acc + l.stake, 0));

	const potentialReturn = $derived(
		isAccumulator ? totalStake * totalOdds : legs.reduce((acc, l) => acc + l.stake * l.odds, 0)
	);

	function addLeg(matchId: number, matchName: string, selection: 'Home' | 'Draw' | 'Away', odds: number) {
		const exists = legs.some((l) => l.matchId === matchId && l.selection === selection);
		if (exists) return;
		legs = [
			...legs,
			{ id: `${matchId}-${selection}-${Date.now()}`, matchId, matchName, selection, odds, stake: 0 }
		];
		open = true;
	}

	function removeLeg(id: string) {
		legs = legs.filter((l) => l.id !== id);
	}

	function setStake(id: string, amount: number) {
		legs = legs.map((l) => (l.id === id ? { ...l, stake: amount } : l));
	}

	function applyQuickStake(amount: number) {
		if (legs.length === 0) return;
		if (isAccumulator) {
			legs = legs.map((l) => ({ ...l, stake: amount }));
		} else {
			const perLeg = amount / legs.length;
			legs = legs.map((l) => ({ ...l, stake: parseFloat(perLeg.toFixed(2)) }));
		}
	}

	function handlePlaceBet() {
		if (onPlaceBet && legs.length > 0 && totalStake > 0) {
			onPlaceBet(legs, totalStake, isAccumulator);
		}
	}

	export { addLeg, removeLeg };
</script>

<div class="flex flex-col bg-card">
	<!-- Header -->
	<div class="flex items-center justify-between px-4 py-3 border-b border-border">
		<div class="flex items-center gap-2">
			<ShoppingCart class="w-4 h-4 text-football-green" />
			<span class="text-xs font-bold tracking-widest font-sport text-foreground">BET SLIP</span>
			{#if legs.length > 0}
				<Badge variant="success">{legs.length}</Badge>
			{/if}
		</div>
		<Button variant="ghost" size="sm" class="p-1 lg:hidden" onclick={() => (open = false)} aria-label="Close bet slip">
			<X class="w-5 h-5 text-muted-foreground" />
		</Button>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-y-auto scroll-thin">
		{#if legs.length === 0}
			<div class="flex flex-col items-center justify-center py-16 gap-3">
				<ShoppingCart class="w-10 h-10 text-muted-foreground opacity-30" />
				<p class="text-sm text-muted-foreground">Select odds to add bets</p>
				<p class="text-xs text-muted-foreground">
					Click odds on any match card
				</p>
			</div>
		{:else}
			<!-- Legs list -->
			<div class="p-3 space-y-2">
				{#each legs as leg (leg.id)}
					<div class="p-3  bg-background border border-border">
						<div class="flex items-start justify-between mb-2">
							<div class="flex-1 min-w-0">
								<p class="text-xs font-medium truncate text-foreground">
									{leg.matchName}
								</p>
								<div class="flex items-center gap-2 mt-1">
									<Badge variant="success" class="text-[10px] px-1.5 py-0.5 font-mono">
										{leg.selection}
									</Badge>
									<span class="text-sm font-mono font-semibold text-football-blue">
										{leg.odds.toFixed(2)}
									</span>
								</div>
							</div>
							<Button variant="ghost" size="sm" class="p-1 ml-2" onclick={() => removeLeg(leg.id)} aria-label="Remove leg">
								<X class="w-4 h-4 text-muted-foreground" />
							</Button>
						</div>

						<!-- Stake input -->
						<div class="flex items-center gap-2">
							<span class="text-[10px] font-mono text-muted-foreground">£</span>
							<input
								type="number"
								min="0"
								step="0.01"
								value={leg.stake || ''}
								placeholder="0.00"
								class="flex-1 bg-transparent text-sm outline-none text-right  border border-border px-2 py-1 font-mono text-foreground focus:ring-1 focus:ring-ring"
								oninput={(e) => setStake(leg.id, parseFloat(e.currentTarget.value) || 0)}
							/>
							<span class="text-[10px] font-mono text-muted-foreground">
								£{(leg.stake * leg.odds).toFixed(2)}
							</span>
						</div>
					</div>
				{/each}
			</div>

			<!-- Quick stakes -->
			<div class="px-3 pb-2">
				<div class="flex items-center gap-1.5">
					{#each quickStakes as amount}
						<button
							class="flex-1 py-1.5 text-xs font-mono transition-colors duration-200  border border-border text-foreground hover:border-football-green"
							onclick={() => applyQuickStake(amount)}
						>
							£{amount}
						</button>
					{/each}
				</div>
			</div>

			<!-- Accumulator toggle -->
			<div class="px-3 py-2">
				<div class="flex items-center justify-between p-2  bg-background border border-border">
					<span class="text-xs text-muted-foreground">Accumulator</span>
					<button
						class="relative w-9 h-5  transition-colors duration-200"
						style="background: {isAccumulator ? 'hsl(var(--football-green))' : 'hsl(var(--border))'};"
						onclick={() => (isAccumulator = !isAccumulator)}
						aria-label="Toggle accumulator"
					>
						<div
							class="absolute top-0.5 w-4 h-4  transition-all duration-200 bg-card"
							style="left: {isAccumulator ? '18px' : '2px'};"
						></div>
					</button>
				</div>
			</div>

			<!-- Summary -->
			<div class="mx-3 p-3 space-y-2  bg-background border border-border">
				<div class="flex items-center justify-between">
					<span class="text-xs text-muted-foreground">Total Stake</span>
					<span class="text-sm font-mono font-semibold text-foreground">
						£{totalStake.toFixed(2)}
					</span>
				</div>
				<div class="flex items-center justify-between">
					<span class="text-xs text-muted-foreground">Potential Return</span>
					<span class="text-sm font-mono font-bold text-football-green">
						£{potentialReturn.toFixed(2)}
					</span>
				</div>
			</div>
		{/if}
	</div>

	<!-- Place Bet button -->
	{#if legs.length > 0}
		<div class="p-3 border-t border-border">
			<Button
				class="w-full py-3 text-sm font-bold tracking-wider bg-football-green text-primary-foreground hover:bg-football-green/90"
				onclick={handlePlaceBet}
			>
				PLACE BET
			</Button>
		</div>
	{/if}
</div>

<style>
	input[type='number']::-webkit-inner-spin-button,
	input[type='number']::-webkit-outer-spin-button {
		-webkit-appearance: none;
		margin: 0;
	}
	input::placeholder {
		color: hsl(var(--muted-foreground));
		opacity: 0.4;
	}
</style>
