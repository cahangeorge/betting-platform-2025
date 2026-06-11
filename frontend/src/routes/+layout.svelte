<script lang="ts">
	import '../app.css';
	import { navigating } from '$app/stores';
	import { fade, slide } from 'svelte/transition';
	import { onMount } from 'svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Navbar from '$lib/components/Navbar.svelte';
	import BetSlipDrawer from '$lib/components/BetSlipDrawer.svelte';
	import BottomNav from '$lib/components/BottomNav.svelte';
	import BetslipFAB from '$lib/components/BetslipFAB.svelte';
	import Loading from '$lib/components/Loading.svelte';
	import { liveSocket } from '$lib/stores/liveSocket';

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
	let betslipOpen = $state(false);

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
				betslipOpen = false;
				prevUrl = nav.to.url.pathname;
			}
		});
		return unsub;
	});

	// Connect to live WebSocket on mount
	onMount(() => {
		liveSocket.connect();
		return () => {
			liveSocket.disconnect();
		};
	});
</script>

<!-- Skip to main content -->
<a href="#main-content" class="sr-only-focusable">Skip to main content</a>

<div class="min-h-screen bg-background">
	<Navbar user={data.user} onToggleSidebar={toggleSidebar} />

	<!-- Desktop: 3-column layout -->
	<div class="hidden lg:grid lg:grid-cols-[220px_1fr_320px] pt-16 min-h-screen">
		<!-- Sidebar: fixed left -->
		<aside class="relative" role="complementary" aria-label="Navigation sidebar">
			<div class="fixed top-16 left-0 z-30 w-[220px] h-[calc(100vh-64px)]">
				<Sidebar bind:open={sidebarOpen} user={data.user} />
			</div>
		</aside>

		<!-- Main content -->
		<main id="main-content" class="min-h-[calc(100vh-4rem)]" role="main">
			<div class="p-4 lg:p-6 max-w-none">
				{#if isNavigating}
					<div class="flex items-center justify-center py-20" transition:fade={{ duration: 150 }}>
						<Loading message="Loading..." />
					</div>
				{:else}
					<div transition:fade={{ duration: 200, delay: 50 }}>
						{@render children()}
					</div>
				{/if}
			</div>
		</main>

		<!-- Betslip: sticky right panel -->
		<aside class="relative" role="complementary" aria-label="Bet slip">
			<div class="sticky top-16 scroll-thin h-[calc(100vh-64px)] overflow-y-auto border-l border-border">
				<BetSlipDrawer />
			</div>
		</aside>
	</div>

	<!-- Tablet/Mobile: single column layout -->
	<div class="lg:hidden pt-16 pb-16">
		<!-- Mobile sidebar overlay -->
		{#if sidebarOpen}
			<Sidebar bind:open={sidebarOpen} user={data.user} />
		{/if}

		<!-- Main content -->
		<main id="main-content-mobile" class="min-h-[calc(100vh-4rem)]" role="main">
			<div class="p-4 max-w-none">
				{#if isNavigating}
					<div class="flex items-center justify-center py-20" transition:fade={{ duration: 150 }}>
						<Loading message="Loading..." />
					</div>
				{:else}
					<div transition:fade={{ duration: 200, delay: 50 }}>
						{@render children()}
					</div>
				{/if}
			</div>
		</main>

		<!-- Betslip FAB (mobile only) -->
		<BetslipFAB count={0} onclick={() => (betslipOpen = true)} />

		<!-- Betslip bottom sheet (mobile/tablet) -->
		{#if betslipOpen}
			<div class="fixed inset-0 z-50 lg:hidden" transition:fade={{ duration: 150 }}>
				<!-- Backdrop -->
				<button
					class="absolute inset-0 bg-black/50 backdrop-blur-sm"
					onclick={() => (betslipOpen = false)}
					aria-label="Close bet slip"
				></button>
				<!-- Bottom sheet -->
				<div
					class="absolute bottom-0 left-0 right-0 max-h-[85vh] bg-card border-t border-border -2xl overflow-hidden"
					style="padding-bottom: env(safe-area-inset-bottom, 0px);"
					transition:slide={{ duration: 250, axis: 'y' }}
				>
					<div class="h-full overflow-y-auto scroll-thin">
						<BetSlipDrawer bind:open={betslipOpen} />
					</div>
				</div>
			</div>
		{/if}
	</div>

	<!-- Bottom nav (mobile only) -->
	<BottomNav />
</div>
