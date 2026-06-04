import type { PageLoad } from './$types';
import { matchesApi } from '$lib/api/matches';
import type { Match } from '$lib/types';

export const load: PageLoad = async (): Promise<{ matches: Match[] }> => {
	try {
		const matches = await matchesApi.getMatches({ status: 'scheduled' });
		return { matches };
	} catch {
		return { matches: [] };
	}
};
