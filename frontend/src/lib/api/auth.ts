import { ApiClient } from './client';
import type { User, LoginRequest, SignupRequest } from '$lib/types';

class AuthApi extends ApiClient {
	async login(data: LoginRequest): Promise<User> {
		const formData = new FormData();
		formData.append('username', data.email);
		formData.append('password', data.password);
		return this.post<User>('/auth/login', formData);
	}

	async signup(data: SignupRequest): Promise<User> {
		return this.post<User>('/auth/signup', data as unknown as Record<string, unknown>);
	}

	async logout(): Promise<void> {
		return this.post<void>('/auth/logout');
	}

	async getMe(): Promise<User> {
		return this.get<User>('/auth/me');
	}
}

export const authApi = new AuthApi();
