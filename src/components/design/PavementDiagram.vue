<template>
  <div class="bg-white rounded-2xl border border-slate-100 shadow-sm shadow-slate-100/40 p-4 select-none flex flex-col h-full overflow-hidden">
    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4 shrink-0">Esquema 2D (Sección)</h2>

    <div v-if="results" class="w-full flex-1 min-h-0 flex justify-center items-center overflow-hidden">
      <!-- SVG Proporcional Estilizado -->
      <svg :viewBox="`0 0 ${svgW + 60} ${svgH + 28}`" class="w-full h-full max-h-full overflow-visible">
        <defs>
          <!-- Degradado Carpeta Asfáltica -->
          <linearGradient id="grad-asphalt" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#404859" />
            <stop offset="100%" stop-color="#2d333f" />
          </linearGradient>
          
          <!-- Degradado Base Granular -->
          <linearGradient id="grad-base" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#c1b6a2" />
            <stop offset="100%" stop-color="#b0a38c" />
          </linearGradient>

          <!-- Degradado Sub-base Granular -->
          <linearGradient id="grad-subbase" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#99775f" />
            <stop offset="100%" stop-color="#826550" />
          </linearGradient>

          <!-- Degradado Subrasante -->
          <linearGradient id="grad-subgrade" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#1b9c4b" />
            <stop offset="100%" stop-color="#15803d" />
          </linearGradient>
        </defs>

        <!-- Capas -->
        <g v-for="(capa, i) in layerRects" :key="i">
          <rect
            :x="2" :y="capa.y" :width="svgW - 4" :height="capa.h - 1"
            :fill="getGradient(capa.nombre)"
            rx="4"
            class="transition-all duration-500 stroke-white/10"
            stroke-width="1"
          />
          <!-- Texto nombre de la capa -->
          <text :x="15" :y="capa.y + capa.h / 2 + 3" font-size="9" fill="white"
            font-family="Fira Sans, sans-serif" font-weight="700" class="tracking-wide uppercase opacity-90 pointer-events-none">
            {{ capa.nombre }}
          </text>
        </g>

        <!-- Subrasante fondo -->
        <rect x="2" :y="svgH" :width="svgW - 4" height="24" fill="url(#grad-subgrade)" rx="4" class="stroke-white/10" stroke-width="1" />
        <text x="15" :y="svgH + 15" font-size="9" fill="white" font-family="Fira Sans, sans-serif" font-weight="700" class="tracking-wide uppercase opacity-90 pointer-events-none">Subrasante</text>

        <!-- Cotas de espesor -->
        <g v-for="(capa, i) in layerRects" :key="'cota-'+i">
          <!-- Línea vertical de la cota -->
          <line :x1="svgW + 12" :y1="capa.y" :x2="svgW + 12" :y2="capa.y + capa.h"
            stroke="#cbd5e1" stroke-width="1" />
          <!-- Ticks extremos -->
          <circle :cx="svgW + 12" :cy="capa.y" r="2.2" fill="#94a3b8" />
          <circle :cx="svgW + 12" :cy="capa.y + capa.h" r="2.2" fill="#94a3b8" />
          
          <!-- Texto espesor -->
          <text :x="svgW + 20" :y="capa.y + capa.h / 2 + 4.5" font-size="10.5"
            fill="#334155" font-family="Fira Code, monospace" font-weight="700">
            {{ capa.cm }} cm
          </text>
        </g>
      </svg>
    </div>

    <div v-else class="text-center py-12 text-slate-400 text-sm font-medium">
      Ingresa los parámetros para ver el diagrama
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAASHTODesign } from '@/composables/useAASHTODesign.js'

const { results } = useAASHTODesign()

const svgW = 200 // Ancho aumentado para alineación centrada
const MAX_H = 180
const MIN_LAYER_H = 26

const getGradient = (nombre) => {
  if (nombre.includes('asfáltica')) return 'url(#grad-asphalt)'
  if (nombre.includes('Base granular')) return 'url(#grad-base)'
  if (nombre.includes('Sub-base')) return 'url(#grad-subbase)'
  return '#ccc'
}

const layerRects = computed(() => {
  if (!results.value) return []
  const capas = results.value.capas
  const total = capas.reduce((a, c) => a + c.cm, 0) || 1
  let y = 0
  return capas.map(c => {
    const h = Math.max(MIN_LAYER_H, Math.round((c.cm / total) * MAX_H))
    const rect = { y, h, color: c.color, nombre: c.nombre, cm: c.cm }
    y += h
    return rect
  })
})

const svgH = computed(() => {
  if (!layerRects.value.length) return MAX_H
  return layerRects.value.reduce((a, r) => a + r.h, 0)
})
</script>
