import type { LayoutLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { authApi } from '$lib/api/auth';

export const load: LayoutLoad = async ({ url }) => {
	const publicRoutes = ['/login', '/signup', '/board', '/about'];
	const isPublicRoute =
		publicRoutes.some((route) => url.pathname.startsWith(route)) ||
		url.pathname === '/';

	let user = null;

	try {
		user = await authApi.getMe();
	} catch {
		user = null;
	}

	// Redirect to login for protected routes
	if (!user && !isPublicRoute) {
		redirect(302, '/login');
	}

	return {
		user
	};
};
