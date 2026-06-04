<script lang="ts">
	let {
		children,
		title,
		padded = true,
		variant = 'default',
		interactive = false,
		class: className = ''
	}: {
		children: import('svelte').Snippet;
		title?: string;
		padded?: boolean;
		variant?: 'default' | 'active' | 'data' | 'prediction';
		interactive?: boolean;
		class?: string;
	} = $props();

	let classes = $derived([
		'card',
		variant === 'active' ? 'card-glow-cyan' : '',
		variant === 'data' ? 'card-glow-violet' : '',
		variant === 'prediction' ? 'card-glow-violet' : '',
		interactive ? 'card-interactive' : '',
		className
	].filter(Boolean).join(' '));

	let topBorder = $derived(() => {
		switch (variant) {
			case 'active': return '2px solid var(--accent-green)';
			case 'data': return '2px solid var(--accent-blue)';
			case 'prediction': return '2px solid var(--accent-gold)';
			default: return 'none';
		}
	});

	let topShadow = $derived(() => {
		switch (variant) {
			case 'active': return '0 0 40px rgba(74,222,128,0.06)';
			default: return 'none';
		}
	});
</script>

<div class={classes} style="border-top: {topBorder()}; box-shadow: {topShadow()};">
	{#if title}
		<div class="px-5 py-4 border-b flex items-center justify-between" style="border-color: var(--border-subtle);">
			<h3 class="text-lg font-semibold" style="color: var(--text-primary);">{title}</h3>
		</div>
	{/if}
	<div class={padded ? 'p-5' : ''}>
		{@render children()}
	</div>
</div>
