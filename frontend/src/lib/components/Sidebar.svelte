<script lang="ts">
	import { page } from '$app/stores';
	import {
		Home,
		BarChart3,
		Ticket,
		Database,
		LayoutGrid,
		User,
		Info,
		Zap,
		Radio
	} from 'lucide-svelte';

	let {
		open,
		user
	}: {
		open: boolean;
		user: { name: string; email: string } | null;
	} = $props();

	const navItems = [
		{ href: '/', label: 'Home', icon: Home },
		{ href: '/value-bets', label: 'Value Bets', icon: Zap },
		{ href: '/live', label: 'Live', icon: Radio },
		{ href: '/predict', label: 'Predictions', icon: BarChart3 },
		{ href: '/tickets', label: 'Tickets', icon: Ticket },
		{ href: '/data', label: 'Data', icon: Database },
		{ href: '/board', label: 'Board', icon: LayoutGrid },
		{ href: '/account', label: 'Account', icon: User },
		{ href: '/about', label: 'About', icon: Info }
	];

	function isActive(href: string): boolean {
		if (href === '/') return $page.url.pathname === '/';
		return $page.url.pathname.startsWith(href);
	}

	let connected = $state(true);
</script>

{#if open}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-20 lg:hidden"
		role="presentation"
		onclick={() => (open = false)}
		onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') open = false; }}
		style="background-color: rgba(6, 11, 20, 0.85);"
	></div>
{/if}

<aside
	class="fixed top-16 left-0 z-30 border-r transform transition-transform duration-200 overflow-y-auto lg:translate-x-0 scroll-thin sidebar-nav"
	class:-translate-x-full={!open}
	style="background-color: var(--bg-surface); border-color: var(--border-subtle); width: 220px; height: calc(100vh - 64px);"
>
	<nav class="p-3 space-y-0.5">
		{#each navItems as item (item.href)}
			<a
				href={item.href}
				class="flex items-center space-x-3 px-3 py-2.5 text-sm font-medium transition-all duration-200 ease-out sidebar-link"
				style={isActive(item.href)
					? 'background-color: rgba(74, 222, 128, 0.05); color: var(--accent-green); border-left: 2px solid var(--accent-green);'
					: 'color: var(--text-secondary); border-left: 2px solid transparent;'}
			>
				<item.icon class="w-5 h-5 flex-shrink-0" />
				<span>{item.label}</span>
			</a>
		{/each}
	</nav>

	<div class="absolute bottom-0 left-0 right-0 border-t p-3" style="border-color: var(--border-subtle); background-color: var(--bg-surface);">
		<div class="flex items-center justify-between">
			<div class="flex items-center space-x-2">
				<div
					class="w-2 h-2 animate-pulse-dot"
					style="background-color: {connected ? 'var(--accent-green)' : 'var(--danger)'}; border-radius: 50%;"
				></div>
				<span class="text-xs" style="color: var(--text-secondary);">
					{connected ? 'Connected' : 'Disconnected'}
				</span>
			</div>
			<span class="text-xs font-mono" style="color: var(--text-muted);">SI v0.2.0</span>
		</div>
		<div class="mt-2 flex items-center space-x-2" style="color: var(--text-secondary);">
			<Info class="w-3 h-3" />
			<span class="text-xs" style="color: var(--text-muted);">
				{user?.name ?? 'Offline'}
			</span>
		</div>
	</div>
</aside>

<style>
	.sidebar-link:hover {
		background-color: var(--bg-elevated);
		color: var(--text-primary);
	}
</style>
