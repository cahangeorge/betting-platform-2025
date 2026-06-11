import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ cookies }) => {
	const token = cookies.get('access_token');
	if (!token) {
		redirect(302, '/login');
	}

	const apiBase = process.env.BET_API_URL || 'http://localhost:8001';

	async function apiFetch<T>(path: string, fallback: T): Promise<T> {
		try {
			const res = await fetch(`${apiBase}/api/v1${path}`, {
				headers: { 'Authorization': `Bearer ${token}` }
			});
			if (!res.ok) return fallback;
			return res.json() as Promise<T>;
		} catch {
			return fallback;
		}
	}

	const [tickets, matches, stats] = await Promise.all([
		apiFetch('/tickets', []),
		apiFetch('/matches?status=scheduled', { matches: [] }),
		apiFetch('/tickets/stats', { total: 0, won: 0, lost: 0, profit_loss: 0 })
	]);

	return {
		tickets,
		matches: matches.matches ?? [],
		stats
	};
};
