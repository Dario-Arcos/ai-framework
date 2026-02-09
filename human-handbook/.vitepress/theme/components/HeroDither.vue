<script setup>
import { onMounted, onUnmounted, nextTick } from 'vue'

const REVEAL_MS = 1200
const TAGLINE_OVERLAP = 400
const WORD_STAGGER = 55

let el = null
let taglineEl = null
let taglineOriginal = null
let actionsEl = null
let badgeEl = null
const timers = []

function teardown() {
  timers.forEach(clearTimeout)
  timers.length = 0
  if (el) el.classList.remove('hero-text-reveal')
  if (taglineEl && taglineOriginal !== null) {
    taglineEl.innerHTML = taglineOriginal
    taglineEl.style.visibility = ''
  }
  if (actionsEl) {
    actionsEl.style.opacity = ''
    actionsEl.style.transform = ''
    actionsEl.style.transition = ''
  }
  if (badgeEl) {
    badgeEl.style.opacity = ''
    badgeEl.style.transform = ''
    badgeEl.style.transition = ''
  }
}

onMounted(async () => {
  await nextTick()
  if (typeof window === 'undefined') return
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

  el = document.querySelector('.VPHero .text')
  if (!el) return

  // --- Title: mask-based soft-edge reveal (preserves gradient + scanlines) ---
  el.classList.add('hero-text-reveal')

  // --- Tagline: word-by-word blur reveal ---
  const taglineStart = REVEAL_MS - TAGLINE_OVERLAP
  taglineEl = document.querySelector('.VPHero .tagline')
  if (taglineEl) {
    taglineOriginal = taglineEl.innerHTML
    taglineEl.style.visibility = 'visible'
    const words = taglineEl.textContent.trim().split(/\s+/)
    taglineEl.innerHTML = words.map((w, i) =>
      `<span class="hero-word" style="animation-delay:${taglineStart + i * WORD_STAGGER}ms">${w}</span>`
    ).join(' ')
  }

  // --- Version badge ---
  badgeEl = document.querySelector('.version-badge')
  if (badgeEl) {
    badgeEl.style.opacity = '0'
    badgeEl.style.transform = 'translateY(6px)'
    badgeEl.style.transition = 'none'
    timers.push(setTimeout(() => {
      badgeEl.style.transition = 'opacity 0.5s cubic-bezier(0.25,0.1,0.25,1), transform 0.5s cubic-bezier(0.25,0.1,0.25,1)'
      badgeEl.style.opacity = '1'
      badgeEl.style.transform = 'translateY(0)'
    }, REVEAL_MS - 200))
  }

  // --- Action buttons ---
  actionsEl = document.querySelector('.VPHero .actions')
  if (actionsEl) {
    actionsEl.style.opacity = '0'
    actionsEl.style.transform = 'translateY(8px)'
    actionsEl.style.transition = 'none'
    timers.push(setTimeout(() => {
      actionsEl.style.transition = 'opacity 0.6s cubic-bezier(0.25,0.1,0.25,1), transform 0.6s cubic-bezier(0.25,0.1,0.25,1)'
      actionsEl.style.opacity = '1'
      actionsEl.style.transform = 'translateY(0)'
    }, REVEAL_MS))
  }
})

onUnmounted(() => teardown())
</script>

<template><!-- orchestrated hero cascade: mask-reveal → word → badge → buttons --></template>
