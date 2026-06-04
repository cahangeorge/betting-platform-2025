<script lang="ts">
	import TicketsPanel from '$lib/components/TicketsPanel.svelte';
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-extrabold font-sport" style="color: var(--text-primary);">TICKETS</h1>
		<p class="mt-1" style="color: var(--text-secondary);">Place bets, track active tickets, and review betting history</p>
	</div>

	<TicketsPanel />
</div>
