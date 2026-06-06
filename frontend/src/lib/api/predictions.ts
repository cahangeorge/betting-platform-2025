import { ApiClient } from './client';
import type {
	PredictionRun,
	RunRequest,
	PredictionModel,
	EnsembleResult,
	BacktestRequest,
	BacktestResult
} from '$lib/types';

class PredictionsApi extends ApiClient {
	async getModels(): Promise<PredictionModel[]> {
		return this.get<PredictionModel[]>('/api/v1/predictions/catalog');
	}

	async getRuns(): Promise<PredictionRun[]> {
		return this.get<PredictionRun[]>('/api/v1/predictions/runs');
	}

	async getRun(id: number): Promise<PredictionRun> {
		return this.get<PredictionRun>(`/api/v1/predictions/runs/${id}`);
	}

	async createRun(data: RunRequest): Promise<PredictionRun> {
		return this.post<PredictionRun>('/api/v1/predictions/run', data as unknown as Record<string, unknown>);
	}

	async getEnsemble(runId: number): Promise<EnsembleResult> {
		return this.post<EnsembleResult>(`/api/v1/predictions/ensemble`, { run_id: runId } as unknown as Record<string, unknown>);
	}

	async runBacktest(data: BacktestRequest): Promise<BacktestResult> {
		// Backend doesn't have a dedicated backtest endpoint yet — return empty
		return {
			model_type: data.model_type,
			total_matches: 0,
			accuracy: 0,
			profit_loss: 0,
			roi: 0,
			results: []
		};
	}

	async getValueBets(fetchFn?: typeof fetch): Promise<Array<{
		id: number;
		match_id: number;
		league: string;
		home_team: string;
		away_team: string;
		kickoff: string;
		market: string;
		selection: string;
		model_prob: number;
		odds: number;
		edge: number;
		model_type: string;
		confidence: number;
	}>> {
		// Backend doesn't have a value-bets endpoint yet — return empty
		return [];
	}
}

export const predictionsApi = new PredictionsApi();
