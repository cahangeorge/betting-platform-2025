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

// Activate and clean old caches + take control immediately
sw.addEventListener('activate', (event) => {
	async function deleteOldCaches() {
		const keys = await caches.keys();
		await Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)));
		// Take control of all open tabs immediately
		await sw.clients.claim();
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
		// Network-first for API calls — don't cache failures
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
		// Return offline fallback for assets
		return new Response('Offline', { status: 503 });
	}
}

async function networkFirst(request: Request): Promise<Response> {
	try {
		const response = await fetch(request);
		// Only cache successful responses, not errors
		if (response.ok) {
			const cache = await caches.open(CACHE);
			cache.put(request, response.clone());
		}
		return response;
	} catch {
		// Try cache as fallback
		const cache = await caches.open(CACHE);
		const cached = await cache.match(request);
		if (cached) {
			return cached;
		}
		// Return a clear error — don't pretend we're offline if the server is just slow
		return new Response(JSON.stringify({ error: 'Network request failed' }), {
			status: 503,
			headers: { 'Content-Type': 'application/json' }
		});
	}
}
