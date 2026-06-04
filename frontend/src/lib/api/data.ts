import { ApiClient } from './client';
import type { ScrapeJob, ScrapeJobCreateRequest, Dataset, League } from '$lib/types';

class DataApi extends ApiClient {
	async getJobs(status?: string): Promise<ScrapeJob[]> {
		const params = status ? `?status=${status}` : '';
		return this.get<ScrapeJob[]>(`/data/jobs${params}`);
	}

	async getJob(id: number): Promise<ScrapeJob> {
		return this.get<ScrapeJob>(`/data/jobs/${id}`);
	}

	async createJob(data: ScrapeJobCreateRequest): Promise<ScrapeJob> {
		return this.post<ScrapeJob>('/data/jobs', data as unknown as Record<string, unknown>);
	}

	async cancelJob(id: number): Promise<ScrapeJob> {
		return this.post<ScrapeJob>(`/data/jobs/${id}/cancel`);
	}

	async getDatasets(): Promise<Dataset[]> {
		return this.get<Dataset[]>('/data/datasets');
	}

	async getDataset(id: number): Promise<Dataset> {
		return this.get<Dataset>(`/data/datasets/${id}`);
	}

	async getLeagues(): Promise<League[]> {
		return this.get<League[]>('/data/leagues');
	}
}

export const dataApi = new DataApi();
