<script lang="ts">
	import {
		Home,
		Brain,
		Ticket,
		Database,
		LayoutDashboard,
		User,
		Search,
		Zap,
		Plus,
		Eye
	} from 'lucide-svelte';

	interface CommandItem {
		id: string;
		label: string;
		icon: typeof Home;
		shortcut?: string;
		category: 'page' | 'match' | 'action';
		action: () => void;
	}

	const pages: CommandItem[] = [
		{ id: 'home', label: 'Home', icon: Home, shortcut: 'H', category: 'page', action: () => goto('/') },
		{ id: 'predict', label: 'Predict', icon: Brain, shortcut: 'P', category: 'page', action: () => goto('/predict') },
		{ id: 'tickets', label: 'Tickets', icon: Ticket, shortcut: 'T', category: 'page', action: () => goto('/tickets') },
		{ id: 'data', label: 'Data', icon: Database, shortcut: 'D', category: 'page', action: () => goto('/data') },
		{ id: 'board', label: 'Board', icon: LayoutDashboard, shortcut: 'B', category: 'page', action: () => goto('/board') },
		{ id: 'account', label: 'Account', icon: User, shortcut: 'A', category: 'page', action: () => goto('/account') }
	];

	const actions: CommandItem[] = [
		{ id: 'run-prediction', label: 'Run Prediction', icon: Zap, category: 'action', action: () => goto('/predict') },
		{ id: 'place-bet', label: 'Place Bet', icon: Plus, category: 'action', action: () => goto('/tickets') },
		{ id: 'view-value-bets', label: 'View Value Bets', icon: Eye, category: 'action', action: () => goto('/predict') }
	];

	let {
		matches = [],
		open = $bindable(false)
	}: {
		matches?: { id: number; home_team: string; away_team: string }[];
		open?: boolean;
	} = $props();

	let query = $state('');
	let selectedIndex = $state(0);
	let inputRef = $state<HTMLInputElement | null>(null);

	function goto(path: string) {
		window.location.href = path;
	}

	const allItems = $derived.by(() => {
		const matchItems: CommandItem[] = matches.map((m) => ({
			id: `match-${m.id}`,
			label: `${m.home_team} vs ${m.away_team}`,
			icon: Search,
			category: 'match' as const,
			action: () => goto(`/matches/${m.id}`)
		}));
		return [...pages, ...matchItems, ...actions];
	});

	const filtered = $derived(
		query.trim() === ''
			? allItems
			: allItems.filter(
				(item) =>
					item.label.toLowerCase().includes(query.toLowerCase()) ||
					item.category.toLowerCase().includes(query.toLowerCase())
			)
	);

	$effect(() => {
		selectedIndex = 0;
	});

	function handleKeydown(e: KeyboardEvent) {
		if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
			e.preventDefault();
			open = !open;
			return;
		}
		if (!open) return;

		if (e.key === 'Escape') {
			e.preventDefault();
			open = false;
			return;
		}

		if (e.key === 'ArrowDown') {
			e.preventDefault();
			selectedIndex = (selectedIndex + 1) % filtered.length;
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			selectedIndex = (selectedIndex - 1 + filtered.length) % filtered.length;
		} else if (e.key === 'Enter') {
			e.preventDefault();
			const item = filtered[selectedIndex];
			if (item) {
				item.action();
				open = false;
			}
		}
	}

	function executeItem(item: CommandItem) {
		item.action();
		open = false;
	}

	$effect(() => {
		if (open) {
			const t = setTimeout(() => inputRef?.focus(), 50);
			return () => clearTimeout(t);
		}
	});
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
	<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-[60] flex items-start justify-center pt-[15vh]"
		style="background: rgba(6, 11, 20, 0.95);"
		onclick={(e) => {
			if (e.target === e.currentTarget) open = false;
		}}
	>
		<div
			class="w-full max-w-xl overflow-hidden"
			style="background: var(--bg-surface); border: 1px solid var(--border-active); box-shadow: 0 0 40px rgba(0,0,0,0.4);"
		>
			<!-- Search input -->
			<div class="flex items-center gap-3 px-4 py-3 border-b" style="border-color: var(--border-subtle);">
				<Search class="w-5 h-5" style="color: var(--text-secondary);" />
				<input
					bind:this={inputRef}
					type="text"
					placeholder="Search pages, matches, actions..."
					class="flex-1 bg-transparent text-sm outline-none"
					style="color: var(--text-primary);"
					bind:value={query}
				/>
				<span
					class="text-[10px] font-mono px-1.5 py-0.5"
					style="color: var(--text-secondary); border: 1px solid var(--border-subtle); font-family: 'JetBrains Mono', monospace;"
				>
					ESC
				</span>
			</div>

			<!-- Results -->
			<div class="max-h-[50vh] overflow-y-auto">
				{#if filtered.length === 0}
					<div class="flex flex-col items-center justify-center py-12 gap-2">
						<Search class="w-8 h-8" style="color: var(--text-secondary); opacity: 0.4;" />
						<p class="text-sm" style="color: var(--text-secondary);">No results found</p>
						<p class="text-xs" style="color: var(--text-secondary); opacity: 0.6;">
							Try a different search term
						</p>
					</div>
				{:else}
					{#each filtered as item, i (item.id)}
						{@const isSelected = i === selectedIndex}
						{@const Icon = item.icon}
						<button
							class="flex items-center justify-between w-full px-4 py-3 text-left transition-colors duration-200"
							style={
								isSelected
									? 'background: rgba(74, 222, 128, 0.08); color: var(--accent-green);'
									: 'color: var(--text-primary);'
							}
							onmouseenter={() => (selectedIndex = i)}
							onclick={() => executeItem(item)}
						>
							<div class="flex items-center gap-3">
								<Icon class="w-4 h-4" style={isSelected ? 'color: var(--accent-green);' : 'color: var(--text-secondary);'} />
								<span class="text-sm">{item.label}</span>
								<span
									class="text-[10px] font-mono px-1 py-0.5"
									style="color: var(--text-secondary); border: 1px solid var(--border-subtle); text-transform: uppercase; font-family: 'JetBrains Mono', monospace;"
								>
									{item.category}
								</span>
							</div>
							{#if item.shortcut}
								<span
									class="text-[10px] font-mono px-1.5 py-0.5"
									style="color: var(--text-secondary); border: 1px solid var(--border-subtle); font-family: 'JetBrains Mono', monospace;"
								>
									{item.shortcut}
								</span>
							{/if}
						</button>
					{/each}
				{/if}
			</div>

			<!-- Footer hint -->
			<div
				class="flex items-center gap-4 px-4 py-2 text-[10px]"
				style="color: var(--text-secondary); opacity: 0.6; border-top: 1px solid var(--border-subtle); font-family: 'JetBrains Mono', monospace;"
			>
				<span>&#8593;&#8595; navigate</span>
				<span>&#8629; select</span>
				<span>esc close</span>
			</div>
		</div>
	</div>
{/if}

<style>
	input::placeholder {
		color: var(--text-secondary);
		opacity: 0.5;
	}
</style>
