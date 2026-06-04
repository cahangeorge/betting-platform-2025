<script lang="ts">
	import { X, ShoppingCart } from 'lucide-svelte';

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

<div class="h-full flex flex-col" style="background: var(--bg-surface); border-left: 1px solid var(--border-subtle);">
	<!-- Header -->
	<div
		class="flex items-center justify-between px-4 py-3 border-b"
		style="border-color: var(--border-subtle);"
	>
		<div class="flex items-center gap-2">
			<ShoppingCart class="w-4 h-4" style="color: var(--accent-green);" />
			<span class="text-xs font-bold tracking-widest font-sport" style="color: var(--text-primary);">BET SLIP</span>
			{#if legs.length > 0}
				<span
					class="text-[10px] font-mono px-1.5 py-0.5"
					style="color: var(--bg-surface); background: var(--accent-green); font-family: 'JetBrains Mono', monospace;"
				>
					{legs.length}
				</span>
			{/if}
		</div>
		<button class="p-1 transition-colors duration-200 hover:opacity-80 lg:hidden" onclick={() => (open = false)} aria-label="Close bet slip">
			<X class="w-5 h-5" style="color: var(--text-secondary);" />
		</button>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-y-auto scroll-thin">
		{#if legs.length === 0}
			<div class="flex flex-col items-center justify-center py-16 gap-3">
				<ShoppingCart class="w-10 h-10" style="color: var(--text-secondary); opacity: 0.3;" />
				<p class="text-sm" style="color: var(--text-secondary);">Select odds to add bets</p>
				<p class="text-xs" style="color: var(--text-muted);">
					Click odds on any match card
				</p>
			</div>
		{:else}
			<!-- Legs list -->
			<div class="p-3 space-y-2">
				{#each legs as leg (leg.id)}
					<div
						class="p-3"
						style="background: var(--bg-deep); border: 1px solid var(--border-subtle);"
					>
						<div class="flex items-start justify-between mb-2">
							<div class="flex-1 min-w-0">
								<p class="text-xs font-medium truncate" style="color: var(--text-primary);">
									{leg.matchName}
								</p>
								<div class="flex items-center gap-2 mt-1">
									<span
										class="text-[10px] font-mono px-1.5 py-0.5"
										style="color: var(--accent-green); border: 1px solid rgba(74, 222, 128, 0.3); font-family: 'JetBrains Mono', monospace;"
									>
										{leg.selection}
									</span>
									<span
										class="text-sm font-mono font-semibold"
										style="color: var(--accent-blue); font-family: 'JetBrains Mono', monospace;"
									>
										{leg.odds.toFixed(2)}
									</span>
								</div>
							</div>
							<button
								class="p-1 ml-2 transition-colors duration-200 hover:opacity-80"
								onclick={() => removeLeg(leg.id)}
								aria-label="Remove leg"
							>
								<X class="w-4 h-4" style="color: var(--text-secondary);" />
							</button>
						</div>

						<!-- Stake input -->
						<div class="flex items-center gap-2">
							<span class="text-[10px] font-mono" style="color: var(--text-secondary); font-family: 'JetBrains Mono', monospace;">£</span>
							<input
								type="number"
								min="0"
								step="0.01"
								value={leg.stake || ''}
								placeholder="0.00"
								class="flex-1 bg-transparent text-sm outline-none text-right"
								style="color: var(--text-primary); border: 1px solid var(--border-subtle); padding: 4px 8px; font-family: 'JetBrains Mono', monospace;"
								oninput={(e) => setStake(leg.id, parseFloat(e.currentTarget.value) || 0)}
							/>
							<span
								class="text-[10px] font-mono"
								style="color: var(--text-secondary); font-family: 'JetBrains Mono', monospace;"
							>
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
							class="flex-1 py-1.5 text-xs font-mono transition-colors duration-200"
							style="color: var(--text-primary); border: 1px solid var(--border-subtle); border-radius: 9999px; font-family: 'JetBrains Mono', monospace;"
							onclick={() => applyQuickStake(amount)}
							onmouseenter={(e) => (e.currentTarget.style.borderColor = 'var(--accent-green)')}
							onmouseleave={(e) => (e.currentTarget.style.borderColor = 'var(--border-subtle)')}
						>
							£{amount}
						</button>
					{/each}
				</div>
			</div>

			<!-- Accumulator toggle -->
			<div class="px-3 py-2">
				<div
					class="flex items-center justify-between p-2"
					style="background: var(--bg-deep); border: 1px solid var(--border-subtle);"
				>
					<span class="text-xs" style="color: var(--text-secondary);">Accumulator</span>
					<button
						class="relative w-9 h-5 transition-colors duration-200"
						style="background: {isAccumulator ? 'var(--accent-green)' : 'var(--border-subtle)'};"
						onclick={() => (isAccumulator = !isAccumulator)}
						aria-label="Toggle accumulator"
					>
						<div
							class="absolute top-0.5 w-4 h-4 transition-all duration-200"
							style="background: var(--bg-surface); left: {isAccumulator ? '18px' : '2px'};"
						></div>
					</button>
				</div>
			</div>

			<!-- Summary -->
			<div
				class="mx-3 p-3 space-y-2"
				style="background: var(--bg-deep); border: 1px solid var(--border-subtle);"
			>
				<div class="flex items-center justify-between">
					<span class="text-xs" style="color: var(--text-secondary);">Total Stake</span>
					<span
						class="text-sm font-mono font-semibold"
						style="color: var(--text-primary); font-family: 'JetBrains Mono', monospace;"
					>
						£{totalStake.toFixed(2)}
					</span>
				</div>
				<div class="flex items-center justify-between">
					<span class="text-xs" style="color: var(--text-secondary);">Potential Return</span>
					<span
						class="text-sm font-mono font-bold"
						style="color: var(--accent-green); font-family: 'JetBrains Mono', monospace;"
					>
						£{potentialReturn.toFixed(2)}
					</span>
				</div>
			</div>
		{/if}
	</div>

	<!-- Place Bet button -->
	{#if legs.length > 0}
		<div class="p-3 border-t" style="border-color: var(--border-subtle);">
			<button
				class="w-full py-3 text-sm font-bold tracking-wider transition-all duration-200"
				style="background: var(--accent-green); color: var(--text-inverse); border: none;"
				onmouseenter={(e) => (e.currentTarget.style.boxShadow = '0 0 20px rgba(74, 222, 128, 0.2)')}
				onmouseleave={(e) => (e.currentTarget.style.boxShadow = 'none')}
				onclick={handlePlaceBet}
			>
				PLACE BET
			</button>
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
		color: var(--text-secondary);
		opacity: 0.4;
	}
</style>
