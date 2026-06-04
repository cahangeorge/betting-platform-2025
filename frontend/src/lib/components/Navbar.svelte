<script lang="ts">
	import { page } from '$app/stores';
	import { authApi } from '$lib/api/auth';
	import { Menu, Activity } from 'lucide-svelte';

	let {
		user,
		onToggleSidebar
	}: {
		user: { name: string; email: string } | null;
		onToggleSidebar: () => void;
	} = $props();

	let showUserMenu = $state(false);
	let now = $state(new Date());
	let connected = $state(true);

	async function handleLogout() {
		try {
			await authApi.logout();
			window.location.href = '/login';
		} catch {
			window.location.href = '/login';
		}
	}

	function closeMenuOnClickOutside(e: MouseEvent) {
		const target = e.target as HTMLElement;
		if (!target.closest('[data-user-menu]')) {
			showUserMenu = false;
		}
	}

	$effect(() => {
		if (showUserMenu) {
			document.addEventListener('click', closeMenuOnClickOutside);
			return () => document.removeEventListener('click', closeMenuOnClickOutside);
		}
	});

	$effect(() => {
		const interval = setInterval(() => {
			now = new Date();
		}, 1000);
		return () => clearInterval(interval);
	});

	let timeStr = $derived(
		now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
	);
</script>

<nav
	class="fixed top-0 left-0 right-0 z-50 h-16 border-b"
	style="background-color: var(--bg-deep); border-color: var(--border-subtle);"
>
	<div class="flex items-center justify-between h-full px-4 lg:px-6">
		<div class="flex items-center space-x-4">
			<button
				class="lg:hidden p-2 transition-colors"
				style="color: var(--text-secondary); border-radius: 0;"
				onclick={onToggleSidebar}
				aria-label="Toggle sidebar"
			>
				<Menu class="w-5 h-5" />
			</button>
			<a href="/" class="flex items-center space-x-3">
				<span
					class="text-lg font-extrabold tracking-tight hidden sm:inline"
					style="color: var(--text-primary); font-family: var(--font-sport); letter-spacing: 0.05em;"
				>
					STADIUM INTEL
				</span>
			</a>
		</div>

		<div class="flex items-center space-x-4">
			<div class="hidden md:flex items-center space-x-3">
				<Activity class="w-3 h-3" style="color: {connected ? 'var(--accent-green)' : 'var(--danger)'};" />
				<span class="text-xs font-mono" style="color: var(--text-secondary);">{timeStr}</span>
			</div>

			{#if user}
				<div class="relative" data-user-menu>
					<button
						class="flex items-center space-x-2 p-1.5 transition-colors"
						style="border: 1px solid var(--border-subtle); border-radius: 0;"
						onclick={() => (showUserMenu = !showUserMenu)}
					>
						<div
							class="w-7 h-7 flex items-center justify-center text-xs font-bold"
							style="background-color: var(--bg-elevated); color: var(--accent-green); border-radius: 0;"
						>
							{user.name.charAt(0).toUpperCase()}
						</div>
						<span class="text-sm hidden md:block" style="color: var(--text-primary);">{user.name}</span>
						<svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 hidden md:block" style="color: var(--text-secondary);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
						</svg>
					</button>

					{#if showUserMenu}
						<div class="absolute right-0 mt-2 w-56 py-2 z-50 border" style="background-color: var(--bg-surface); border-color: var(--border-subtle); border-radius: 0; box-shadow: 0 0 20px rgba(0,0,0,0.3);">
							<div class="px-4 py-2 border-b" style="border-color: var(--border-subtle);">
								<p class="text-sm font-medium" style="color: var(--text-primary);">{user.name}</p>
								<p class="text-xs" style="color: var(--text-secondary);">{user.email}</p>
							</div>
							<a href="/account" class="block px-4 py-2 text-sm transition-colors duration-200" style="color: var(--text-secondary);" onclick={() => (showUserMenu = false)}>
								Account
							</a>
							<button
								class="w-full text-left px-4 py-2 text-sm transition-colors duration-200"
								style="color: var(--danger);"
								onclick={handleLogout}
							>
								Sign Out
							</button>
						</div>
					{/if}
				</div>
			{:else}
				<a href="/login" class="btn-primary text-sm">Sign In</a>
			{/if}
		</div>
	</div>
</nav>
