<script lang="ts">
	import { predictionsApi } from '$lib/api/predictions';
	import { matchesApi } from '$lib/api/matches';
	import { ApiClientError } from '$lib/api/client';
	import type { PredictionRun, PredictionModel, Match, ModelType } from '$lib/types';
	import Button from './ui/Button.svelte';
	import Card from './ui/Card.svelte';
	import Tabs from './ui/Tabs.svelte';
	import Select from './ui/Select.svelte';
	import Badge from './ui/Badge.svelte';
	import Loading from './Loading.svelte';

	let runs = $state<PredictionRun[]>([]);
	let models = $state<PredictionModel[]>([]);
	let matches = $state<Match[]>([]);
	let loading = $state(true);
	let submitting = $state(false);
	let error = $state('');
	let activeTab = $state('all');
	let pollInterval = $state<ReturnType<typeof setInterval> | null>(null);

	// Run form
	let selectedModel = $state('');
	let selectedMatchIds = $state<number[]>([]);
	let backtestFrom = $state('');
	let backtestTo = $state('');
	let formError = $state('');

	const statusBadge: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
		completed: 'success',
		running: 'warning',
		pending: 'info',
		failed: 'danger'
	};

	const modelAccent: Record<string, string> = {
		poisson: 'var(--accent-green)',
		bivariate_poisson: 'var(--accent-green)',
		dixon_coles: 'var(--accent-blue)',
		elo: 'var(--accent-blue)',
		xgboost: 'var(--accent-violet)',
		ensemble: 'var(--accent-gold)'
	};

	async function loadData() {
		try {
			const [r, m, mt] = await Promise.all([
				predictionsApi.getRuns(),
				predictionsApi.getModels(),
				matchesApi.getMatches({ status: 'scheduled' })
			]);
			runs = r;
			models = m;
			matches = mt;
			if (!selectedModel && m.length > 0) selectedModel = m[0].type;
		} catch (err) {
			error = err instanceof ApiClientError ? err.message : 'Failed to load predictions';
		} finally {
			loading = false;
		}
	}

	async function submitRun() {
		if (!selectedModel || selectedMatchIds.length === 0) {
			formError = 'Select a model and at least one match';
			return;
		}
		submitting = true;
		formError = '';
		try {
			const run = await predictionsApi.createRun({
				model_type: selectedModel as ModelType,
				match_ids: selectedMatchIds
			});
			runs = [run, ...runs];
			activeTab = 'all';
		} catch (err) {
			formError = err instanceof ApiClientError ? err.message : 'Failed to start prediction run';
		} finally {
			submitting = false;
		}
	}

	function toggleMatch(id: number) {
		if (selectedMatchIds.includes(id)) {
			selectedMatchIds = selectedMatchIds.filter((m) => m !== id);
		} else {
			selectedMatchIds = [...selectedMatchIds, id];
		}
	}

	// Auto-refresh
	$effect(() => {
		loadData();
		pollInterval = setInterval(loadData, 5000);
		return () => {
			if (pollInterval) clearInterval(pollInterval);
		};
	});

	const tabs = $derived([
		{ id: 'all', label: 'All Runs', count: runs.length },
		{ id: 'new', label: 'Run Prediction' },
		{ id: 'backtest', label: 'Backtest' }
	]);

	const modelOptions = $derived(
		models.map((m) => ({ value: m.type, label: m.name }))
	);

	const matchOptions = $derived(
		matches.map((m) => ({
			value: String(m.id),
			label: `${m.home_team} vs ${m.away_team}`
		}))
	);
</script>

<div class="space-y-6">
	{#if error}
		<div class="p-4 border text-sm" style="background-color: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3); color: var(--danger); border-radius: 0;">{error}</div>
		<Button onclick={loadData}>Retry</Button>
	{/if}

	<Tabs bind:activeTab {tabs}>
		{#if activeTab === 'all'}
			{#if loading && runs.length === 0}
				<Loading message="Loading predictions..." />
			{:else if runs.length === 0}
				<div class="text-center py-12" style="color: var(--text-muted);">
					<p class="text-lg mb-2">No prediction runs yet</p>
					<p class="text-sm">Go to Run Prediction to start one</p>
				</div>
			{:else}
				<div class="space-y-4">
					{#each runs as run (run.id)}
						{@const accent = modelAccent[run.model_type] || 'var(--accent-green)'}
						<div class="card card-interactive p-4" style="border-top: 2px solid {accent};">
							<div class="flex items-center justify-between mb-3">
								<div class="flex items-center space-x-3">
									<h4 class="font-medium" style="color: var(--text-primary);">{run.model_type}</h4>
									<Badge variant={statusBadge[run.status] || 'default'}>{run.status}</Badge>
								</div>
								<span class="text-xs" style="color: var(--text-muted);">{new Date(run.created_at).toLocaleString()}</span>
							</div>

							{#if run.results && run.results.length > 0}
								<div class="overflow-x-auto">
									<table class="w-full text-sm">
										<thead class="text-xs uppercase" style="background-color: var(--bg-surface); border-bottom: 1px solid var(--border-subtle); color: var(--text-secondary); font-family: var(--font-body);">
											<tr>
												<th class="px-3 py-2 text-left">Match</th>
												<th class="px-3 py-2 text-center">1</th>
												<th class="px-3 py-2 text-center">X</th>
												<th class="px-3 py-2 text-center">2</th>
												<th class="px-3 py-2 text-center">Score</th>
												<th class="px-3 py-2 text-center">Confidence</th>
											</tr>
										</thead>
										<tbody>
											{#each run.results as r (r.match_id)}
												<tr class="transition-colors duration-200" style="border-bottom: 1px solid var(--border-subtle);">
													<td class="px-3 py-2" style="color: var(--text-primary);">{r.home_team} vs {r.away_team}</td>
													<td class="px-3 py-2 text-center font-mono">{(r.home_prob * 100).toFixed(1)}%</td>
													<td class="px-3 py-2 text-center font-mono">{(r.draw_prob * 100).toFixed(1)}%</td>
													<td class="px-3 py-2 text-center font-mono">{(r.away_prob * 100).toFixed(1)}%</td>
													<td class="px-3 py-2 text-center font-mono" style="color: var(--accent-green);">{r.predicted_score}</td>
													<td class="px-3 py-2 text-center">
														<div class="inline-flex items-center">
															<div class="w-16 h-1.5" style="background: var(--bg-elevated);">
																<div
																	class="h-1.5"
																	style="width: {r.confidence * 100}%; background: linear-gradient(90deg, var(--accent-green), var(--accent-blue));"
																></div>
															</div>
														</div>
													</td>
												</tr>
											{/each}
										</tbody>
									</table>
								</div>
							{:else if run.status === 'running' || run.status === 'pending'}
								<div class="flex items-center space-x-2 text-sm">
									<div class="w-4 h-4 border-2 border-t-transparent animate-spin" style="border-color: var(--accent-gold); border-top-color: transparent; border-radius: 50%;"></div>
									<span style="color: var(--accent-gold);">Running prediction...</span>
								</div>
							{/if}

							{#if run.error}
								<div class="mt-2 p-2 text-xs" style="background-color: rgba(239, 68, 68, 0.1); color: var(--danger); border-radius: 0;">{run.error}</div>
							{/if}
						</div>
					{/each}
				</div>
			{/if}

		{:else if activeTab === 'new'}
			<div class="card p-4" style="border-top: 2px solid var(--accent-green);">
				<h3 class="text-lg font-semibold mb-4" style="color: var(--text-primary);">Run Prediction</h3>
				<form onsubmit={(e) => { e.preventDefault(); submitRun(); }} class="space-y-4">
					{#if formError}
						<div class="p-3 text-sm" style="background-color: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: var(--danger); border-radius: 0;">{formError}</div>
					{/if}

					<Select
						label="Model"
						bind:value={selectedModel}
						options={modelOptions}
					/>

					{#if models.length > 0 && selectedModel}
						{@const model = models.find((m) => m.type === selectedModel)}
						{#if model}
							<p class="text-xs" style="color: var(--text-muted);">{model.description}</p>
						{/if}
					{/if}

					<div>
						<p class="label">Select Matches</p>
						<div class="max-h-48 overflow-y-auto space-y-2 border p-3 scroll-thin" style="border-color: var(--border-subtle);">
							{#each matches as m (m.id)}
								<label class="flex items-center space-x-3 cursor-pointer p-2 transition-colors duration-200" style="border-radius: 0;" class:selected-match={selectedMatchIds.includes(m.id)} onmouseenter={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-elevated)'} onmouseleave={(e) => { if (!selectedMatchIds.includes(m.id)) e.currentTarget.style.backgroundColor = 'transparent'; }}>
									<input
										type="checkbox"
										checked={selectedMatchIds.includes(m.id)}
										onchange={() => toggleMatch(m.id)}
										class="w-4 h-4"
										style="accent-color: var(--accent-green);"
									/>
									<span class="text-sm" style="color: var(--text-secondary);">{m.home_team} vs {m.away_team}</span>
									<span class="text-xs ml-auto" style="color: var(--text-muted);">{new Date(m.start_time).toLocaleDateString()}</span>
								</label>
							{:else}
								<p class="text-sm text-center py-4" style="color: var(--text-muted);">No upcoming matches available</p>
							{/each}
						</div>
					</div>

					<Button type="submit" disabled={submitting || matches.length === 0}>
						{submitting ? 'Starting...' : 'Run Prediction'}
					</Button>
				</form>
			</div>

		{:else if activeTab === 'backtest'}
			<div class="card p-4" style="border-top: 2px solid var(--accent-gold);">
				<h3 class="text-lg font-semibold mb-4" style="color: var(--text-primary);">Backtest</h3>
				<p class="text-sm mb-4" style="color: var(--text-muted);">
					Run historical backtests to evaluate model performance against past match results.
				</p>
				<form onsubmit={(e) => { e.preventDefault(); }} class="space-y-4">
					<Select
						label="Model"
						bind:value={selectedModel}
						options={modelOptions}
					/>
					<div class="grid grid-cols-2 gap-4">
						<Input label="From Date" type="date" bind:value={backtestFrom} />
						<Input label="To Date" type="date" bind:value={backtestTo} />
					</div>
					<Button type="submit">Run Backtest</Button>
				</form>
			</div>
		{/if}
	</Tabs>
</div>

<style>
	.selected-match {
		background-color: rgba(74, 222, 128, 0.05);
	}
</style>
