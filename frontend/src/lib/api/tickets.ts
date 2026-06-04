import { ApiClient } from './client';
import type { Ticket, PlaceBetRequest, SettleRequest } from '$lib/types';

class TicketsApi extends ApiClient {
	async getTickets(status?: string): Promise<Ticket[]> {
		const params = status ? `?status=${status}` : '';
		return this.get<Ticket[]>(`/tickets${params}`);
	}

	async getTicket(id: number): Promise<Ticket> {
		return this.get<Ticket>(`/tickets/${id}`);
	}

	async placeBet(data: PlaceBetRequest): Promise<Ticket> {
		return this.post<Ticket>('/tickets', data as unknown as Record<string, unknown>);
	}

	async settleTicket(data: SettleRequest): Promise<Ticket> {
		return this.post<Ticket>('/tickets/settle', data as unknown as Record<string, unknown>);
	}

	async getStats(): Promise<{ total: number; won: number; lost: number; profit_loss: number }> {
		return this.get('/tickets/stats');
	}
}

export const ticketsApi = new TicketsApi();
