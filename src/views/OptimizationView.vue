<template>
  <div class="p-6 space-y-6 select-none">

    <!-- Aviso si no hay 3 capas -->
    <div v-if="state.numCapas !== 3"
      class="bg-amber-50 border border-amber-200 rounded-2xl p-5 flex items-start gap-4 shadow-sm shadow-amber-50/50">
      <div class="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center text-amber-600 shrink-0 text-sm font-bold">!</div>
      <div>
        <h3 class="text-xs font-bold text-amber-800 uppercase tracking-wider">Configuración de Capas Insuficiente</h3>
        <p class="text-xs text-amber-700 mt-1 leading-relaxed">
          La optimización estructural basada en costos mínimos requiere el diseño con <strong>3 capas</strong> (Carpeta Asfáltica + Base Granular + Sub-base Granular). Por favor, cambia el número de capas en la sección de diseño.
        </p>
      </div>
    </div>

    <template v-else>
      <!-- Costos unitarios -->
      <div class="bg-white rounded-2xl border border-slate-100 shadow-sm shadow-slate-100/40 p-6">
        <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-5">Costos unitarios ($/m²·cm)</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="item in costFields" :key="item.key"
            class="p-4 rounded-xl bg-slate-50/50 border border-slate-100/80">
            <label class="field-label mb-2">{{ item.label }}</label>
            <div class="relative flex items-center">
              <span class="absolute left-3 text-xs text-slate-400 font-semibold">$</span>
              <input
                v-model.number="costs[item.key]"
                type="number" min="0" step="1"
                class="field-input pl-7 font-mono text-slate-700"
              />
            </div>
            <p class="text-[10px] text-slate-400 font-medium mt-2 tracking-wide uppercase">{{ item.hint }}</p>
          </div>
        </div>
      </div>

      <!-- Resultado óptimo -->
      <div v-if="optimizationResults" class="grid grid-cols-1 md:grid-cols-2 gap-6">

        <!-- Mejor combinación -->
        <div class="bg-white rounded-2xl border border-slate-100 shadow-sm shadow-slate-100/40 p-6 flex flex-col justify-between">
          <div>
            <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-5">Combinación óptima recomendada</h2>
            <div class="space-y-3.5">
              <!-- CA -->
              <div class="flex items-center justify-between p-3 rounded-xl bg-slate-800 text-white shadow-sm">
                <span class="text-xs font-bold uppercase tracking-wider">Carpeta asfáltica (CA)</span>
                <span class="font-mono font-bold text-sm bg-white/10 px-2 py-0.5 rounded">{{ optimizationResults.best.D1 }} cm</span>
              </div>
              <!-- BG -->
              <div class="flex items-center justify-between p-3 rounded-xl bg-stone-500 text-white shadow-sm">
                <span class="text-xs font-bold uppercase tracking-wider">Base granular (BG)</span>
                <span class="font-mono font-bold text-sm bg-white/10 px-2 py-0.5 rounded">{{ optimizationResults.best.D2 }} cm</span>
              </div>
              <!-- SBG -->
              <div class="flex items-center justify-between p-3 rounded-xl bg-amber-800 text-white shadow-sm">
                <span class="text-xs font-bold uppercase tracking-wider">Sub-base granular (SBG)</span>
                <span class="font-mono font-bold text-sm bg-white/10 px-2 py-0.5 rounded">{{ optimizationResults.best.D3 }} cm</span>
              </div>
            </div>
          </div>

          <div class="mt-6 pt-4 border-t border-slate-100 flex justify-between items-center">
            <span class="text-xs text-slate-400 font-bold uppercase tracking-wider">Costo total por área</span>
            <span class="font-mono font-black text-secondary text-lg bg-indigo-50 px-3 py-1 rounded-xl border border-indigo-100/50">
              ${{ optimizationResults.best.costo.toFixed(2) }}/m²
            </span>
          </div>
        </div>

        <!-- Tabla de alternativas -->
        <div class="bg-white rounded-2xl border border-slate-100 shadow-sm shadow-slate-100/40 p-6">
          <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-5">Alternativas estructuradas (menor costo)</h2>
          <div class="overflow-hidden border border-slate-100 rounded-xl">
            <table class="w-full text-xs">
              <thead>
                <tr class="bg-slate-50 border-b border-slate-100 text-slate-400 font-semibold tracking-wider uppercase text-[10px]">
                  <th class="py-2.5 pr-4 text-right">CA (cm)</th>
                  <th class="py-2.5 pr-4 text-right">BG (cm)</th>
                  <th class="py-2.5 pr-4 text-right">SBG (cm)</th>
                  <th class="py-2.5 pr-6 text-right">Costo ($/m²)</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-50">
                <tr
                  v-for="(row, i) in optimizationResults.candidates"
                  :key="i"
                  :class="[
                    'transition-colors duration-150',
                    i === 0 ? 'bg-secondary/5 font-bold text-secondary' : 'hover:bg-slate-50/50 text-slate-600'
                  ]"
                >
                  <td class="py-2.5 pr-4 text-right font-mono font-bold">{{ row.D1 }}</td>
                  <td class="py-2.5 pr-4 text-right font-mono font-bold">{{ row.D2 }}</td>
                  <td class="py-2.5 pr-4 text-right font-mono font-bold">{{ row.D3 }}</td>
                  <td class="py-2.5 pr-6 text-right font-mono font-bold text-secondary text-sm">
                    ${{ row.costo.toFixed(2) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <div v-else class="text-center py-12 text-slate-400 text-sm font-medium">
        Completa los parámetros de diseño primero para ejecutar la optimización.
      </div>
    </template>
  </div>
</template>

<script setup>
import { useAASHTODesign } from '@/composables/useAASHTODesign.js'
import { useOptimization } from '@/composables/useOptimization.js'

const { state } = useAASHTODesign()
const { costs, optimizationResults } = useOptimization()

const costFields = [
  { key: 'c1', label: 'Carpeta asfáltica', hint: 'Mezcla densa en caliente' },
  { key: 'c2', label: 'Base granular',     hint: 'Material granular compactado' },
  { key: 'c3', label: 'Sub-base granular', hint: 'Material granular base' },
]
</script>
