<script lang="ts">
	import { onMount } from 'svelte';
	import { fade, slide } from 'svelte/transition';
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import Skeleton from '$lib/components/ui/skeleton/skeleton.svelte';
	import Separator from '$lib/components/ui/separator/separator.svelte';
	import { cn } from '$lib/utils';
	import type { Country, ScrapeJob } from '$lib/types';

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	const BASE_URL = (import.meta as any).env?.PUBLIC_API_URL || '';

	// --- State ---
	let countries = $state<Country[]>([]);
	let allLeagues = $state<{ id: string; name: string; matches_count: number }[]>([]);
	let selectedCountries = $state<string[]>([]);
	let selectedLeagues = $state<string[]>([]);
	let loadingCatalog = $state(true);

	// Past History
	let pastEnabled = $state(true);
	let pastFrom = $state('');
	let pastTo = $state('');

	// Future Matches
	let futureEnabled = $state(true);
	let futureNumber = $state('7');
	let futureUnit = $state('Days');

	// Options
	let autoScrape = $state(false);
	let autoIntervalNumber = $state('24');
	let autoIntervalUnit = $state('Hours');
	let dedupSkip = $state(true);

	// Jobs
	let jobs = $state<ScrapeJob[]>([]);
	let loadingJobs = $state(true);
	let expandedJobId = $state<number | null>(null);

	// Submit
	let submitting = $state(false);
	let submitSuccess = $state('');
	let submitError = $state('');

	let pollTimer: ReturnType<typeof setInterval> | null = null;

	// --- Derived ---
	const filteredLeagues = $derived(
		selectedCountries.length === 0
			? allLeagues
			: countries
					.filter((c) => selectedCountries.includes(c.country))
					.flatMap((c) => c.leagues)
	);

	const selectedCountryBadges = $derived(
		selectedCountries.map((c) => ({
			value: c,
			label: c
		}))
	);

	const selectedLeagueBadges = $derived(
		selectedLeagues.map((id) => {
			const league = allLeagues.find((l) => l.id === id);
			return { value: id, label: league?.name ?? id };
		})
	);

	const unitOptions = [
		{ value: 'Days', label: 'Days' },
		{ value: 'Weeks', label: 'Weeks' },
		{ value: 'Months', label: 'Months' },
		{ value: 'Years', label: 'Years' }
	];

	const intervalUnitOptions = [
		{ value: 'Hours', label: 'Hours' },
		{ value: 'Days', label: 'Days' },
		{ value: 'Weeks', label: 'Weeks' }
	];

	// --- Data Fetching ---
	async function fetchCatalog() {
		try {
			const res = await fetch(`${BASE_URL}/api/v1/catalog/countries`, { credentials: 'include' });
			if (res.ok) {
				countries = await res.json();
				allLeagues = countries.flatMap((c) => c.leagues);
			}
		} catch {
			// silently handle — catalog may not be available yet
		} finally {
			loadingCatalog = false;
		}
	}

	async function fetchJobs() {
		try {
			const res = await fetch(`${BASE_URL}/api/v1/data/scrape`, { credentials: 'include' });
			if (res.ok) {
				jobs = await res.json();
			}
		} catch {
			// silently handle
		} finally {
			loadingJobs = false;
		}
	}

	async function startScrape() {
		submitting = true;
		submitError = '';
		submitSuccess = '';

		const params: Record<string, unknown> = {
			countries: selectedCountries,
			leagues: selectedLeagues,
			dedup_skip: dedupSkip,
			auto_scrape: autoScrape
		};

		if (pastEnabled && pastFrom && pastTo) {
			params.past_from = pastFrom;
			params.past_to = pastTo;
		}

		if (futureEnabled && futureNumber) {
			const num = parseInt(futureNumber, 10);
			const unitMap: Record<string, string> = {
				Days: 'days',
				Weeks: 'weeks',
				Months: 'months',
				Years: 'years'
			};
			params.future_days = unitMap[futureUnit] === 'days' ? num : num * (futureUnit === 'Weeks' ? 7 : futureUnit === 'Months' ? 30 : 365);
		}

		if (autoScrape) {
			const num = parseInt(autoIntervalNumber, 10) || 24;
			const unitMap: Record<string, number> = { Hours: 1, Days: 24, Weeks: 168 };
			params.auto_interval_hours = num * (unitMap[autoIntervalUnit] ?? 1);
		}

		try {
			const res = await fetch(`${BASE_URL}/api/v1/data/scrape`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify({ type: 'scrape_odds', params })
			});

			if (!res.ok) {
				const err = await res.json().catch(() => ({ detail: 'Failed to create job' }));
				throw new Error(err.detail || `HTTP ${res.status}`);
			}

			submitSuccess = 'Scrape job created successfully';
			await fetchJobs();
			setTimeout(() => (submitSuccess = ''), 4000);
		} catch (err) {
			submitError = err instanceof Error ? err.message : 'Failed to start scrape';
		} finally {
			submitting = false;
		}
	}

	function toggleCountry(country: string) {
		if (selectedCountries.includes(country)) {
			selectedCountries = selectedCountries.filter((c) => c !== country);
			const leagueIds = countries
				.find((c) => c.country === country)
				?.leagues.map((l) => l.id) ?? [];
			selectedLeagues = selectedLeagues.filter((id) => !leagueIds.includes(id));
		} else {
			selectedCountries = [...selectedCountries, country];
		}
	}

	function toggleLeague(id: string) {
		if (selectedLeagues.includes(id)) {
			selectedLeagues = selectedLeagues.filter((l) => l !== id);
		} else {
			selectedLeagues = [...selectedLeagues, id];
		}
	}

	function toggleAllLeagues() {
		const filteredIds = filteredLeagues.map((l) => l.id);
		if (filteredIds.every((id) => selectedLeagues.includes(id))) {
			selectedLeagues = selectedLeagues.filter((id) => !filteredIds.includes(id));
		} else {
			selectedLeagues = [...new Set([...selectedLeagues, ...filteredIds])];
		}
	}

	function toggleExpandJob(id: number) {
		expandedJobId = expandedJobId === id ? null : id;
	}

	function formatDuration(created: string, completed: string | null): string {
		if (!completed) return '—';
		const ms = new Date(completed).getTime() - new Date(created).getTime();
		const secs = Math.floor(ms / 1000);
		if (secs < 60) return `${secs}s`;
		const mins = Math.floor(secs / 60);
		return `${mins}m ${secs % 60}s`;
	}

	function statusVariant(status: string): 'success' | 'warning' | 'danger' | 'info' {
		const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
			completed: 'success',
			running: 'warning',
			queued: 'info',
			failed: 'danger',
			cancelled: 'danger'
		};
		return map[status] ?? 'default';
	}

	onMount(() => {
		fetchCatalog();
		fetchJobs();
		pollTimer = setInterval(fetchJobs, 10000);
		return () => {
			if (pollTimer) clearInterval(pollTimer);
		};
	});
</script>

<div class="max-w-4xl mx-auto space-y-8" transition:fade={{ duration: 200 }}>
	<div>
		<h1 class="text-2xl font-extrabold font-sport text-foreground">SCRAPING</h1>
		<p class="mt-1 text-muted-foreground">Configure and run data scraping jobs for odds and match data</p>
	</div>

	<!-- Section 1: Country / League Selectors -->
	<Card title="Data Selection" variant="data">
		<div class="space-y-6">
			<!-- Countries -->
			<div>
				<p class="text-sm font-medium text-foreground mb-3">Countries</p>
				{#if loadingCatalog}
					<div class="space-y-2">
						<Skeleton class="h-6 w-full" />
						<Skeleton class="h-6 w-3/4" />
					</div>
				{:else if countries.length === 0}
					<p class="text-sm text-muted-foreground">No countries available</p>
				{:else}
					<div class="grid grid-cols-2 md:grid-cols-3 gap-2">
						{#each countries as country (country.country)}
							<label class={cn(
								'flex items-center space-x-2 p-2 border cursor-pointer transition-colors duration-200',
								selectedCountries.includes(country.country)
									? 'border-football-green bg-football-green/5'
									: 'border-border hover:bg-muted'
							)}>
								<input
									type="checkbox"
									checked={selectedCountries.includes(country.country)}
									onchange={() => toggleCountry(country.country)}
									class="w-4 h-4 accent-[hsl(var(--football-green))]"
								/>
								<span class="text-sm text-foreground">{country.country}</span>
								<span class="text-xs text-muted-foreground ml-auto font-mono">{country.leagues.length}</span>
							</label>
						{/each}
					</div>
					{#if selectedCountryBadges.length > 0}
						<div class="flex flex-wrap gap-1.5 mt-2">
							{#each selectedCountryBadges as badge (badge.value)}
								<Badge variant="info">{badge.label}</Badge>
							{/each}
						</div>
					{/if}
				{/if}
			</div>

			<Separator />

			<!-- Leagues -->
			<div>
				<div class="flex items-center justify-between mb-3">
					<p class="text-sm font-medium text-foreground">
						Leagues
						{#if selectedCountries.length > 0}
							<span class="text-muted-foreground font-normal">(filtered)</span>
						{/if}
					</p>
					{#if filteredLeagues.length > 0}
						<button
							type="button"
							onclick={toggleAllLeagues}
							class="text-xs text-football-blue hover:text-football-green transition-colors"
						>
							{filteredLeagues.every((l) => selectedLeagues.includes(l.id)) ? 'Deselect all' : 'Select all'}
						</button>
					{/if}
				</div>
				{#if loadingCatalog}
					<div class="space-y-2">
						<Skeleton class="h-6 w-full" />
						<Skeleton class="h-6 w-2/3" />
					</div>
				{:else if filteredLeagues.length === 0}
					<p class="text-sm text-muted-foreground">No leagues available. Select a country above.</p>
				{:else}
					<div class="max-h-48 overflow-y-auto scroll-thin space-y-1 border border-border p-2">
						{#each filteredLeagues as league (league.id)}
							<label class={cn(
								'flex items-center space-x-2 p-2 cursor-pointer transition-colors duration-200',
								selectedLeagues.includes(league.id)
									? 'bg-football-green/5'
									: 'hover:bg-muted'
							)}>
								<input
									type="checkbox"
									checked={selectedLeagues.includes(league.id)}
									onchange={() => toggleLeague(league.id)}
									class="w-4 h-4 accent-[hsl(var(--football-green))]"
								/>
								<span class="text-sm text-foreground">{league.name}</span>
								<span class="text-xs text-muted-foreground ml-auto font-mono">{league.matches_count}</span>
							</label>
						{/each}
					</div>
					{#if selectedLeagueBadges.length > 0}
						<div class="flex flex-wrap gap-1.5 mt-2">
							{#each selectedLeagueBadges as badge (badge.value)}
								<Badge variant="info">{badge.label}</Badge>
							{/each}
						</div>
					{/if}
				{/if}
			</div>
		</div>
	</Card>

	<!-- Section 2: Time Period -->
	<Card title="Time Period" variant="data">
		<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<!-- Past History -->
			<div class="space-y-3">
				<div class="flex items-center justify-between">
					<p class="text-sm font-medium text-foreground">Past History</p>
					<label class="relative inline-flex items-center cursor-pointer">
						<input
							type="checkbox"
							checked={pastEnabled}
							onchange={() => (pastEnabled = !pastEnabled)}
							class="sr-only peer"
						/>
						<div class="w-9 h-5 bg-muted border border-border peer-checked:bg-football-green peer-checked:border-football-green transition-colors after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-foreground after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-full"></div>
					</label>
				</div>
				{#if pastEnabled}
					<div class="space-y-3" transition:slide={{ duration: 200 }}>
						<div>
							<label class="text-xs text-muted-foreground mb-1 block">From</label>
							<Input type="date" bind:value={pastFrom} />
						</div>
						<div>
							<label class="text-xs text-muted-foreground mb-1 block">To</label>
							<Input type="date" bind:value={pastTo} />
						</div>
					</div>
				{/if}
			</div>

			<!-- Future Matches -->
			<div class="space-y-3">
				<div class="flex items-center justify-between">
					<p class="text-sm font-medium text-foreground">Future Matches</p>
					<label class="relative inline-flex items-center cursor-pointer">
						<input
							type="checkbox"
							checked={futureEnabled}
							onchange={() => (futureEnabled = !futureEnabled)}
							class="sr-only peer"
						/>
						<div class="w-9 h-5 bg-muted border border-border peer-checked:bg-football-green peer-checked:border-football-green transition-colors after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-foreground after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-full"></div>
					</label>
				</div>
				{#if futureEnabled}
					<div class="flex items-end gap-2" transition:slide={{ duration: 200 }}>
						<div class="flex-1">
							<label class="text-xs text-muted-foreground mb-1 block">Number</label>
							<Input type="number" bind:value={futureNumber} placeholder="7" />
						</div>
						<div class="flex-1">
							<Select bind:value={futureUnit} options={unitOptions} />
						</div>
					</div>
				{/if}
			</div>
		</div>
	</Card>

	<!-- Section 3: Options -->
	<Card title="Options" variant="data">
		<div class="space-y-4">
			<!-- Auto-scrape -->
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-foreground">Auto-scrape</p>
					<p class="text-xs text-muted-foreground">Automatically run scrape jobs on a schedule</p>
				</div>
				<label class="relative inline-flex items-center cursor-pointer">
					<input
						type="checkbox"
						checked={autoScrape}
						onchange={() => (autoScrape = !autoScrape)}
						class="sr-only peer"
					/>
					<div class="w-9 h-5 bg-muted border border-border peer-checked:bg-football-green peer-checked:border-football-green transition-colors after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-foreground after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-full"></div>
				</label>
			</div>
			{#if autoScrape}
				<div class="flex items-end gap-2 pl-4 border-l-2 border-football-green/30" transition:slide={{ duration: 200 }}>
					<div class="flex-1">
						<label class="text-xs text-muted-foreground mb-1 block">Interval</label>
						<Input type="number" bind:value={autoIntervalNumber} placeholder="24" />
					</div>
					<div class="flex-1">
						<Select bind:value={autoIntervalUnit} options={intervalUnitOptions} />
					</div>
				</div>
			{/if}

			<Separator />

			<!-- Dedup -->
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-foreground">Skip existing matches</p>
					<p class="text-xs text-muted-foreground">Avoid re-scraping data already in the database</p>
				</div>
				<label class="relative inline-flex items-center cursor-pointer">
					<input
						type="checkbox"
						checked={dedupSkip}
						onchange={() => (dedupSkip = !dedupSkip)}
						class="sr-only peer"
					/>
					<div class="w-9 h-5 bg-muted border border-border peer-checked:bg-football-green peer-checked:border-football-green transition-colors after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-foreground after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-full"></div>
				</label>
			</div>
		</div>
	</Card>

	<!-- Section 4: Job Table -->
	<Card title="Jobs" variant="data">
		{#if loadingJobs}
			<div class="space-y-3">
				<Skeleton class="h-12 w-full" />
				<Skeleton class="h-12 w-full" />
				<Skeleton class="h-12 w-full" />
			</div>
		{:else if jobs.length === 0}
			<p class="text-sm text-muted-foreground text-center py-8">No scraping jobs yet</p>
		{:else}
			<div class="overflow-x-auto">
				<table class="w-full text-sm">
					<thead class="text-xs uppercase bg-muted border-b border-border text-muted-foreground">
						<tr>
							<th class="px-3 py-2 text-left">Name</th>
							<th class="px-3 py-2 text-left">Status</th>
							<th class="px-3 py-2 text-left">Created</th>
							<th class="px-3 py-2 text-left">Duration</th>
							<th class="px-3 py-2 text-left">Progress</th>
							<th class="px-3 py-2 w-8"></th>
						</tr>
					</thead>
					<tbody>
						{#each jobs as job (job.id)}
							<tr
								class="border-b border-border transition-colors duration-200 hover:bg-muted cursor-pointer"
								onclick={() => toggleExpandJob(job.id)}
							>
								<td class="px-3 py-2.5 text-foreground font-medium">
									{job.type}
								</td>
								<td class="px-3 py-2.5">
									<Badge variant={statusVariant(job.status)}>{job.status}</Badge>
								</td>
								<td class="px-3 py-2.5 text-muted-foreground font-mono text-xs">
									{new Date(job.created_at).toLocaleString()}
								</td>
								<td class="px-3 py-2.5 font-mono text-xs text-muted-foreground">
									{formatDuration(job.created_at, job.completed_at)}
								</td>
								<td class="px-3 py-2.5">
									<div class="flex items-center gap-2">
										<div class="flex-1 h-1.5 bg-muted">
											<div
												class="h-1.5 bg-football-green transition-all duration-500"
												style="width: {job.progress}%"
											></div>
										</div>
										<span class="text-xs font-mono text-muted-foreground w-8 text-right">{job.progress}%</span>
									</div>
								</td>
								<td class="px-3 py-2.5 text-muted-foreground">
									<span class="text-xs">{expandedJobId === job.id ? '▲' : '▼'}</span>
								</td>
							</tr>
							{#if expandedJobId === job.id}
								<tr transition:slide={{ duration: 200 }}>
									<td colspan="6" class="px-3 py-3 bg-muted/50">
										<div class="grid grid-cols-2 gap-4 text-xs">
											<div>
												<span class="text-muted-foreground">Job ID:</span>
												<span class="ml-2 font-mono text-foreground">{job.id}</span>
											</div>
											<div>
												<span class="text-muted-foreground">Type:</span>
												<span class="ml-2 font-mono text-foreground">{job.type}</span>
											</div>
											{#if job.error}
												<div class="col-span-2">
													<span class="text-destructive">{job.error}</span>
												</div>
											{/if}
											{#if job.params && Object.keys(job.params).length > 0}
												<div class="col-span-2">
													<span class="text-muted-foreground">Params:</span>
													<pre class="mt-1 p-2 bg-background border border-border font-mono text-xs overflow-x-auto">{JSON.stringify(job.params, null, 2)}</pre>
												</div>
											{/if}
										</div>
									</td>
								</tr>
							{/if}
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</Card>

	<!-- Section 5: Action -->
	<div class="space-y-4">
		{#if submitSuccess}
			<div class="p-3 text-sm bg-football-green/10 border border-football-green/30 text-football-green" transition:slide={{ duration: 200 }}>
									{submitSuccess}
			</div>
		{/if}
		{#if submitError}
			<div class="p-3 text-sm bg-destructive/10 border border-destructive/30 text-destructive" transition:slide={{ duration: 200 }}>
				{submitError}
			</div>
		{/if}
		<Button
			variant="glow"
			size="lg"
			fullWidth
			disabled={submitting || (selectedCountries.length === 0 && selectedLeagues.length === 0)}
			onclick={startScrape}
		>
			{#if submitting}
				<span class="flex items-center justify-center gap-2">
					<span class="h-4 w-4 border-2 border-foreground border-t-transparent animate-spin"></span>
					Starting...
				</span>
			{:else}
				Start Scraping
			{/if}
		</Button>
	</div>
</div>
