---
language: "TypeScript"
version: "5.0+"
framework: "Nuxt 3"
frameworkVersion: "3.8+"
packageManager: "pnpm / npm / yarn"
keyLibraries:
  - "@nuxt/ui (UI components)"
  - "pinia (state management)"
  - "vueuse (composables)"
  - "zod (validation)"
  - "nuxt-icon (icons)"
architecture: "Component-based with Composables"
testFramework: "Vitest + Playwright"
buildTool: "Vite"
linting: "ESLint + Prettier"
---

# Tech Profile — Vue3/Nuxt

## Core Stack

**Language**: TypeScript 5.0+
**Framework**: Nuxt 3.8+
**State**: Pinia
**UI**: Shadcn Vue + Radix Vue + Tailwind CSS
**Data Fetching**: useFetch, useAsyncData
**Build Tool**: Vite

## Project Structure

```
project/
├── app.vue              # Root component
├── nuxt.config.ts       # Configuration
├── components/
│   ├── ui/             # Shadcn UI components
│   ├── forms/
│   └── layout/
├── composables/        # Reusable composition functions
│   ├── useAuth.ts
│   └── useApi.ts
├── pages/              # File-based routing
│   ├── index.vue
│   ├── about.vue
│   └── users/
│       └── [id].vue
├── layouts/
│   ├── default.vue
│   └── admin.vue
├── stores/             # Pinia stores
│   └── user.ts
├── server/             # API routes (Nitro)
│   └── api/
│       └── users.ts
├── public/             # Static assets
└── assets/             # Build-time assets
```

## Composition API Patterns

```vue
<script setup lang="ts">
// Auto-imported from Vue
const count = ref(0)
const doubled = computed(() => count.value * 2)

// Auto-imported composables
const { data: user } = await useFetch('/api/user')

// Props
const props = defineProps<{
  title: string
  count?: number
}>()

// Emits
const emit = defineEmits<{
  update: [value: number]
  delete: []
}>()

// Lifecycle
onMounted(() => {
  console.log('Component mounted')
})
</script>

<template>
  <div>{{ count }}</div>
</template>
```

## Data Fetching

```typescript
// useFetch for SSR-optimized requests
const { data, pending, error, refresh } = await useFetch('/api/users')

// useAsyncData for complex scenarios
const { data } = await useAsyncData('users', () => $fetch('/api/users'))

// $fetch for client-side only
const handleSubmit = async () => {
  const result = await $fetch('/api/users', {
    method: 'POST',
    body: { name: 'John' }
  })
}
```

## Pinia Store

```typescript
// stores/user.ts
export const useUserStore = definePiniaStore('user', () => {
  const user = ref<User | null>(null)
  const isLoggedIn = computed(() => !!user.value)

  async function login(email: string, password: string) {
    const data = await $fetch('/api/auth/login', {
      method: 'POST',
      body: { email, password }
    })
    user.value = data.user
  }

  function logout() {
    user.value = null
  }

  return { user, isLoggedIn, login, logout }
})
```

## Configuration

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@nuxt/ui', '@pinia/nuxt', '@vueuse/nuxt'],

  runtimeConfig: {
    apiSecret: '', // Server-only
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE
    }
  },

  typescript: {
    strict: true
  },

  tailwindcss: {
    exposeConfig: true
  }
})
```
