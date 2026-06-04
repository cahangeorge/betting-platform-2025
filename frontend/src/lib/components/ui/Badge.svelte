<script lang="ts">
	let {
		children,
		variant = 'default'
	}: {
		children: import('svelte').Snippet;
		variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'live' | 'premium' | 'profit' | 'loss' | 'neutral';
	} = $props();

	const variantClasses: Record<string, string> = {
		default: 'badge',
		success: 'badge-success',
		warning: 'badge-warning',
		danger: 'badge-danger',
		info: 'badge-info',
		live: 'badge-live',
		premium: 'badge-premium',
		profit: 'badge-profit',
		loss: 'badge-loss',
		neutral: 'badge'
	};
</script>

<span class={variantClasses[variant]}>
	{@render children()}
</span>
