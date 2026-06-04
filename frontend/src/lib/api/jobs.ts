import { ApiClient } from './client';
import type { ScheduledJob, ScheduledJobCreateRequest } from '$lib/types';

class JobsApi extends ApiClient {
	async getScheduledJobs(): Promise<ScheduledJob[]> {
		return this.get<ScheduledJob[]>('/scheduled-jobs');
	}

	async getScheduledJob(id: number): Promise<ScheduledJob> {
		return this.get<ScheduledJob>(`/scheduled-jobs/${id}`);
	}

	async createScheduledJob(data: ScheduledJobCreateRequest): Promise<ScheduledJob> {
		return this.post<ScheduledJob>('/scheduled-jobs', data as unknown as Record<string, unknown>);
	}

	async updateScheduledJob(id: number, data: Partial<ScheduledJobCreateRequest>): Promise<ScheduledJob> {
		return this.patch<ScheduledJob>(`/scheduled-jobs/${id}`, data as unknown as Record<string, unknown>);
	}

	async deleteScheduledJob(id: number): Promise<void> {
		return this.del<void>(`/scheduled-jobs/${id}`);
	}

	async toggleJob(id: number): Promise<ScheduledJob> {
		return this.post<ScheduledJob>(`/scheduled-jobs/${id}/toggle`);
	}
}

export const jobsApi = new JobsApi();
