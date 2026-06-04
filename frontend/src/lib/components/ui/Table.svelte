<script lang="ts">
	let {
		columns,
		rows,
		loading = false,
		emptyMessage = 'No data available'
	}: {
		columns: { key: string; label: string; sortable?: boolean; class?: string }[];
		rows: Record<string, unknown>[];
		loading?: boolean;
		emptyMessage?: string;
	} = $props();
</script>

<div class="overflow-x-auto border" style="border-color: var(--border-subtle); border-radius: 0;">
	<table class="w-full text-sm text-left">
		<thead class="text-xs uppercase" style="background-color: var(--bg-surface); border-bottom: 1px solid var(--border-subtle); color: var(--text-secondary);">
			<tr>
				{#each columns as col (col.key)}
					<th scope="col" class="px-4 py-3 font-medium {col.class || ''}" style="font-family: var(--font-body);">
						{col.label}
					</th>
				{/each}
			</tr>
		</thead>
		<tbody>
			{#if loading}
				<tr>
					<td colspan={columns.length} class="px-4 py-12 text-center">
						<div class="flex items-center justify-center space-x-2">
							<div class="w-5 h-5 border-2 animate-spin-ring" style="border-color: var(--border-subtle); border-top-color: var(--accent-green);"></div>
							<span style="color: var(--text-secondary);">Loading...</span>
						</div>
					</td>
				</tr>
			{:else if rows.length === 0}
				<tr>
					<td colspan={columns.length} class="px-4 py-12 text-center" style="color: var(--text-muted);">
						{emptyMessage}
					</td>
				</tr>
			{:else}
				{#each rows as row, i (i)}
					<tr class="transition-colors duration-200" style="border-bottom: 1px solid var(--border-subtle);">
						{#each columns as col (col.key)}
							<td class="px-4 py-3 {col.class || ''}" style="color: var(--text-primary);">
								{row[col.key] as string}
							</td>
							{/each}
						</tr>
					{/each}
				{/if}
			</tbody>
		</table>
	</div>

<style>
	tbody tr:hover {
		background-color: var(--bg-elevated);
	}
</style>
