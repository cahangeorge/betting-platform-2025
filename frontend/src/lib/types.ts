// ─── Auth ──────────────────────────────────────────────
export interface User {
	id: number;
	email: string;
	name: string;
	is_active: boolean;
	is_superuser: boolean;
	created_at: string;
}

export interface LoginRequest {
	email: string;
	password: string;
}

export interface SignupRequest {
	email: string;
	password: string;
	name: string;
}

export interface AuthResponse {
	access_token: string;
	token_type: string;
}

// ─── Matches ───────────────────────────────────────────
export interface Match {
	id: number;
	league: string;
	home_team: string;
	away_team: string;
	start_time: string;
	status: MatchStatus;
	home_score: number | null;
	away_score: number | null;
	odds: Odd[];
}

export type MatchStatus = 'scheduled' | 'live' | 'finished' | 'postponed' | 'cancelled';

export interface Odd {
	id: number;
	bookmaker: string;
	market: string;
	home_odds: number;
	draw_odds: number | null;
	away_odds: number;
	updated_at: string;
}

export interface MatchFilter {
	league?: string;
	status?: MatchStatus;
	date_from?: string;
	date_to?: string;
}

// ─── Predictions ──────────────────────────────────────
export type ModelType = 'poisson' | 'bivariate_poisson' | 'skellam' | 'elo' | 'ensemble' | 'xgb';

export interface PredictionModel {
	id: string;
	name: string;
	type: ModelType;
	description: string;
	parameters: Record<string, unknown>;
}

export interface PredictionRun {
	id: number;
	model_type: ModelType;
	status: RunStatus;
	matches: number[];
	parameters: Record<string, unknown>;
	created_at: string;
	completed_at: string | null;
	results: PredictionResult[] | null;
	error: string | null;
}

export type RunStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface PredictionResult {
	match_id: number;
	home_team: string;
	away_team: string;
	home_prob: number;
	draw_prob: number;
	away_prob: number;
	home_expected_goals: number;
	away_expected_goals: number;
	predicted_score: string;
	value_bet: string | null;
	confidence: number;
}

export interface RunRequest {
	model_type: ModelType;
	match_ids: number[];
	parameters?: Record<string, unknown>;
}

export interface EnsembleResult {
	models: string[];
	weights: Record<string, number>;
	results: PredictionResult[];
}

export interface BacktestRequest {
	model_type: ModelType;
	date_from: string;
	date_to: string;
	parameters?: Record<string, unknown>;
}

export interface BacktestResult {
	model_type: ModelType;
	total_matches: number;
	accuracy: number;
	profit_loss: number;
	roi: number;
	results: PredictionResult[];
}

// ─── Tickets ──────────────────────────────────────────
export type TicketStatus = 'open' | 'won' | 'lost' | 'cashed_out' | 'void';
export type TicketType = 'single' | 'accumulator' | 'system';

export interface Ticket {
	id: number;
	reference: string;
	type: TicketType;
	status: TicketStatus;
	stake: number;
	total_odds: number;
	potential_return: number;
	actual_return: number | null;
	legs: TicketLeg[];
	created_at: string;
	settled_at: string | null;
	bankroll_id: number;
}

export interface TicketLeg {
	id: number;
	match_id: number;
	market: string;
	selection: string;
	odds: number;
	status: 'pending' | 'won' | 'lost' | 'void';
	match: Match | null;
}

export interface PlaceBetRequest {
	legs: {
		match_id: number;
		market: string;
		selection: string;
		odds: number;
	}[];
	stake: number;
	type: TicketType;
	bankroll_id: number;
}

export interface SettleRequest {
	ticket_id: number;
	outcome: 'won' | 'lost' | 'void';
	return_amount?: number;
}

// ─── Bankroll ─────────────────────────────────────────
export type BankrollType = 'paper' | 'real';
export type LedgerEntryType = 'deposit' | 'withdrawal' | 'bet_placed' | 'bet_won' | 'bet_lost' | 'adjustment';

export interface Bankroll {
	id: number;
	name: string;
	type: BankrollType;
	currency: string;
	balance: number;
	initial_balance: number;
	is_active: boolean;
	created_at: string;
}

export interface BankrollCreateRequest {
	name: string;
	type: BankrollType;
	currency?: string;
	initial_balance: number;
}

export interface BookmakerAccount {
	id: number;
	bookmaker_name: string;
	account_name: string;
	balance: number;
	currency: string;
	bankroll_id: number;
}

export interface BookmakerAccountCreateRequest {
	bookmaker_name: string;
	account_name: string;
	balance?: number;
	currency?: string;
	bankroll_id: number;
}

export interface LedgerEntry {
	id: number;
	entry_type: LedgerEntryType;
	description: string;
	amount: number;
	balance_after: number;
	reference_type: string | null;
	reference_id: number | null;
	created_at: string;
	bankroll_id: number;
}

// ─── Data / Scraping ──────────────────────────────────
export type JobStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
export type JobType = 'scrape_odds' | 'scrape_results' | 'scrape_league' | 'sync_data';

export interface ScrapeJob {
	id: number;
	type: JobType;
	status: JobStatus;
	params: Record<string, unknown>;
	progress: number;
	created_at: string;
	completed_at: string | null;
	error: string | null;
	result: Record<string, unknown> | null;
}

export interface ScrapeJobCreateRequest {
	type: JobType;
	params?: Record<string, unknown>;
}

export interface Dataset {
	id: number;
	name: string;
	source: string;
	league: string;
	season: string;
	row_count: number;
	columns: string[];
	created_at: string;
	updated_at: string;
	size_bytes: number;
}

export interface League {
	id: number;
	name: string;
	country: string;
	sport: string;
	is_active: boolean;
}

// ─── Scheduled Jobs ───────────────────────────────────
export interface ScheduledJob {
	id: number;
	name: string;
	cron_expression: string;
	task_type: string;
	params: Record<string, unknown>;
	is_enabled: boolean;
	last_run: string | null;
	next_run: string | null;
	created_at: string;
}

export interface ScheduledJobCreateRequest {
	name: string;
	cron_expression: string;
	task_type: string;
	params?: Record<string, unknown>;
}

// ─── API Error ─────────────────────────────────────────
export interface ApiError {
	detail: string;
	status_code: number;
}

// ─── Polling ──────────────────────────────────────────
export interface PollingState<T> {
	data: T | null;
	loading: boolean;
	error: string | null;
}
