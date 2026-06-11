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
		} catch {
			return fallback;
		}
	}

	const [bankrolls, accounts, ledger] = await Promise.all([
		fetchJson('/bankroll', []),
		fetchJson('/bankroll/1/accounts', []),
		fetchJson('/bankroll/1/ledger', []),
	]);

	return {
		bankrolls,
		accounts,
		ledger,
	};
};
