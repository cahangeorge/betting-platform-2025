<script lang="ts">
	import { dataApi } from '$lib/api/data';
	import { ApiClientError } from '$lib/api/client';
	import type { ScrapeJob, Dataset, League, JobType } from '$lib/types';
	import Button from './ui/Button.svelte';
	import Card from './ui/Card.svelte';
	import Tabs from './ui/Tabs.svelte';
	import Select from './ui/Select.svelte';
	import Badge from './ui/Badge.svelte';
	import Loading from './Loading.svelte';

	let jobs = $state<ScrapeJob[]>([]);
	let datasets = $state<Dataset[]>([]);
	let leagues = $state<League[]>([]);
	let loading = $state(true);
	let error = $state('');
	let activeTab = $state('jobs');
	let pollInterval = $state<ReturnType<typeof setInterval> | null>(null);

	// New job form
	let showNewJob = $state(false);
	let newJobType = $state<JobType>('scrape_odds');
	let newJobParams = $state('{}');
	let newJobError = $state('');
	let newJobSubmitting = $state(false);

	const statusBadge: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
		completed: 'success',
		running: 'warning',
		queued: 'info',
		failed: 'danger',
		cancelled: 'default'
	};

	async function loadData() {
		try {
			const [j, d, l] = await Promise.all([
				dataApi.getJobs(),
				dataApi.getDatasets(),
				dataApi.getLeagues()
			]);
			jobs = j;
			datasets = d;
			leagues = l;
		} catch (err) {
			error = err instanceof ApiClientError ? err.message : 'Failed to load data';
		} finally {
			loading = false;
		}
	}

	async function createJob() {
		newJobSubmitting = true;
		newJobError = '';
		try {
			let params: Record<string, unknown> = {};
			try { params = JSON.parse(newJobParams); } catch { /* use empty */ }
			const job = await dataApi.createJob({ type: newJobType, params });
			jobs = [job, ...jobs];
			showNewJob = false;
			newJobParams = '{}';
		} catch (err) {
			newJobError = err instanceof ApiClientError ? err.message : 'Failed to create job';
		} finally {
			newJobSubmitting = false;
		}
	}

	async function cancelJob(id: number) {
		try {
			const job = await dataApi.cancelJob(id);
			jobs = jobs.map((j) => (j.id === id ? job : j));
		} catch (err) {
			// Silently handle
		}
	}

	$effect(() => {
		loadData();
		pollInterval = setInterval(loadData, 5000);
		return () => {
			if (pollInterval) clearInterval(pollInterval);
		};
	});

	const tabs = $derived([
		{ id: 'jobs', label: 'Scrape Jobs', count: jobs.length },
		{ id: 'datasets', label: 'Datasets', count: datasets.length },
		{ id: 'leagues', label: 'League Catalog', count: leagues.length }
	]);

	const jobTypeOptions = [
		{ value: 'scrape_odds', label: 'Scrape Odds' },
		{ value: 'scrape_results', label: 'Scrape Results' },
		{ value: 'scrape_league', label: 'Scrape League' },
		{ value: 'sync_data', label: 'Sync Data' }
	];

	function formatBytes(bytes: number): string {
		if (bytes === 0) return '0 B';
		const k = 1024;
		const sizes = ['B', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
	}
</script>

<div class="space-y-6">
	{#if loading && jobs.length === 0}
		<Loading message="Loading data module..." />
	{:else if error}
		<div class="p-4 border text-sm" style="background-color: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3); color: var(--danger); border-radius: 0;">{error}</div>
		<Button onclick={loadData}>Retry</Button>
	{:else}
		<Tabs bind:activeTab {tabs}>
			{#if activeTab === 'jobs'}
				<div class="space-y-4">
					{#if showNewJob}
						<div class="card p-4" style="border-top: 2px solid var(--accent-blue);">
							<h3 class="text-lg font-semibold mb-4" style="color: var(--text-primary);">New Scrape Job</h3>
							<form onsubmit={(e) => { e.preventDefault(); createJob(); }} class="space-y-4">
								{#if newJobError}
									<div class="p-3 text-sm" style="background-color: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: var(--danger); border-radius: 0;">{newJobError}</div>
								{/if}
								<Select
									label="Job Type"
									bind:value={newJobType}
									options={jobTypeOptions}
								/>
								<div>
									<p class="label">Parameters (JSON)</p>
									<textarea
										bind:value={newJobParams}
										class="input font-mono text-xs h-24 resize-none"
										placeholder={`{"league": "EPL", "season": "2024/2025"}`}
									></textarea>
								</div>
								<div class="flex space-x-2">
									<Button type="submit" disabled={newJobSubmitting}>
										{newJobSubmitting ? 'Creating...' : 'Create Job'}
									</Button>
									<Button variant="ghost" onclick={() => (showNewJob = false)}>Cancel</Button>
								</div>
							</form>
						</div>
					{:else}
						<Button onclick={() => (showNewJob = true)} variant="secondary">
							+ New Scrape Job
						</Button>
					{/if}

					{#if jobs.length === 0}
						<p class="text-center py-8" style="color: var(--text-muted);">No jobs created yet</p>
					{:else}
						<div class="space-y-3">
							{#each jobs as job (job.id)}
								<Card>
									<div class="flex items-center justify-between">
										<div class="flex items-center space-x-3">
											<Badge variant={statusBadge[job.status] || 'default'}>{job.status}</Badge>
											<span class="text-sm font-medium" style="color: var(--text-primary);">{job.type.replace('_', ' ')}</span>
										</div>
										<div class="flex items-center space-x-3">
											{#if job.status === 'running' || job.status === 'queued'}
												<div class="w-24 h-1.5" style="background: var(--bg-elevated);">
													<div class="h-1.5 transition-all" style="width: {job.progress}%; background: var(--accent-green);"></div>
												</div>
												<Button size="sm" variant="danger" onclick={() => cancelJob(job.id)}>Cancel</Button>
											{/if}
											<span class="text-xs" style="color: var(--text-muted);">{new Date(job.created_at).toLocaleString()}</span>
										</div>
									</div>
									{#if job.error}
										<div class="mt-2 p-2 text-xs" style="background-color: rgba(239, 68, 68, 0.1); color: var(--danger); border-radius: 0;">{job.error}</div>
									{/if}
								</Card>
							{/each}
						</div>
					{/if}
				</div>

			{:else if activeTab === 'datasets'}
				{#if datasets.length === 0}
					<p class="text-center py-8" style="color: var(--text-muted);">No datasets available</p>
				{:else}
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						{#each datasets as ds (ds.id)}
							<Card>
								<div class="space-y-2">
									<h4 class="font-medium" style="color: var(--text-primary);">{ds.name}</h4>
									<div class="flex items-center space-x-2 text-xs" style="color: var(--text-muted);">
										<Badge>{ds.source}</Badge>
										<span>{ds.league}</span>
										<span>{ds.season}</span>
									</div>
									<div class="flex justify-between text-sm" style="color: var(--text-secondary);">
										<span>{ds.row_count.toLocaleString()} rows</span>
										<span>{formatBytes(ds.size_bytes)}</span>
									</div>
									<p class="text-xs" style="color: var(--text-muted);">{ds.columns.length} columns</p>
								</div>
							</Card>
						{/each}
					</div>
				{/if}

			{:else if activeTab === 'leagues'}
				{#if leagues.length === 0}
					<p class="text-center py-8" style="color: var(--text-muted);">No leagues configured</p>
				{:else}
					<div class="overflow-x-auto">
						<table class="w-full text-sm">
							<thead class="text-xs uppercase" style="background-color: var(--bg-surface); border-bottom: 1px solid var(--border-subtle); color: var(--text-secondary); font-family: var(--font-body);">
								<tr>
									<th class="px-4 py-3 text-left">Name</th>
									<th class="px-4 py-3 text-left">Country</th>
									<th class="px-4 py-3 text-left">Sport</th>
									<th class="px-4 py-3 text-left">Status</th>
								</tr>
							</thead>
							<tbody>
								{#each leagues as league (league.id)}
									<tr class="transition-colors duration-200" style="border-bottom: 1px solid var(--border-subtle);">
										<td class="px-4 py-3 font-medium" style="color: var(--text-primary);">{league.name}</td>
										<td class="px-4 py-3" style="color: var(--text-muted);">{league.country}</td>
										<td class="px-4 py-3" style="color: var(--text-muted);">{league.sport}</td>
										<td class="px-4 py-3">
											<Badge variant={league.is_active ? 'success' : 'default'}>
												{league.is_active ? 'Active' : 'Inactive'}
											</Badge>
										</td>
									</tr>
								{:else}
										<tr>
											<td colspan="4" class="px-4 py-8 text-center" style="color: var(--text-muted);">No leagues found</td>
										</tr>
									{/each}
							</tbody>
						</table>
					</div>
				{/if}
			{/if}
		</Tabs>
	{/if}
</div>

<style>
	tbody tr:hover {
		background-color: var(--bg-elevated);
	}
</style>
