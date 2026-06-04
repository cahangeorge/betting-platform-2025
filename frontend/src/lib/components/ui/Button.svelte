<script lang="ts">
	let {
		children,
		variant = 'primary',
		size = 'md',
		disabled = false,
		type = 'button',
		fullWidth = false,
		onclick,
		...rest
	}: {
		children: import('svelte').Snippet;
		variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'glow';
		size?: 'sm' | 'md' | 'lg';
		disabled?: boolean;
		type?: 'button' | 'submit' | 'reset';
		fullWidth?: boolean;
		onclick?: (e: MouseEvent) => void;
	} = $props();

	const variantClasses: Record<string, string> = {
		primary: 'btn-primary',
		secondary: 'btn-secondary',
		danger: 'btn-danger',
		ghost: 'btn-ghost',
		glow: 'btn-glow'
	};

	const sizeClasses: Record<string, string> = {
		sm: 'px-3 py-1.5 text-xs',
		md: 'px-4 py-2 text-sm',
		lg: 'px-6 py-3 text-base'
	};

	let classes = $derived([
		variantClasses[variant],
		sizeClasses[size],
		fullWidth ? 'w-full' : ''
	].filter(Boolean).join(' '));
</script>

<button {type} {disabled} class={classes} {onclick} {...rest}>
	{@render children()}
</button>
