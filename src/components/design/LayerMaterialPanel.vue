<template>
  <div class="bg-white rounded-2xl border border-slate-100 shadow-sm shadow-slate-100/40 p-6 select-none">
    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-5">Propiedades de materiales</h2>

    <div class="space-y-4">

      <!-- Carpeta asfáltica (Siempre visible) -->
      <div class="rounded-xl border border-slate-100 overflow-hidden shadow-sm bg-slate-50/30">
        <div class="bg-slate-800 px-4 py-2">
          <span class="text-white text-xs font-bold uppercase tracking-wider">Carpeta asfáltica</span>
        </div>
        <div class="p-3.5 space-y-3">
          <div class="flex items-center justify-between gap-4">
            <span class="text-xs text-slate-500 font-medium flex items-center" title="Coeficiente estructural de la mezcla asfáltica. Típico: 0.40–0.50">
              a₁ (coeficiente capa)
              <span class="text-[9px] text-slate-300 ml-1 cursor-help">ⓘ</span>
            </span>
            <input
              type="number"
              step="0.001"
              v-model.number="s.a1"
              class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right bg-white focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/10 transition-all duration-200"
            />
          </div>
        </div>
      </div>

      <!-- Base granular (Capas >= 2) -->
      <div v-if="s.numCapas >= 2" class="rounded-xl border border-slate-100 overflow-hidden shadow-sm bg-slate-50/30">
        <div class="bg-stone-500 px-4 py-2">
          <span class="text-white text-xs font-bold uppercase tracking-wider">Base granular</span>
        </div>
        <div class="p-3.5 space-y-3">
          <!-- Mr1 -->
          <div class="flex items-center justify-between gap-4">
            <span class="text-xs text-slate-500 font-medium flex items-center" title="Módulo resiliente de la base granular. Típico: 28,000–40,000 psi">
              Mr₁ (módulo, psi)
              <span class="text-[9px] text-slate-300 ml-1 cursor-help">ⓘ</span>
            </span>
            <input
              type="number"
              step="1000"
              v-model.number="s.Mr1"
              class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right bg-white focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/10 transition-all duration-200"
            />
          </div>
          <!-- a2 -->
          <div class="flex items-center justify-between gap-4">
            <span class="text-xs text-slate-500 font-medium flex items-center" title="Coeficiente estructural base granular. Típico: 0.10–0.15">
              a₂ (coeficiente)
              <span class="text-[9px] text-slate-300 ml-1 cursor-help">ⓘ</span>
            </span>
            <input
              type="number"
              step="0.001"
              v-model.number="s.a2"
              class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right bg-white focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/10 transition-all duration-200"
            />
          </div>
          <!-- m2 -->
          <div class="flex items-center justify-between gap-4">
            <span class="text-xs text-slate-500 font-medium flex items-center" title="Factor de drenaje. 1.0 = excelente, 0.80 = regular, 0.60 = malo">
              m₂ (drenaje)
              <span class="text-[9px] text-slate-300 ml-1 cursor-help">ⓘ</span>
            </span>
            <input
              type="number"
              step="0.01"
              v-model.number="s.m2"
              class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right bg-white focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/10 transition-all duration-200"
            />
          </div>
        </div>
      </div>

      <!-- Sub-base (Solo 3 capas) -->
      <div v-if="s.numCapas === 3" class="rounded-xl border border-slate-100 overflow-hidden shadow-sm bg-slate-50/30">
        <div class="bg-amber-800/80 px-4 py-2">
          <span class="text-white text-xs font-bold uppercase tracking-wider">Sub-base granular</span>
        </div>
        <div class="p-3.5 space-y-3">
          <!-- Mr2 -->
          <div class="flex items-center justify-between gap-4">
            <span class="text-xs text-slate-500 font-medium flex items-center" title="Módulo resiliente de la sub-base. Típico: 14,000–20,000 psi">
              Mr₂ (módulo, psi)
              <span class="text-[9px] text-slate-300 ml-1 cursor-help">ⓘ</span>
            </span>
            <input
              type="number"
              step="1000"
              v-model.number="s.Mr2"
              class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right bg-white focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/10 transition-all duration-200"
            />
          </div>
          <!-- a3 -->
          <div class="flex items-center justify-between gap-4">
            <span class="text-xs text-slate-500 font-medium flex items-center" title="Coeficiente estructural sub-base. Típico: 0.08–0.14">
              a₃ (coeficiente)
              <span class="text-[9px] text-slate-300 ml-1 cursor-help">ⓘ</span>
            </span>
            <input
              type="number"
              step="0.001"
              v-model.number="s.a3"
              class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right bg-white focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/10 transition-all duration-200"
            />
          </div>
          <!-- m3 -->
          <div class="flex items-center justify-between gap-4">
            <span class="text-xs text-slate-500 font-medium flex items-center" title="Factor de drenaje de la sub-base">
              m₃ (drenaje)
              <span class="text-[9px] text-slate-300 ml-1 cursor-help">ⓘ</span>
            </span>
            <input
              type="number"
              step="0.01"
              v-model.number="s.m3"
              class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right bg-white focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/10 transition-all duration-200"
            />
          </div>
        </div>
      </div>

      <!-- Subrasante (Siempre visible) -->
      <div class="rounded-xl border border-slate-100 overflow-hidden shadow-sm bg-slate-50/30">
        <div class="bg-emerald-800 px-4 py-2">
          <span class="text-white text-xs font-bold uppercase tracking-wider">Subrasante</span>
        </div>
        <div class="p-3.5 space-y-3">
          <div class="flex items-center justify-between gap-4">
            <span class="text-xs text-slate-500 font-medium flex items-center" title="Módulo resiliente de la subrasante (terreno natural). Típico: 7,000–15,000 psi">
              Mr₃ (módulo, psi)
              <span class="text-[9px] text-slate-300 ml-1 cursor-help">ⓘ</span>
            </span>
            <input
              type="number"
              step="500"
              v-model.number="s.Mr3"
              class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right bg-white focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/10 transition-all duration-200"
            />
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { useAASHTODesign } from '@/composables/useAASHTODesign.js'
const { state: s } = useAASHTODesign()
</script>
