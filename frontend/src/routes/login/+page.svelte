<script lang="ts">
	import AuthForm from '$lib/components/AuthForm.svelte';
	import Card from '$lib/components/ui/Card.svelte';

	function onLoginSuccess() {
		window.location.href = '/';
	}
</script>

<div class="min-h-[calc(100vh-4rem)] flex items-center justify-center">
	<div class="w-full max-w-md">
		<div class="text-center mb-8">
			<div
				class="w-16 h-16 flex items-center justify-center mx-auto mb-4"
				style="background-color: var(--bg-elevated); border: 1px solid var(--accent-green); border-radius: 0;"
			>
				<span class="font-extrabold text-2xl" style="color: var(--accent-green); font-family: var(--font-sport);">SI</span>
			</div>
			<h1 class="text-2xl font-extrabold font-sport" style="color: var(--text-primary);">Welcome back</h1>
			<p class="mt-2" style="color: var(--text-secondary);">Sign in to your account</p>
		</div>

		<div class="card p-5" style="border-top: 2px solid var(--accent-green);">
			<AuthForm mode="login" onSuccess={onLoginSuccess} />
		</div>
	</div>
</div>
