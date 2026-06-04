/// <reference types="@sveltejs/kit" />
/// <reference no-default-lib="true"/>
/// <reference lib="esnext" />
/// <reference lib="webworker" />

const sw = self as unknown as ServiceWorkerGlobalScope;

import { build, files, version } from '$service-worker';

// Create a unique cache name for this deployment
const CACHE = `betfront-${version}`;

const ASSETS = [
	...build, // the app itself
	...files  // everything in `static`
];

// Install service worker
sw.addEventListener('install', (event) => {
	async function addFilesToCache() {
		const cache = await caches.open(CACHE);
		await cache.addAll(ASSETS);
	}
	event.waitUntil(addFilesToCache());
});

// Activate and clean old caches
sw.addEventListener('activate', (event) => {
	async function deleteOldCaches() {
		for (const key of await caches.keys()) {
			if (key !== CACHE) {
				await caches.delete(key);
			}
		}
	}
	event.waitUntil(deleteOldCaches());
});

// Fetch strategy
sw.addEventListener('fetch', (event) => {
	// Ignore non-GET requests
	if (event.request.method !== 'GET') return;

	// Ignore chrome-extension requests
	if (event.request.url.startsWith('chrome-extension://')) return;

	const url = new URL(event.request.url);
	const isApiCall = url.pathname.startsWith('/api/') || url.hostname !== self.location.hostname;
	const isAsset = ASSETS.includes(url.pathname);

	if (isApiCall) {
		// Network-first for API calls
		event.respondWith(networkFirst(event.request));
	} else if (isAsset || url.origin === self.location.origin) {
		// Cache-first for app assets
		event.respondWith(cacheFirst(event.request));
	}
});

async function cacheFirst(request: Request): Promise<Response> {
	const cache = await caches.open(CACHE);
	const cached = await cache.match(request);
	if (cached) {
		return cached;
	}
	try {
		const response = await fetch(request);
		if (response.ok) {
			cache.put(request, response.clone());
		}
		return response;
	} catch {
		// Return offline fallback
		return new Response('Offline', { status: 503 });
	}
}

async function networkFirst(request: Request): Promise<Response> {
	try {
		const response = await fetch(request);
		if (response.ok) {
			const cache = await caches.open(CACHE);
			cache.put(request, response.clone());
		}
		return response;
	} catch {
		const cache = await caches.open(CACHE);
		const cached = await cache.match(request);
		if (cached) {
			return cached;
		}
		return new Response(JSON.stringify({ error: 'You are offline' }), {
			status: 503,
			headers: { 'Content-Type': 'application/json' }
		});
	}
}
