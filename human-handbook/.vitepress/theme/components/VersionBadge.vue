<script setup>
import { useData } from 'vitepress'
import { computed } from 'vue'

const { theme } = useData()

const version = computed(() => theme.value.version || 'N/A')
const previousVersion = computed(() => theme.value.previousVersion || 'N/A')

const githubReleaseUrl = computed(() => {
  if (version.value === 'N/A') return '#'
  return `https://github.com/Dario-Arcos/ai-framework/releases/tag/v${version.value}`
})

const isFirstRelease = computed(() => {
  return previousVersion.value === 'N/A' || previousVersion.value === version.value
})
</script>

<template>
  <div class="version-badge">
    <div class="version-current">
      <a
        :href="githubReleaseUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="version-link"
      >
        Version {{ version }}
      </a>
    </div>
    <div v-if="!isFirstRelease" class="version-previous">
      Previous: {{ previousVersion }}
    </div>
  </div>
</template>

<style scoped>
.version-badge {
  margin-top: 1rem;
  font-size: 0.8125rem;
  color: var(--vp-c-text-2);
  line-height: 1.5;
}

.version-current a {
  color: var(--vp-c-text-1);
  text-decoration: none;
  font-weight: 500;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s;
}

.version-current a:hover {
  border-bottom-color: var(--vp-c-brand-1);
}

.version-previous {
  display: inline;
  margin-left: 0.5rem;
  opacity: 0.6;
}
</style>
