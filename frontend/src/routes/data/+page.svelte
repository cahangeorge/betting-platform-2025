<script lang="ts">
	import DataPanel from '$lib/components/DataPanel.svelte';
	import JobsPanel from '$lib/components/JobsPanel.svelte';
	import Tabs from '$lib/components/ui/Tabs.svelte';

	let activeTab = $state('scrape');
	const tabs = [
		{ id: 'scrape', label: 'Scrape Jobs' },
		{ id: 'scheduled', label: 'Scheduled Jobs' }
	];
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-extrabold font-sport" style="color: var(--text-primary);">DATA</h1>
		<p class="mt-1" style="color: var(--text-secondary);">Manage data scraping, browse datasets, and configure scheduled jobs</p>
	</div>

	<Tabs bind:activeTab {tabs}>
		{#if activeTab === 'scrape'}
			<DataPanel />
		{:else if activeTab === 'scheduled'}
			<JobsPanel />
		{/if}
	</Tabs>
</div>
