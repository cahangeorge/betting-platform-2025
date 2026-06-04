<script lang="ts">
	import AccountPanel from '$lib/components/AccountPanel.svelte';
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-extrabold font-sport" style="color: var(--text-primary);">ACCOUNT</h1>
		<p class="mt-1" style="color: var(--text-secondary);">Manage bankrolls, bookmaker accounts, and view transaction history</p>
	</div>

	<AccountPanel />
</div>
