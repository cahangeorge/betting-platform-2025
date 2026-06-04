<script lang="ts">
	let {
		value,
		label,
		options,
		placeholder = 'Select...',
		disabled = false,
		name
	}: {
		value: string;
		label?: string;
		options: { value: string; label: string }[];
		placeholder?: string;
		disabled?: boolean;
		name?: string;
	} = $props();
</script>

<div class="space-y-1.5">
	{#if label}
		<label for={name} class="label">{label}</label>
	{/if}
	<select
		{name}
		{disabled}
		bind:value
		class="input appearance-none cursor-pointer"
		style="background-image: url('data:image/svg+xml,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 fill=%27none%27 viewBox=%270 0 20 20%27%3e%3cpath stroke=%27%2364748B%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%271.5%27 d=%27M6 8l4 4 4-4%27/%3e%3c/svg%3e'); background-position: right 0.5rem center; background-repeat: no-repeat; background-size: 1.5em 1.5em; padding-right: 2.5rem;"
	>
		<option value="" disabled>{placeholder}</option>
		{#each options as opt (opt.value)}
			<option value={opt.value}>{opt.label}</option>
		{/each}
	</select>
</div>
