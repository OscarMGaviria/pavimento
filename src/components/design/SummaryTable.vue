<template>
  <div class="bg-white rounded-2xl border border-slate-100 shadow-sm shadow-slate-100/40 p-4 select-none">
    <div v-if="results" class="grid grid-cols-1 xl:grid-cols-3 gap-4 items-start">
      
      <!-- Tabla 1: Parámetros de entrada -->
      <div class="xl:col-span-1 space-y-2">
        <h3 class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Parámetros</h3>
        <div class="border border-slate-100 rounded-xl overflow-hidden text-xs">
          <table class="w-full">
            <tbody class="divide-y divide-slate-50">
              <tr class="hover:bg-slate-50/40">
                <td class="py-1 px-2 text-slate-500 font-medium">Confiabilidad (R)</td>
                <td class="py-1 px-2 text-right font-mono font-bold text-slate-700">{{ s.reliability }}%</td>
              </tr>
              <tr class="hover:bg-slate-50/40">
                <td class="py-1 px-2 text-slate-500 font-medium">Zr</td>
                <td class="py-1 px-2 text-right font-mono font-bold text-slate-700">{{ s.Zr.toFixed(3) }}</td>
              </tr>
              <tr class="hover:bg-slate-50/40">
                <td class="py-1 px-2 text-slate-500 font-medium">So</td>
                <td class="py-1 px-2 text-right font-mono font-bold text-slate-700">{{ s.So.toFixed(2) }}</td>
              </tr>
              <tr class="hover:bg-slate-50/40">
                <td class="py-1 px-2 text-slate-500 font-medium">ΔPSI</td>
                <td class="py-1 px-2 text-right font-mono font-bold text-slate-700">{{ s.DPSI.toFixed(2) }}</td>
              </tr>
              <tr class="hover:bg-slate-50/40">
                <td class="py-1 px-2 text-slate-500 font-medium">Tránsito (W₁₈)</td>
                <td class="py-1 px-2 text-right font-mono font-bold text-secondary font-extrabold">{{ s.W18.toLocaleString('es-CO') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tabla 2: Estructura de capas y resultados -->
      <div class="xl:col-span-2 flex flex-col gap-2">
        <h3 class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Resultados Estructurales</h3>
        <div class="border border-slate-100 rounded-xl overflow-x-auto overflow-y-hidden md:overflow-hidden text-[11px] flex-1">
          <table class="w-full h-full min-w-[500px] md:min-w-0">
            <thead>
              <tr class="bg-slate-50 border-b border-slate-100 text-slate-400 font-bold uppercase text-[9px] tracking-wider">
                <th class="py-1.5 px-2 text-left">Capa</th>
                <th class="py-1.5 px-2 text-right">a</th>
                <th class="py-1.5 px-2 text-right">m</th>
                <th class="py-1.5 px-2 text-right">Mr (psi)</th>
                <th class="py-1.5 px-2 text-right">SN</th>
                <th class="py-1.5 px-2 text-right">Espesor</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr v-for="(capa, i) in tableRows" :key="i" class="hover:bg-slate-50/40 text-slate-600 font-medium">
                <td class="py-1.5 px-2 flex items-center gap-1.5 text-slate-700 font-semibold">
                  <span class="w-2 h-2 rounded-sm border border-black/5" :style="{ background: capa.color }"></span>
                  {{ capa.nombre }}
                </td>
                <td class="py-1.5 px-2 text-right font-mono">{{ capa.a.toFixed(3) }}</td>
                <td class="py-1.5 px-2 text-right font-mono">{{ capa.m !== '-' ? capa.m.toFixed(2) : '-' }}</td>
                <td class="py-1.5 px-2 text-right font-mono">{{ capa.Mr !== '-' ? capa.Mr.toLocaleString('es-CO') : '-' }}</td>
                <td class="py-1.5 px-2 text-right font-mono text-slate-400">{{ capa.SN.toFixed(3) }}</td>
                <td class="py-1.5 px-2 text-right font-mono font-bold text-secondary text-xs">{{ capa.cm }} cm</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Fila de totales -->
        <div class="flex justify-between items-center bg-indigo-50/40 border border-indigo-100/40 p-2 rounded-xl mt-auto">
          <span class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Espesor Total</span>
          <span class="font-mono font-black text-secondary text-sm bg-white px-2 py-0.5 rounded-md border border-indigo-100 shadow-sm">
            {{ results.capas.reduce((a, c) => a + c.cm, 0) }} cm
          </span>
        </div>
      </div>

    </div>

    <div v-else class="text-center py-8 text-slate-400 text-sm font-medium">
      Cargando parámetros...
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAASHTODesign } from '@/composables/useAASHTODesign.js'

const { state: s, results } = useAASHTODesign()

const tableRows = computed(() => {
  if (!results.value) return []
  const { capas, SNT } = results.value
  const n = s.numCapas

  if (n === 1) {
    return [
      { nombre: capas[0].nombre, a: s.a1, m: '-', Mr: s.Mr3, SN: SNT[2], cm: capas[0].cm, color: capas[0].color }
    ]
  }

  if (n === 2) {
    return [
      { nombre: capas[0].nombre, a: s.a1, m: '-', Mr: s.Mr1, SN: SNT[0], cm: capas[0].cm, color: capas[0].color },
      { nombre: capas[1].nombre, a: s.a2, m: s.m2, Mr: s.Mr3, SN: SNT[2], cm: capas[1].cm, color: capas[1].color },
    ]
  }

  // 3 capas
  return [
    { nombre: capas[0].nombre, a: s.a1, m: '-', Mr: s.Mr1, SN: SNT[0], cm: capas[0].cm, color: capas[0].color },
    { nombre: capas[1].nombre, a: s.a2, m: s.m2, Mr: s.Mr2, SN: SNT[1], cm: capas[1].cm, color: capas[1].color },
    { nombre: capas[2].nombre, a: s.a3, m: s.m3, Mr: s.Mr3, SN: SNT[2], cm: capas[2].cm, color: capas[2].color },
  ]
})
</script>
