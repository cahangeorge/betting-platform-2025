import { ApiClient } from './client';
import type { ScrapeJob, ScrapeJobCreateRequest, Dataset, League } from '$lib/types';

class DataApi extends ApiClient {
	async getJobs(status?: string): Promise<ScrapeJob[]> {
		return this.get<ScrapeJob[]>('/api/v1/data/scrape');
	}

	async getJob(id: number): Promise<ScrapeJob> {
		return this.get<ScrapeJob>(`/api/v1/data/scrape/${id}`);
	}

	async createJob(data: ScrapeJobCreateRequest): Promise<ScrapeJob> {
		return this.post<ScrapeJob>('/api/v1/data/scrape', data as unknown as Record<string, unknown>);
	}

	async cancelJob(id: number): Promise<ScrapeJob> {
		// Backend doesn't have cancel endpoint — return the job as-is
		return this.get<ScrapeJob>(`/api/v1/data/scrape/${id}`);
	}

	async getDatasets(): Promise<Dataset[]> {
		return this.get<Dataset[]>('/api/v1/data/datasets');
	}

	async getDataset(id: number): Promise<Dataset> {
		return this.get<Dataset>(`/api/v1/data/datasets/${id}`);
	}

	async getLeagues(): Promise<League[]> {
		// Backend doesn't have a leagues endpoint yet — return empty
		return [];
	}
}

export const dataApi = new DataApi();
