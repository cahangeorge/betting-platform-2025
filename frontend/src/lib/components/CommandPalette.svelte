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
	import { cn } from '$lib/utils';
	import { Separator } from './ui/separator';

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
		class="fixed inset-0 z-[60] flex items-start justify-center pt-[15vh] bg-background/95 backdrop-blur-sm"
		onclick={(e) => {
			if (e.target === e.currentTarget) open = false;
		}}
	>
		<div class="w-full max-w-xl overflow-hidden  border border-border bg-card shadow-2xl">
			<!-- Search input -->
			<div class="flex items-center gap-3 px-4 py-3 border-b border-border">
				<Search class="w-5 h-5 text-muted-foreground" />
				<input
					bind:this={inputRef}
					type="text"
					placeholder="Search pages, matches, actions..."
					class="flex-1 bg-transparent text-sm outline-none text-foreground placeholder:text-muted-foreground"
					bind:value={query}
				/>
				<span class="text-[10px] font-mono px-1.5 py-0.5 border border-border text-muted-foreground">
					ESC
				</span>
			</div>

			<!-- Results -->
			<div class="max-h-[50vh] overflow-y-auto">
				{#if filtered.length === 0}
					<div class="flex flex-col items-center justify-center py-12 gap-2">
						<Search class="w-8 h-8 text-muted-foreground opacity-40" />
						<p class="text-sm text-muted-foreground">No results found</p>
						<p class="text-xs text-muted-foreground opacity-60">
							Try a different search term
						</p>
					</div>
				{:else}
					{#each filtered as item, i (item.id)}
						{@const isSelected = i === selectedIndex}
						{@const Icon = item.icon}
						<button
							class={cn(
								'flex items-center justify-between w-full px-4 py-3 text-left transition-colors duration-200',
								isSelected
									? 'bg-football-green/8 text-football-green'
									: 'text-foreground hover:bg-muted'
							)}
							onmouseenter={() => (selectedIndex = i)}
							onclick={() => executeItem(item)}
						>
							<div class="flex items-center gap-3">
								<Icon class={cn('w-4 h-4', isSelected ? 'text-football-green' : 'text-muted-foreground')} />
								<span class="text-sm">{item.label}</span>
								<span class="text-[10px] font-mono px-1 py-0.5 border border-border text-muted-foreground uppercase">
									{item.category}
								</span>
							</div>
							{#if item.shortcut}
								<span class="text-[10px] font-mono px-1.5 py-0.5 border border-border text-muted-foreground">
									{item.shortcut}
								</span>
							{/if}
						</button>
					{/each}
				{/if}
			</div>

			<!-- Footer hint -->
			<div class="flex items-center gap-4 px-4 py-2 text-[10px] border-t border-border text-muted-foreground opacity-60 font-mono">
				<span>&#8593;&#8595; navigate</span>
				<span>&#8629; select</span>
				<span>esc close</span>
			</div>
		</div>
	</div>
{/if}
