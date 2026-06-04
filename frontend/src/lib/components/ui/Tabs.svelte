<script lang="ts">
	let {
		tabs,
		activeTab,
		children
	}: {
		tabs: { id: string; label: string; count?: number }[];
		activeTab: string;
		children: import('svelte').Snippet;
	} = $props();
</script>

<div class="w-full">
	<div class="border-b mb-6" style="border-color: var(--border-subtle);">
		<div class="flex space-x-6 overflow-x-auto" role="tablist">
			{#each tabs as tab (tab.id)}
				<button
					role="tab"
					aria-selected={activeTab === tab.id}
					class="whitespace-nowrap pb-3 px-1 text-sm transition-all duration-200 ease-out"
					class:tab-active={activeTab === tab.id}
					class:tab-inactive={activeTab !== tab.id}
					onclick={() => (activeTab = tab.id)}
				>
					{tab.label}
					{#if tab.count !== undefined}
						<span class="ml-2 text-xs px-2 py-0.5" style="background-color: var(--bg-elevated); color: var(--text-secondary); border-radius: 0; font-family: var(--font-mono);">{tab.count}</span>
					{/if}
				</button>
			{/each}
		</div>
	</div>
	<div role="tabpanel">
		{@render children()}
	</div>
</div>
