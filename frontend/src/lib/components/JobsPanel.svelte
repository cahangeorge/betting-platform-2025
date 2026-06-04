<script lang="ts">
	import { jobsApi } from '$lib/api/jobs';
	import { ApiClientError } from '$lib/api/client';
	import type { ScheduledJob } from '$lib/types';
	import Button from './ui/Button.svelte';
	import Card from './ui/Card.svelte';
	import Badge from './ui/Badge.svelte';
	import Loading from './Loading.svelte';

	let jobs = $state<ScheduledJob[]>([]);
	let loading = $state(true);
	let error = $state('');

	async function loadJobs() {
		loading = true;
		error = '';
		try {
			jobs = await jobsApi.getScheduledJobs();
		} catch (err) {
			error = err instanceof ApiClientError ? err.message : 'Failed to load scheduled jobs';
		} finally {
			loading = false;
		}
	}

	async function toggleJob(id: number) {
		try {
			const updated = await jobsApi.toggleJob(id);
			jobs = jobs.map((j) => (j.id === id ? updated : j));
		} catch (err) {
			error = err instanceof ApiClientError ? err.message : 'Failed to toggle job';
		}
	}

	async function deleteJob(id: number) {
		try {
			await jobsApi.deleteScheduledJob(id);
			jobs = jobs.filter((j) => j.id !== id);
		} catch (err) {
			error = err instanceof ApiClientError ? err.message : 'Failed to delete job';
		}
	}

	$effect(() => {
		loadJobs();
	});
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h2 class="text-xl font-semibold" style="color: var(--text-primary);">Scheduled Jobs</h2>
		<Button onclick={loadJobs} variant="ghost" size="sm">
			Refresh
		</Button>
	</div>

	{#if loading}
		<Loading message="Loading scheduled jobs..." />
	{:else if error}
		<div class="p-4 border text-sm" style="background-color: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3); color: var(--danger); border-radius: 0;">{error}</div>
		<Button onclick={loadJobs}>Retry</Button>
	{:else if jobs.length === 0}
		<div class="text-center py-12" style="color: var(--text-muted);">
			<p class="text-lg mb-2">No scheduled jobs</p>
			<p class="text-sm">Scheduled jobs will appear here once configured</p>
		</div>
	{:else}
		<div class="space-y-3">
			{#each jobs as job (job.id)}
				<Card>
					<div class="flex items-center justify-between">
						<div class="flex-1">
							<div class="flex items-center space-x-3">
								<h4 class="font-medium" style="color: var(--text-primary);">{job.name}</h4>
								<Badge variant={job.is_enabled ? 'success' : 'default'}>
									{job.is_enabled ? 'Enabled' : 'Disabled'}
								</Badge>
							</div>
							<div class="mt-1 flex items-center space-x-4 text-xs" style="color: var(--text-muted);">
								<span>Task: {job.task_type}</span>
								<span>Cron: <code class="font-mono" style="color: var(--accent-green);">{job.cron_expression}</code></span>
							</div>
							<div class="mt-1 flex items-center space-x-4 text-xs" style="color: var(--text-muted); opacity: 0.7;">
								<span>Last run: {job.last_run ? new Date(job.last_run).toLocaleString() : 'Never'}</span>
								<span>Next run: {job.next_run ? new Date(job.next_run).toLocaleString() : 'N/A'}</span>
							</div>
						</div>
						<div class="flex items-center space-x-2">
							<Button
								size="sm"
								variant={job.is_enabled ? 'danger' : 'primary'}
								onclick={() => toggleJob(job.id)}
							>
								{job.is_enabled ? 'Disable' : 'Enable'}
							</Button>
							<Button size="sm" variant="danger" onclick={() => deleteJob(job.id)}>
								Delete
							</Button>
						</div>
					</div>
				</Card>
			{/each}
		</div>
	{/if}
</div>
