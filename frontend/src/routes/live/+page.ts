import type { PageLoad } from './$types';
import { matchesApi } from '$lib/api/matches';

export const load: PageLoad = async ({ fetch }) => {
	try {
		const matches = await matchesApi.getMatches(fetch, { status: 'live' });
		return {
			matches,
			loading: false,
			lastUpdated: new Date().toISOString()
		};
	} catch (e) {
		// Demo data fallback
		return {
			matches: [
				{
					id: 201,
					league: 'Premier League',
					home_team: 'Man City',
					away_team: 'Arsenal',
					start_time: new Date(Date.now() - 3600000 * 1.2).toISOString(),
					status: 'live',
					home_score: 2,
					away_score: 1,
					minute: 78,
					possession_home: 62,
					possession_away: 38,
					shots_home: 14,
					shots_away: 7,
					xg_home: 2.34,
					xg_away: 0.89,
					momentum: 'home',
					momentum_intensity: 'strong',
					odds: [
						{ id: 1, bookmaker: 'Betfair', market: '1X2', home_odds: 1.25, draw_odds: 6.50, away_odds: 12.00, updated_at: new Date().toISOString() },
						{ id: 2, bookmaker: 'Matchbook', market: '1X2', home_odds: 1.28, draw_odds: 6.20, away_odds: 11.50, updated_at: new Date().toISOString() }
					]
				},
				{
					id: 202,
					league: 'La Liga',
					home_team: 'Real Madrid',
					away_team: 'Barcelona',
					start_time: new Date(Date.now() - 3600000 * 0.8).toISOString(),
					status: 'live',
					home_score: 1,
					away_score: 1,
					minute: 52,
					possession_home: 48,
					possession_away: 52,
					shots_home: 8,
					shots_away: 10,
					xg_home: 1.12,
					xg_away: 1.45,
					momentum: 'away',
					momentum_intensity: 'moderate',
					odds: [
						{ id: 3, bookmaker: 'Betfair', market: '1X2', home_odds: 2.80, draw_odds: 3.10, away_odds: 2.60, updated_at: new Date().toISOString() },
						{ id: 4, bookmaker: 'Matchbook', market: '1X2', home_odds: 2.85, draw_odds: 3.05, away_odds: 2.55, updated_at: new Date().toISOString() }
					]
				},
				{
					id: 203,
					league: 'Serie A',
					home_team: 'Juventus',
					away_team: 'Inter',
					start_time: new Date(Date.now() - 3600000 * 2.1).toISOString(),
					status: 'live',
					home_score: 0,
					away_score: 2,
					minute: 85,
					possession_home: 45,
					possession_away: 55,
					shots_home: 5,
					shots_away: 12,
					xg_home: 0.56,
					xg_away: 2.34,
					momentum: 'away',
					momentum_intensity: 'overwhelming',
					odds: [
						{ id: 5, bookmaker: 'Betfair', market: '1X2', home_odds: 8.50, draw_odds: 4.20, away_odds: 1.40, updated_at: new Date().toISOString() }
					]
				},
				{
					id: 204,
					league: 'Bundesliga',
					home_team: 'Bayern Munich',
					away_team: 'Dortmund',
					start_time: new Date(Date.now() - 3600000 * 0.3).toISOString(),
					status: 'live',
					home_score: 1,
					away_score: 0,
					minute: 18,
					possession_home: 68,
					possession_away: 32,
					shots_home: 6,
					shots_away: 2,
					xg_home: 1.23,
					xg_away: 0.34,
					momentum: 'home',
					momentum_intensity: 'moderate',
					odds: [
						{ id: 6, bookmaker: 'Betfair', market: '1X2', home_odds: 1.55, draw_odds: 4.20, away_odds: 5.80, updated_at: new Date().toISOString() }
					]
				},
				{
					id: 205,
					league: 'Ligue 1',
					home_team: 'PSG',
					away_team: 'Marseille',
					start_time: new Date(Date.now() - 3600000 * 1.5).toISOString(),
					status: 'live',
					home_score: 3,
					away_score: 1,
					minute: 62,
					possession_home: 58,
					possession_away: 42,
					shots_home: 16,
					shots_away: 6,
					xg_home: 3.12,
					xg_away: 0.78,
					momentum: 'home',
					momentum_intensity: 'strong',
					odds: [
						{ id: 7, bookmaker: 'Betfair', market: '1X2', home_odds: 1.15, draw_odds: 8.00, away_odds: 15.00, updated_at: new Date().toISOString() }
					]
				},
				{
					id: 206,
					league: 'Premier League',
					home_team: 'Liverpool',
					away_team: 'Chelsea',
					start_time: new Date(Date.now() - 3600000 * 0.1).toISOString(),
					status: 'live',
					home_score: 0,
					away_score: 0,
					minute: 8,
					possession_home: 55,
					possession_away: 45,
					shots_home: 2,
					shots_away: 1,
					xg_home: 0.12,
					xg_away: 0.08,
					momentum: 'neutral',
					momentum_intensity: 'neutral',
					odds: [
						{ id: 8, bookmaker: 'Betfair', market: '1X2', home_odds: 2.10, draw_odds: 3.40, away_odds: 3.30, updated_at: new Date().toISOString() }
					]
				}
			],
			loading: false,
			lastUpdated: new Date().toISOString()
		};
	}
};
