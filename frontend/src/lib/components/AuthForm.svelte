<script lang="ts">
	import { authApi } from '$lib/api/auth';
	import { ApiClientError } from '$lib/api/client';
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';

	let {
		mode = 'login',
		onSuccess
	}: {
		mode?: 'login' | 'signup';
		onSuccess?: () => void;
	} = $props();

	let email = $state('');
	let password = $state('');
	let name = $state('');
	let confirmPassword = $state('');
	let error = $state('');
	let loading = $state(false);
	let errors = $state<Record<string, string>>({});

	$effect(() => {
		email = '';
		password = '';
		name = '';
		confirmPassword = '';
		error = '';
		errors = {};
	});

	function validate(): boolean {
		const newErrors: Record<string, string> = {};
		if (!email.trim()) newErrors.email = 'Email is required';
		else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) newErrors.email = 'Invalid email format';
		if (!password) newErrors.password = 'Password is required';
		else if (password.length < 6) newErrors.password = 'At least 6 characters';
		if (mode === 'signup') {
			if (!name.trim()) newErrors.name = 'Name is required';
			if (password !== confirmPassword) newErrors.confirmPassword = 'Passwords do not match';
		}
		errors = newErrors;
		return Object.keys(newErrors).length === 0;
	}

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!validate()) return;

		loading = true;
		error = '';

		try {
			if (mode === 'login') {
				await authApi.login({ email, password });
			} else {
				await authApi.signup({ email, password, name });
			}
			onSuccess?.();
		} catch (err) {
			if (err instanceof ApiClientError) {
				error = err.message;
			} else {
				error = 'An unexpected error occurred';
			}
		} finally {
			loading = false;
		}
	}
</script>

<form onsubmit={handleSubmit} class="space-y-5">
	{#if error}
		<div class="p-3 text-sm" style="background-color: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: var(--danger); border-radius: 0;">
			{error}
		</div>
	{/if}

	{#if mode === 'signup'}
		<Input
			label="Name"
			name="name"
			placeholder="Your full name"
			bind:value={name}
			error={errors.name}
			disabled={loading}
		/>
	{/if}

	<Input
		label="Email"
		name="email"
		type="email"
		placeholder="you@example.com"
		bind:value={email}
		error={errors.email}
		disabled={loading}
	/>

	<Input
		label="Password"
		name="password"
		type="password"
		placeholder="Enter your password"
		bind:value={password}
		error={errors.password}
		disabled={loading}
	/>

	{#if mode === 'signup'}
		<Input
			label="Confirm Password"
			name="confirmPassword"
			type="password"
			placeholder="Repeat your password"
			bind:value={confirmPassword}
			error={errors.confirmPassword}
			disabled={loading}
		/>
	{/if}

	<div class="flex items-center justify-between pt-2">
		{#if mode === 'login'}
			<a href="/signup" class="text-sm transition-colors duration-200" style="color: var(--accent-green);">
				No account yet? Sign up
			</a>
		{:else}
			<a href="/login" class="text-sm transition-colors duration-200" style="color: var(--accent-green);">
				Already have an account? Sign in
			</a>
		{/if}
	</div>

	<Button type="submit" fullWidth disabled={loading}>
		{#if loading}
			<div class="w-4 h-4 border-2 border-[#0F172A] border-t-transparent animate-spin mr-2" style="border-radius: 50%;"></div>
		{/if}
		{mode === 'login' ? 'Sign In' : 'Create Account'}
	</Button>
</form>
