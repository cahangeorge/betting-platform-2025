import { ApiClient } from './client';
import type {
	Bankroll,
	BankrollCreateRequest,
	BookmakerAccount,
	BookmakerAccountCreateRequest,
	LedgerEntry
} from '$lib/types';

class BankrollApi extends ApiClient {
	async getBankrolls(): Promise<Bankroll[]> {
		return this.get<Bankroll[]>('/bankrolls');
	}

	async getBankroll(id: number): Promise<Bankroll> {
		return this.get<Bankroll>(`/bankrolls/${id}`);
	}

	async createBankroll(data: BankrollCreateRequest): Promise<Bankroll> {
		return this.post<Bankroll>('/bankrolls', data as unknown as Record<string, unknown>);
	}

	async deleteBankroll(id: number): Promise<void> {
		return this.del<void>(`/bankrolls/${id}`);
	}

	async getAccounts(bankrollId?: number): Promise<BookmakerAccount[]> {
		const params = bankrollId ? `?bankroll_id=${bankrollId}` : '';
		return this.get<BookmakerAccount[]>(`/bankrolls/accounts${params}`);
	}

	async createAccount(data: BookmakerAccountCreateRequest): Promise<BookmakerAccount> {
		return this.post<BookmakerAccount>('/bankrolls/accounts', data as unknown as Record<string, unknown>);
	}

	async getLedger(bankrollId?: number): Promise<LedgerEntry[]> {
		const params = bankrollId ? `?bankroll_id=${bankrollId}` : '';
		return this.get<LedgerEntry[]>(`/bankrolls/ledger${params}`);
	}
}

export const bankrollApi = new BankrollApi();
