<script lang="ts">
	let {
		value,
		label,
		type = 'text',
		placeholder = '',
		error,
		disabled = false,
		name,
		...rest
	}: {
		value: string;
		label?: string;
		type?: string;
		placeholder?: string;
		error?: string;
		disabled?: boolean;
		name?: string;
	} = $props();
</script>

<div class="space-y-1.5">
	{#if label}
		<label for={name} class="label">{label}</label>
	{/if}
	<input
		{type}
		{name}
		{placeholder}
		{disabled}
		bind:value
		class={error ? 'input-error' : 'input'}
		{...rest}
	/>
	{#if error}
		<p class="text-xs mt-1" style="color: var(--danger);">{error}</p>
	{/if}
</div>
