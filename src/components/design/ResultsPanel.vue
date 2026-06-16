<template>
  <div class="bg-white rounded-2xl border border-slate-100 shadow-sm shadow-slate-100/40 p-6 select-none">
    <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-5">Números estructurales (SN)</h2>

    <div v-if="results" class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div v-for="(item, i) in snItems" :key="i"
        class="flex flex-col justify-between p-4 rounded-xl bg-slate-50/50 border border-slate-100/80 hover:bg-slate-50 transition-colors duration-150">
        <div>
          <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">{{ item.label }}</span>
          <p class="text-xs font-semibold text-slate-500 mt-1 leading-tight">{{ item.desc }}</p>
        </div>
        <div class="mt-4 flex items-baseline justify-between">
          <span class="font-mono text-2xl font-extrabold text-slate-800 leading-none">
            {{ item.value.toFixed(3) }}
          </span>
          <span class="text-[10px] font-extrabold text-secondary tracking-widest uppercase font-mono">SN</span>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-8 text-slate-400 text-sm font-medium">
      Sin resultados
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAASHTODesign } from '@/composables/useAASHTODesign.js'

const { state, results } = useAASHTODesign()

const LAYER_LABELS = ['Base granular', 'Sub-base', 'Subrasante']
const LAYER_DESC   = ['SN req. sobre base', 'SN req. sobre sub-base', 'SN req. sobre subrasante']

const snItems = computed(() => {
  if (!results.value) return []
  const { SNT } = results.value
  const n = state.numCapas

  if (n === 1) return [{ label: 'Subrasante', desc: LAYER_DESC[2], value: SNT[2] }]
  if (n === 2) return [
    { label: LAYER_LABELS[0], desc: LAYER_DESC[0], value: SNT[0] },
    { label: LAYER_LABELS[2], desc: LAYER_DESC[2], value: SNT[2] },
  ]
  return [
    { label: LAYER_LABELS[0], desc: LAYER_DESC[0], value: SNT[0] },
    { label: LAYER_LABELS[1], desc: LAYER_DESC[1], value: SNT[1] },
    { label: LAYER_LABELS[2], desc: LAYER_DESC[2], value: SNT[2] },
  ]
})
</script>
