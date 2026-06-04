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
		return this.get<PredictionModel[]>('/predict/models');
	}

	async getRuns(): Promise<PredictionRun[]> {
		return this.get<PredictionRun[]>('/predict/runs');
	}

	async getRun(id: number): Promise<PredictionRun> {
		return this.get<PredictionRun>(`/predict/runs/${id}`);
	}

	async createRun(data: RunRequest): Promise<PredictionRun> {
		return this.post<PredictionRun>('/predict/runs', data as unknown as Record<string, unknown>);
	}

	async getEnsemble(runId: number): Promise<EnsembleResult> {
		return this.get<EnsembleResult>(`/predict/runs/${runId}/ensemble`);
	}

	async runBacktest(data: BacktestRequest): Promise<BacktestResult> {
		return this.post<BacktestResult>('/predict/backtest', data as unknown as Record<string, unknown>);
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
		return this.get('/predictions/value-bets', undefined, fetchFn);
	}
}

export const predictionsApi = new PredictionsApi();
