import { ApiClient } from './client';
import type { Match, MatchFilter } from '$lib/types';

class MatchesApi extends ApiClient {
	async getMatches(filter?: MatchFilter): Promise<Match[]> {
		const params = new URLSearchParams();
		if (filter?.league) params.set('league', filter.league);
		if (filter?.status) params.set('status', filter.status);
		if (filter?.date_from) params.set('date_from', filter.date_from);
		if (filter?.date_to) params.set('date_to', filter.date_to);
		const qs = params.toString();
		return this.get<Match[]>(`/matches${qs ? `?${qs}` : ''}`);
	}

	async getMatch(id: number): Promise<Match> {
		return this.get<Match>(`/matches/${id}`);
	}

	async getOdds(matchId: number): Promise<Match['odds']> {
		return this.get<Match['odds']>(`/matches/${matchId}/odds`);
	}

	async getLeagues(): Promise<string[]> {
		return this.get<string[]>('/matches/leagues');
	}
}

export const matchesApi = new MatchesApi();
