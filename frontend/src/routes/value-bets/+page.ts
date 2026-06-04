import type { PageLoad } from './$types';
import { predictionsApi } from '$lib/api/predictions';

export const load: PageLoad = async ({ fetch }) => {
	try {
		const valueBets = await predictionsApi.getValueBets(fetch);
		return {
			valueBets,
			loading: false
		};
	} catch (e) {
		// Demo data fallback
		return {
			valueBets: [
				{
					id: 1,
					match_id: 101,
					league: 'Premier League',
					home_team: 'Man City',
					away_team: 'Arsenal',
					kickoff: new Date(Date.now() + 3600000 * 2).toISOString(),
					market: '1X2',
					selection: 'Home',
					model_prob: 0.623,
					odds: 1.85,
					edge: 15.2,
					model_type: 'poisson',
					confidence: 0.78
				},
				{
					id: 2,
					match_id: 102,
					league: 'La Liga',
					home_team: 'Real Madrid',
					away_team: 'Barcelona',
					kickoff: new Date(Date.now() + 3600000 * 4).toISOString(),
					market: '1X2',
					selection: 'Draw',
					model_prob: 0.312,
					odds: 3.60,
					edge: 12.4,
					model_type: 'dixon_coles',
					confidence: 0.65
				},
				{
					id: 3,
					match_id: 103,
					league: 'Serie A',
					home_team: 'Juventus',
					away_team: 'Inter',
					kickoff: new Date(Date.now() + 3600000 * 1.5).toISOString(),
					market: 'OU',
					selection: 'Over 2.5',
					model_prob: 0.584,
					odds: 2.10,
					edge: 22.6,
					model_type: 'ensemble',
					confidence: 0.82
				},
				{
					id: 4,
					match_id: 104,
					league: 'Bundesliga',
					home_team: 'Bayern Munich',
					away_team: 'Dortmund',
					kickoff: new Date(Date.now() + 3600000 * 3).toISOString(),
					market: '1X2',
					selection: 'Home',
					model_prob: 0.712,
					odds: 1.55,
					edge: 10.4,
					model_type: 'poisson',
					confidence: 0.85
				},
				{
					id: 5,
					match_id: 105,
					league: 'Ligue 1',
					home_team: 'PSG',
					away_team: 'Marseille',
					kickoff: new Date(Date.now() + 3600000 * 5).toISOString(),
					market: 'BTTS',
					selection: 'Yes',
					model_prob: 0.671,
					odds: 1.72,
					edge: 15.4,
					model_type: 'bivariate_poisson',
					confidence: 0.71
				},
				{
					id: 6,
					match_id: 106,
					league: 'Premier League',
					home_team: 'Liverpool',
					away_team: 'Chelsea',
					kickoff: new Date(Date.now() + 3600000 * 6).toISOString(),
					market: '1X2',
					selection: 'Away',
					model_prob: 0.284,
					odds: 4.20,
					edge: 19.3,
					model_type: 'ensemble',
					confidence: 0.68
				},
				{
					id: 7,
					match_id: 107,
					league: 'La Liga',
					home_team: 'Atletico Madrid',
					away_team: 'Sevilla',
					kickoff: new Date(Date.now() + 3600000 * 2.5).toISOString(),
					market: 'OU',
					selection: 'Under 2.5',
					model_prob: 0.452,
					odds: 2.40,
					edge: 8.5,
					model_type: 'dixon_coles',
					confidence: 0.62
				},
				{
					id: 8,
					match_id: 108,
					league: 'Serie A',
					home_team: 'AC Milan',
					away_team: 'Roma',
					kickoff: new Date(Date.now() + 3600000 * 1).toISOString(),
					market: '1X2',
					selection: 'Home',
					model_prob: 0.541,
					odds: 2.25,
					edge: 21.7,
					model_type: 'poisson',
					confidence: 0.74
				}
			],
			loading: false
		};
	}
};
