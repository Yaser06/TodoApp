---
architectureStyle: "Component + Composable"
layering: "Pages → Components → Composables → API"
errorStrategy: "error.vue + NuxtErrorBoundary"
testingApproach: "Vitest (unit) + Playwright (e2e)"
observability: "console + Nuxt DevTools"
---

# Pattern Profile — Vue3/Nuxt

## Composables Pattern

**Reusable logic extraction:**

```typescript
// composables/useCounter.ts (auto-imported)
export const useCounter = (initialValue = 0) => {
  const count = ref(initialValue)
  const increment = () => count.value++
  const decrement = () => count.value--

  return { count, increment, decrement }
}

// Usage in component (no import needed!)
const { count, increment } = useCounter(10)
```

## Component Patterns

**Prop Validation:**

```vue
<script setup lang="ts">
interface Props {
  title: string
  count?: number
  user: { id: number; name: string }
}

const props = withDefaults(defineProps<Props>(), {
  count: 0
})
</script>
```

**Slots:**

```vue
<template>
  <div class="card">
    <slot name="header" :title="title" />
    <slot /> <!-- default slot -->
    <slot name="footer" />
  </div>
</template>
```

## State Management

```typescript
// Simple state (no store needed)
const globalState = useState('counter', () => 0)

// Pinia for complex state
const userStore = useUserStore()
```

## Error Handling

```vue
<!-- error.vue -->
<script setup lang="ts">
const error = useError()
</script>

<template>
  <div>
    <h1>{{ error.statusCode }}</h1>
    <p>{{ error.message }}</p>
    <button @click="clearError">Go Home</button>
  </div>
</template>
```

## SEO

```typescript
useHead({
  title: 'My Page',
  meta: [
    { name: 'description', content: 'Page description' }
  ]
})

useSeoMeta({
  ogTitle: 'My Page',
  ogDescription: 'Page description',
  ogImage: '/og-image.png'
})
```
