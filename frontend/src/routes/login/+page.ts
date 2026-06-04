import type { PageLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { authApi } from '$lib/api/auth';

export const load: PageLoad = async () => {
	try {
		await authApi.getMe();
		// Already logged in, redirect to home
		redirect(302, '/');
	} catch {
		// Not logged in, show login form
		return {};
	}
};
