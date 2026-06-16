<template>
  <header class="h-14 bg-white border-b border-slate-100 flex items-center px-8 justify-between shrink-0 select-none">
    <h1 class="text-sm font-bold text-slate-800 tracking-tight">
      {{ titles[active] }}
    </h1>
    <div class="flex items-center gap-2">
      <span class="text-[10px] text-slate-400 font-semibold tracking-wider uppercase font-mono">AASHTO Guide for Design of Pavement Structures, 1993</span>
    </div>
  </header>
</template>

<script setup>
defineProps({ active: String })

const titles = {
  design:       'Diseño de estructura de pavimento',
  optimization: 'Optimización por costo mínimo',
  report:       'Generación de reporte PDF',
}
</script>
