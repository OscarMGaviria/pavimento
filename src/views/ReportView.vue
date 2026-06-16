<template>
  <div class="p-6 space-y-6 select-none">
    <div class="bg-white rounded-2xl border border-slate-100 shadow-sm shadow-slate-100/40 p-6 max-w-xl">
      <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-5">Generar reporte PDF</h2>

      <div v-if="results" class="space-y-4 mb-6 text-sm text-slate-600">
        <p class="font-medium text-slate-700">El reporte PDF descargable incluirá la siguiente información técnica:</p>
        <ul class="space-y-2.5 text-xs text-slate-500 font-medium">
          <li class="flex items-center gap-2">
            <span class="w-4 h-4 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-[9px] shrink-0">✓</span>
            Parámetros de diseño general AASHTO 93
          </li>
          <li class="flex items-center gap-2">
            <span class="w-4 h-4 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-[9px] shrink-0">✓</span>
            Números estructurales (SN) calculados por capa
          </li>
          <li class="flex items-center gap-2">
            <span class="w-4 h-4 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-[9px] shrink-0">✓</span>
            Espesores constructivos en centímetros
          </li>
          <li class="flex items-center gap-2">
            <span class="w-4 h-4 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-[9px] shrink-0">✓</span>
            Propiedades mecánicas y coeficientes de drenaje
          </li>
        </ul>
      </div>

      <div v-else class="text-xs font-semibold text-amber-700 bg-amber-50 border border-amber-200/50 rounded-xl p-4 mb-6 flex items-center gap-3">
        <span class="w-6 h-6 rounded-lg bg-amber-100 flex items-center justify-center font-bold shrink-0 text-xs">!</span>
        Realiza el diseño primero antes de generar el reporte.
      </div>

      <button
        @click="generatePDF"
        :disabled="!results"
        :class="[
          'w-full py-3 rounded-lg text-xs font-bold uppercase tracking-wider transition-all duration-150 cursor-pointer active:scale-97 select-none',
          results
            ? 'bg-secondary text-white hover:bg-indigo-700 shadow-md shadow-secondary/15'
            : 'bg-slate-100 text-slate-400 cursor-not-allowed'
        ]"
      >
        Descargar Documento PDF
      </button>
    </div>
  </div>
</template>

<script setup>
import { useAASHTODesign } from '@/composables/useAASHTODesign.js'
import { generatePavimentoPDF } from '@/utils/pdfReport.js'

const { state, results } = useAASHTODesign()

function generatePDF() {
  if (!results.value) return
  generatePavimentoPDF(state, results.value)
}
</script>
