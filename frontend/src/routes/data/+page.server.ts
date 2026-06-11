import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ cookies }) => {
	const token = cookies.get('access_token');
	if (!token) {
		redirect(302, '/login');
	}

	const apiBase = process.env.BET_API_URL || 'http://localhost:8001';

	async function fetchJson<T>(path: string, fallback: T): Promise<T> {
		try {
			const res = await fetch(`${apiBase}/api/v1${path}`, {
				headers: { 'Authorization': `Bearer ${token}` },
			});
			if (!res.ok) return fallback;
			return res.json() as Promise<T>;
		} catch (e) {
			console.error(`API fetch error for ${path}:`, e);
			return fallback;
		}
	}

	try {
		const [matchesRes, tickets, predictions] = await Promise.all([
			fetchJson('/matches', { matches: [] }),
			fetchJson('/tickets', [] as unknown[]),
			fetchJson('/predictions/runs', [] as unknown[]),
		]);

		const matches = Array.isArray(matchesRes?.matches) ? matchesRes.matches : [];

		return {
			matches,
			tickets,
			predictionRuns: predictions,
		};
	} catch (e) {
		console.error('Data page server load error:', e);
		return {
			matches: [],
			tickets: [],
			predictionRuns: [],
		};
	}
};
