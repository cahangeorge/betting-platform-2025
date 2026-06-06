<script lang="ts">
	import { Dialog as DialogPrimitive } from "bits-ui";
	import { cn } from "$lib/utils.js";

	let {
		class: className,
		...restProps
	}: DialogPrimitive.RootProps = $props();
</script>

<DialogPrimitive.Root class={cn("", className)} {...restProps}>
	{@render restProps.children?.()}
</DialogPrimitive.Root>
