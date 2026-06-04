<script lang="ts">
	let {
		size = 'md',
		message = 'Loading...'
	}: {
		size?: 'sm' | 'md' | 'lg';
		message?: string;
	} = $props();

	const sizeClasses: Record<string, string> = {
		sm: 'w-5 h-5',
		md: 'w-10 h-10',
		lg: 'w-14 h-14'
	};
</script>

<div class="flex flex-col items-center justify-center space-y-3">
	<div class="relative {sizeClasses[size]}">
		<div
			class="absolute inset-0 border-2 animate-spin-ring"
			style="border-color: var(--border-subtle); border-top-color: var(--accent-green); border-radius: 4px;"
		></div>
		<div
			class="absolute inset-1 border-2 animate-spin-ring"
			style="border-color: transparent; border-top-color: var(--accent-blue); animation-direction: reverse; animation-duration: 0.8s; border-radius: 4px;"
		></div>
	</div>
	{#if message}
		<p class="text-sm font-mono" style="color: var(--text-secondary);">{message}</p>
	{/if}
</div>
