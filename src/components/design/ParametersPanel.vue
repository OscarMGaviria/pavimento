<template>
  <div class="bg-white rounded-2xl border border-slate-100 shadow-sm shadow-slate-100/40 p-6 select-none">
    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-5">Parámetros de diseño</h2>

    <!-- Confiabilidad R -->
    <div class="mb-4">
      <label class="field-label">
        Confiabilidad R (%)
        <span class="tooltip-icon" title="Probabilidad de que la estructura no falle durante su vida útil">?</span>
      </label>
      <select
        v-model.number="s.reliability"
        @change="setReliability(s.reliability)"
        class="field-input cursor-pointer bg-white"
      >
        <option v-for="r in RELIABILITY_OPTIONS" :key="r" :value="r">{{ r }}%</option>
      </select>

      <!-- Gráfico de Confiabilidad (Campana de Gauss) -->
      <div class="mt-3 bg-slate-50 border border-slate-100 rounded-xl p-3 flex flex-col items-center">
        <svg class="w-full max-w-[280px] h-[105px]" viewBox="0 0 280 105">
          <defs>
            <linearGradient id="shadedGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#818cf8" stop-opacity="0.15" />
              <stop offset="100%" stop-color="#4f46e5" stop-opacity="0.35" />
            </linearGradient>
          </defs>
          
          <!-- Área sombreada (Confiabilidad R%) -->
          <path :d="shadedPath" fill="url(#shadedGrad)" />
          
          <!-- Eje horizontal Z -->
          <line x1="20" y1="85" x2="260" y2="85" stroke="#cbd5e1" stroke-width="1.5" />
          
          <!-- Ticks y etiquetas del eje Z -->
          <g stroke="#94a3b8" stroke-width="1">
            <line v-for="z in [-3, -2, -1, 0, 1, 2, 3]" :key="z" :x1="getX(z)" y1="85" :x2="getX(z)" y2="88" />
          </g>
          <g fill="#94a3b8" font-size="7.5" font-family="monospace" text-anchor="middle">
            <text v-for="z in [-3, -2, -1, 0, 1, 2, 3]" :key="z" :x="getX(z)" y="97">{{ z }}</text>
          </g>
          
          <!-- Línea de la media (z = 0) -->
          <line :x1="getX(0)" y1="20" :x2="getX(0)" y2="85" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3,3" />
          
          <!-- Curva de distribución normal (Delineado) -->
          <path :d="outlinePath" fill="none" stroke="#6366f1" stroke-width="2" />
          
          <!-- Línea divisoria de Confiabilidad (Z_r) -->
          <line :x1="getX(s.Zr)" :y1="getY(s.Zr)" :x2="getX(s.Zr)" y2="85" stroke="#ef4444" stroke-width="1.5" />
          
          <!-- Marcador de Z_r -->
          <circle :cx="getX(s.Zr)" :cy="getY(s.Zr)" r="3" fill="#ef4444" />
          <g fill="#ef4444" font-size="7" font-weight="bold" font-family="sans-serif" :text-anchor="s.Zr > 0 ? 'start' : 'end'">
            <text :x="getX(s.Zr) + (s.Zr > 0 ? 6 : -6)" :y="getY(s.Zr) + 2">Z_r = {{ s.Zr.toFixed(3) }}</text>
          </g>
          
          <!-- Texto informativo del área sombreada -->
          <g fill="#4f46e5" font-size="8.5" font-weight="bold" font-family="sans-serif" text-anchor="end">
            <text x="255" y="15">R = {{ s.reliability }}%</text>
          </g>
        </svg>
      </div>
    </div>

    <!-- Zr -->
    <div class="mb-4">
      <label class="field-label">
        Desviación estándar normal (Zr)
        <span class="tooltip-icon" title="Se calcula automáticamente desde R%">?</span>
      </label>
      <input v-model.number="s.Zr" type="number" step="0.001" class="field-input font-mono text-slate-600 bg-slate-50/50" readonly />
    </div>

    <!-- So -->
    <div class="mb-4">
      <label class="field-label">
        Error estándar combinado (So)
        <span class="tooltip-icon" title="Típico: 0.40–0.50 para pavimento flexible">?</span>
      </label>
      <input v-model.number="s.So" type="number" step="0.01" min="0.3" max="0.6" class="field-input font-mono" />
    </div>

    <!-- DPSI -->
    <div class="mb-4">
      <label class="field-label">
        Pérdida de serviciabilidad (ΔPSI)
        <span class="tooltip-icon" title="Pi − Pt. Típico: 1.5–2.0">?</span>
      </label>
      <input v-model.number="s.DPSI" type="number" step="0.1" min="0.5" max="3" class="field-input font-mono" />
    </div>

    <!-- W18 -->
    <div class="mb-4">
      <label class="field-label">
        Ejes equivalentes 18 kips (W₁₈)
        <span class="tooltip-icon" title="Ejes acumulados de 18 kips durante la vida útil de diseño">?</span>
      </label>
      <input v-model.number="s.W18" type="number" step="100000" min="1000" class="field-input font-mono" />
    </div>

    <!-- Número de capas -->
    <div class="mt-5 pt-5 border-t border-slate-100">
      <label class="field-label mb-3">Número de capas</label>
      <div class="flex gap-2">
        <button
          v-for="n in [1, 2, 3]"
          :key="n"
          @click="s.numCapas = n"
          :class="[
            'flex-1 py-2 rounded-lg text-xs font-bold transition-all duration-150 cursor-pointer border active:scale-95 select-none',
            s.numCapas === n
              ? 'bg-secondary text-white border-secondary shadow-md shadow-secondary/15'
              : 'bg-white text-slate-500 border-slate-200 hover:border-secondary hover:text-secondary hover:bg-slate-50/50'
          ]"
        >{{ n }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAASHTODesign } from '@/composables/useAASHTODesign.js'

const { state: s, setReliability, RELIABILITY_OPTIONS } = useAASHTODesign()

// --- Campana de Gauss para Confiabilidad R% ---
const getX = (z) => 140 + z * 35 // z=-3 -> 35, z=3 -> 245
const getY = (z) => 85 - 60 * Math.exp(-z * z / 2) // Peak at y=25, base at y=85

const outlinePath = computed(() => {
  let points = []
  for (let z = -3.0; z <= 3.0; z += 0.1) {
    points.push(`${getX(z).toFixed(1)},${getY(z).toFixed(1)}`)
  }
  return `M ${points.join(' L ')}`
})

const shadedPath = computed(() => {
  const Zr = Math.max(-3.0, Math.min(3.0, s.Zr)) // Limitar en el rango visible del gráfico
  let points = []
  
  // Punto inicial en el eje Z
  const startX = getX(Zr)
  points.push(`${startX.toFixed(1)},85`)
  
  // Seguir la curva desde Zr hasta +3.0
  for (let z = Zr; z <= 3.0; z += 0.05) {
    points.push(`${getX(z).toFixed(1)},${getY(z).toFixed(1)}`)
  }
  points.push(`${getX(3.0).toFixed(1)},${getY(3.0).toFixed(1)}`)
  
  // Bajar al eje Z en z = 3.0
  points.push(`${getX(3.0).toFixed(1)},85`)
  
  return `M ${points.join(' L ')} Z`
})
</script>
