<script lang="ts">
	import { page } from '$app/stores';
	import { authApi } from '$lib/api/auth';
	import { Menu, Activity } from 'lucide-svelte';
	import { cn } from '$lib/utils';
	import Button from './ui/Button.svelte';
	import { ThemeToggle } from './ui/theme-toggle';
	import {
		DropdownMenuRoot,
		DropdownMenuTrigger,
		DropdownMenuContent,
		DropdownMenuItem,
		DropdownMenuSeparator,
		DropdownMenuLabel
	} from './ui/dropdown-menu';

	let {
		user,
		onToggleSidebar
	}: {
		user: { name: string; email: string } | null;
		onToggleSidebar: () => void;
	} = $props();

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
	class="fixed top-0 left-0 right-0 z-50 h-16 border-b border-border bg-background/80 backdrop-blur-xl"
	aria-label="Main navigation bar"
>
	<div class="flex items-center justify-between h-full px-4 lg:px-6">
		<div class="flex items-center space-x-4">
			<Button
				variant="ghost"
				size="sm"
				class="lg:hidden p-2"
				onclick={onToggleSidebar}
				aria-label="Toggle sidebar"
			>
				<Menu class="w-5 h-5 text-muted-foreground" />
			</Button>
			<a href="/" class="flex items-center space-x-3">
				<span class="text-lg font-extrabold tracking-tight hidden sm:inline text-foreground font-sport tracking-wider">
					Betfront
				</span>
			</a>
		</div>

		<div class="flex items-center space-x-4">
			<ThemeToggle />

			<div class="hidden md:flex items-center space-x-3">
				<Activity class="w-3 h-3 {connected ? 'text-football-green' : 'text-destructive'}" />
				<span class="text-xs font-mono text-muted-foreground">{timeStr}</span>
			</div>

			{#if user}
				<DropdownMenuRoot>
					<DropdownMenuTrigger class="flex items-center space-x-2 p-1.5  border border-border transition-colors hover:bg-muted">
						<div class="w-7 h-7 flex items-center justify-center text-xs font-bold  bg-muted text-football-green">
							{user.name.charAt(0).toUpperCase()}
						</div>
						<span class="text-sm hidden md:block text-foreground">{user.name}</span>
					</DropdownMenuTrigger>
					<DropdownMenuContent class="w-56" align="end">
						<DropdownMenuLabel>
							<p class="text-sm font-medium text-foreground">{user.name}</p>
							<p class="text-xs text-muted-foreground">{user.email}</p>
						</DropdownMenuLabel>
						<DropdownMenuSeparator />
						<DropdownMenuItem>
							<a href="/account" class="block w-full text-sm text-muted-foreground hover:text-foreground transition-colors">
								Account
							</a>
						</DropdownMenuItem>
						<DropdownMenuItem>
							<button
								class="w-full text-left text-sm text-destructive hover:text-destructive/80 transition-colors"
								onclick={handleLogout}
							>
								Sign Out
							</button>
						</DropdownMenuItem>
					</DropdownMenuContent>
				</DropdownMenuRoot>
			{:else}
				<a href="/login">
					<Button size="sm">Sign In</Button>
				</a>
			{/if}
		</div>
	</div>
</nav>
