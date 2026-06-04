<script lang="ts">
	interface OddsPoint {
		timestamp: string;
		odds: number;
	}

	let {
		history,
		width = 100,
		height = 30
	}: {
		history: OddsPoint[];
		width?: number;
		height?: number;
	} = $props();

	let svgRef = $state<SVGSVGElement | null>(null);
	let hoverX = $state<number | null>(null);
	let tooltipData = $state<{ timestamp: string; odds: number; x: number; y: number } | null>(null);

	const sorted = $derived([...history].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()));

	const values = $derived(sorted.map((p) => p.odds));
	const minOdds = $derived(Math.min(...values, Infinity));
	const maxOdds = $derived(Math.max(...values, -Infinity));
	const range = $derived(maxOdds - minOdds || 1);

	const points = $derived(
		sorted.map((p, i) => {
			const x = (i / (sorted.length - 1 || 1)) * width;
			const y = height - ((p.odds - minOdds) / range) * (height - 4) - 2;
			return { x, y, ...p };
		})
	);

	const firstOdds = $derived(values[0] ?? 0);
	const lastOdds = $derived(values[values.length - 1] ?? 0);
	const isTrendingDown = $derived(lastOdds < firstOdds);
	const lineColor = $derived(isTrendingDown ? 'var(--accent-green)' : 'var(--danger)');

	const pathD = $derived(() => {
		if (points.length < 2) return '';
		let d = `M ${points[0].x} ${points[0].y}`;
		for (let i = 1; i < points.length; i++) {
			const prev = points[i - 1];
			const curr = points[i];
			const cp1x = prev.x + (curr.x - prev.x) * 0.5;
			const cp1y = prev.y;
			const cp2x = prev.x + (curr.x - prev.x) * 0.5;
			const cp2y = curr.y;
			d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${curr.x} ${curr.y}`;
		}
		return d;
	});

	function handleMouseMove(e: MouseEvent) {
		if (!svgRef || points.length === 0) return;
		const rect = svgRef.getBoundingClientRect();
		const x = e.clientX - rect.left;
		hoverX = x;

		const closest = points.reduce((best, p) =>
			Math.abs(p.x - x) < Math.abs(best.x - x) ? p : best,
			points[0]
		);

		if (closest) {
			tooltipData = {
				timestamp: closest.timestamp,
				odds: closest.odds,
				x: closest.x,
				y: closest.y
			};
		}
	}

	function handleMouseLeave() {
		hoverX = null;
		tooltipData = null;
	}

	const directionArrow = $derived(isTrendingDown ? '▲' : '▼');
	const directionColor = $derived(isTrendingDown ? 'var(--accent-green)' : 'var(--danger)');
</script>

<div class="relative inline-block">
	<svg
		bind:this={svgRef}
		{width}
		{height}
		class="overflow-visible"
		onmousemove={handleMouseMove}
		onmouseleave={handleMouseLeave}
		style="cursor: crosshair;"
	>
		<!-- Subtle background -->
		<rect x="0" y="0" {width} {height} fill="var(--bg-deep)" opacity="0.3" />

		{#if points.length >= 2}
			<!-- Sparkline path -->
			<path
				d={pathD()}
				fill="none"
				stroke={lineColor}
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
			/>

			<!-- Hover indicator -->
			{#if hoverX !== null && tooltipData}
				<circle
					cx={tooltipData.x}
					cy={tooltipData.y}
					r="3"
					fill={lineColor}
					stroke="var(--bg-surface)"
					stroke-width="1"
				/>
				<line
					x1={tooltipData.x}
					y1="0"
					x2={tooltipData.x}
					y2={height}
					stroke={lineColor}
					stroke-width="1"
					opacity="0.3"
					stroke-dasharray="2 2"
				/>
			{/if}
		{/if}
	</svg>

	<!-- Direction indicator -->
	{#if points.length > 1}
		<span
			class="ml-1 text-[10px] font-mono"
			style="color: {directionColor}; font-family: 'JetBrains Mono', monospace;"
		>
			{directionArrow}
		</span>
	{/if}

	<!-- Tooltip -->
	{#if tooltipData}
		<div
			class="absolute z-10 px-2 py-1 text-[10px] font-mono whitespace-nowrap pointer-events-none"
			style="left: {Math.min(tooltipData.x + 8, width - 80)}px; top: -28px; background: var(--bg-surface); border: 1px solid var(--border-active); color: var(--text-primary); font-family: 'JetBrains Mono', monospace; box-shadow: 0 0 8px rgba(0,0,0,0.2);"
		>
			{new Date(tooltipData.timestamp).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })} — {tooltipData.odds.toFixed(2)}
		</div>
	{/if}
</div>
