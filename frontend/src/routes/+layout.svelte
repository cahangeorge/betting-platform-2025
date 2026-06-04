<script lang="ts">
	import '../app.css';
	import { navigating } from '$app/stores';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Navbar from '$lib/components/Navbar.svelte';
	import BetSlipDrawer from '$lib/components/BetSlipDrawer.svelte';
	import Loading from '$lib/components/Loading.svelte';

	let {
		children,
		data
	}: {
		children: import('svelte').Snippet;
		data: {
			user: { name: string; email: string } | null;
		};
	} = $props();

	let sidebarOpen = $state(false);

	function toggleSidebar() {
		sidebarOpen = !sidebarOpen;
	}

	let isNavigating = $state(false);

	let prevUrl = $state('');
	$effect(() => {
		const unsub = navigating.subscribe((nav) => {
			isNavigating = !!nav;
			if (nav && nav.to && nav.to.url.pathname !== prevUrl) {
				sidebarOpen = false;
				prevUrl = nav.to.url.pathname;
			}
		});
		return unsub;
	});
</script>

<div class="min-h-screen" style="background-color: var(--bg-deep);">
	<Navbar user={data.user} onToggleSidebar={toggleSidebar} />

	<div class="flex pt-16">
		<!-- Sidebar: fixed left, 220px, hidden on mobile by default -->
		<div class="hidden lg:block" style="width: 220px; flex-shrink: 0;">
			<div class="fixed top-16 left-0 z-30" style="width: 220px; height: calc(100vh - 64px);">
				<Sidebar bind:open={sidebarOpen} user={data.user} />
			</div>
		</div>

		<!-- Mobile sidebar overlay -->
		{#if sidebarOpen}
			<div class="lg:hidden">
				<Sidebar bind:open={sidebarOpen} user={data.user} />
			</div>
		{/if}

		<!-- Main content area -->
		<main
			class="flex-1 min-h-[calc(100vh-4rem)] transition-all duration-200"
		>
			<div class="p-4 lg:p-6 max-w-none">
				{#if isNavigating}
					<div class="flex items-center justify-center py-20">
						<Loading message="Loading..." />
					</div>
				{:else}
					{@render children()}
				{/if}
			</div>
		</main>

		<!-- Right betslip: fixed on desktop, hidden on mobile -->
		<div class="hidden lg:block" style="width: 320px; flex-shrink: 0;">
			<div class="sticky top-16 scroll-thin" style="height: calc(100vh - 64px); overflow-y: auto;">
				<BetSlipDrawer />
			</div>
		</div>
	</div>
</div>
