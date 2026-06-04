<script lang="ts">
	interface LiveMatchStats {
		possession_home: number;
		possession_away: number;
		shots_home: number;
		shots_away: number;
		xg_home: number;
		xg_away: number;
	}

	interface LiveMatch {
		id: number;
		home_team: string;
		away_team: string;
		home_score: number;
		away_score: number;
		minute: number;
		status: 'live' | 'ht' | 'ft';
		stats: LiveMatchStats;
	}

	let {
		match
	}: {
		match: LiveMatch;
	} = $props();

	let expanded = $state(false);
	let now = $state(new Date());

	$effect(() => {
		const interval = setInterval(() => {
			now = new Date();
		}, 30000);
		return () => clearInterval(interval);
	});

	const timeDisplay = $derived(
		match.status === 'ht'
			? 'HT'
			: match.status === 'ft'
				? 'FT'
				: `${match.minute}'`
	);

	const isLive = $derived(match.status === 'live');

	const momentum = $derived(() => {
		const homeScore = match.home_score;
		const awayScore = match.away_score;
		const homeXg = match.stats.xg_home;
		const awayXg = match.stats.xg_away;
		const homeShots = match.stats.shots_home;
		const awayShots = match.stats.shots_away;

		const homeMomentum = homeXg * 2 + homeShots * 0.5 + homeScore * 3;
		const awayMomentum = awayXg * 2 + awayShots * 0.5 + awayScore * 3;
		const total = homeMomentum + awayMomentum;

		if (total === 0) return { side: 'neutral' as const, ratio: 0.5 };
		const ratio = homeMomentum / total;
		if (ratio > 0.55) return { side: 'home' as const, ratio };
		if (ratio < 0.45) return { side: 'away' as const, ratio };
		return { side: 'neutral' as const, ratio };
	});

	const mom = $derived(momentum());

	const totalShots = $derived(match.stats.shots_home + match.stats.shots_away || 1);
	const totalXg = $derived(match.stats.xg_home + match.stats.xg_away || 1);
</script>

<div
	class="relative overflow-hidden transition-all duration-200"
	style="background: var(--bg-surface); border: 1px solid var(--border-subtle); cursor: pointer;"
	onclick={() => (expanded = !expanded)}
	style:box-shadow={
		mom.side === 'home'
			? 'inset 4px 0 12px rgba(74, 222, 128, 0.1)'
			: mom.side === 'away'
				? 'inset -4px 0 12px rgba(56, 189, 248, 0.1)'
				: 'none'
	}
>
	<!-- Main scoreboard row -->
	<div class="flex items-center justify-between px-4 py-3">
		<!-- Home -->
		<div class="flex items-center gap-3 flex-1 min-w-0">
			<span class="text-xs font-medium truncate font-sport" style="color: var(--text-primary);">
				{match.home_team}
			</span>
			<span
				class="text-2xl font-bold"
				style="color: {mom.side === 'home' ? 'var(--accent-green)' : 'var(--text-primary)'}; font-family: 'JetBrains Mono', monospace;"
			>
				{match.home_score}
			</span>
		</div>

		<!-- Center: time + live dot -->
		<div class="flex flex-col items-center gap-1 px-4">
			<div class="flex items-center gap-2">
				{#if isLive}
					<span
						class="relative flex h-2.5 w-2.5"
					>
						<span
							class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
							style="background-color: var(--accent-green);"
						></span>
						<span
							class="relative inline-flex rounded-full h-2.5 w-2.5"
							style="background-color: var(--accent-green);"
						></span>
					</span>
				{/if}
				<span
					class="text-sm font-mono font-bold"
					style="color: {isLive ? 'var(--accent-green)' : 'var(--text-secondary)'}; font-family: 'JetBrains Mono', monospace;"
				>
					{timeDisplay}
				</span>
			</div>
		</div>

		<!-- Away -->
		<div class="flex items-center gap-3 flex-1 min-w-0 justify-end">
			<span
				class="text-2xl font-bold"
				style="color: {mom.side === 'away' ? 'var(--accent-blue)' : 'var(--text-primary)'}; font-family: 'JetBrains Mono', monospace;"
			>
				{match.away_score}
			</span>
			<span class="text-xs font-medium truncate text-right font-sport" style="color: var(--text-primary);">
				{match.away_team}
			</span>
		</div>
	</div>

	<!-- Momentum bar -->
	<div class="px-4 pb-2">
		<div class="flex items-center gap-2">
			<div class="flex-1 h-1 flex">
				<div
					class="h-full transition-all duration-500"
					style="width: {mom.ratio * 100}%; background: {mom.side === 'home' ? 'var(--accent-green)' : mom.side === 'neutral' ? 'var(--border-subtle)' : 'transparent'};"
				></div>
				<div
					class="h-full transition-all duration-500"
					style="width: {(1 - mom.ratio) * 100}%; background: {mom.side === 'away' ? 'var(--accent-blue)' : mom.side === 'neutral' ? 'var(--border-subtle)' : 'transparent'};"
				></div>
			</div>
		</div>
	</div>

	<!-- Expanded stats -->
	{#if expanded}
		<div class="px-4 pb-3 space-y-2 border-t" style="border-color: var(--border-subtle);">
			<!-- Possession -->
			<div class="pt-2">
				<div class="flex items-center justify-between mb-1">
					<span class="text-[10px] font-mono" style="color: var(--accent-green); font-family: 'JetBrains Mono', monospace;">
						{match.stats.possession_home}%
					</span>
					<span class="text-[10px] font-mono" style="color: var(--text-secondary); font-family: 'JetBrains Mono', monospace;">Possession</span>
					<span class="text-[10px] font-mono" style="color: var(--accent-blue); font-family: 'JetBrains Mono', monospace;">
						{match.stats.possession_away}%
					</span>
				</div>
				<div class="flex h-1">
					<div
						class="h-full"
						style="width: {match.stats.possession_home}%; background: var(--accent-green);"
					></div>
					<div
						class="h-full"
						style="width: {match.stats.possession_away}%; background: var(--accent-blue);"
					></div>
				</div>
			</div>

			<!-- Shots -->
			<div>
				<div class="flex items-center justify-between mb-1">
					<span class="text-[10px] font-mono" style="color: var(--accent-green); font-family: 'JetBrains Mono', monospace;">
						{match.stats.shots_home}
					</span>
					<span class="text-[10px] font-mono" style="color: var(--text-secondary); font-family: 'JetBrains Mono', monospace;">Shots</span>
					<span class="text-[10px] font-mono" style="color: var(--accent-blue); font-family: 'JetBrains Mono', monospace;">
						{match.stats.shots_away}
					</span>
				</div>
				<div class="flex h-1">
					<div
						class="h-full"
						style="width: {(match.stats.shots_home / totalShots) * 100}%; background: var(--accent-green);"
					></div>
					<div
						class="h-full"
						style="width: {(match.stats.shots_away / totalShots) * 100}%; background: var(--accent-blue);"
					></div>
				</div>
			</div>

			<!-- xG -->
			<div>
				<div class="flex items-center justify-between mb-1">
					<span class="text-[10px] font-mono" style="color: var(--accent-green); font-family: 'JetBrains Mono', monospace;">
						{match.stats.xg_home.toFixed(2)}
					</span>
					<span class="text-[10px] font-mono" style="color: var(--text-secondary); font-family: 'JetBrains Mono', monospace;">xG</span>
					<span class="text-[10px] font-mono" style="color: var(--accent-blue); font-family: 'JetBrains Mono', monospace;">
						{match.stats.xg_away.toFixed(2)}
					</span>
				</div>
				<div class="flex h-1">
					<div
						class="h-full"
						style="width: {(match.stats.xg_home / totalXg) * 100}%; background: var(--accent-green);"
					></div>
					<div
						class="h-full"
						style="width: {(match.stats.xg_away / totalXg) * 100}%; background: var(--accent-blue);"
					></div>
				</div>
			</div>
		</div>
	{/if}
</div>
