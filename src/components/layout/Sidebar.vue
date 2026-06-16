<template>
  <aside class="w-20 min-h-screen bg-slate-950 border-r border-slate-900 flex flex-col items-center select-none py-6 shrink-0">
    <!-- Logo Compacto -->
    <div class="mb-8 text-center">
      <span class="text-transparent bg-clip-text bg-gradient-to-br from-slate-200 to-slate-400 font-mono font-extrabold text-sm tracking-tight leading-none block">AASHTO</span>
      <span class="text-slate-600 font-mono text-[8px] font-bold uppercase block mt-1 tracking-wider">93</span>
    </div>

    <!-- Navegación de Vistas -->
    <nav class="flex flex-col gap-3.5 w-full px-3">
      <div v-for="item in nav" :key="item.id" class="relative group flex justify-center">
        <button
          @click="$emit('change', item.id)"
          :class="[
            'w-12 h-12 flex items-center justify-center rounded-xl transition-all duration-200 cursor-pointer active:scale-90 border',
            active === item.id
              ? 'bg-slate-900 text-indigo-400 border-indigo-500/30 shadow-md shadow-indigo-950/40 font-bold'
              : 'text-slate-500 hover:bg-slate-900/40 hover:text-slate-300 border-transparent'
          ]"
        >
          <!-- Icono Diseño -->
          <svg v-if="item.id === 'design'" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <path d="M3 9h18M9 21V9"/>
          </svg>
          
          <!-- Icono Optimización -->
          <svg v-else-if="item.id === 'optimization'" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2v20M2 12h20"/>
            <circle cx="12" cy="12" r="4"/>
          </svg>

          <!-- Icono Reporte -->
          <svg v-else-if="item.id === 'report'" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="8" y1="13" x2="16" y2="13"/>
            <line x1="8" y1="17" x2="16" y2="17"/>
          </svg>
        </button>
        <!-- Tooltip -->
        <span class="absolute left-16 top-1/2 -translate-y-1/2 bg-slate-900 text-slate-100 text-[10px] font-bold uppercase tracking-wider py-1.5 px-3 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150 pointer-events-none z-50 whitespace-nowrap border border-slate-800 shadow-xl">
          {{ item.label }}
        </span>
      </div>
    </nav>

    <!-- Divisor -->
    <div class="w-10 h-[1px] bg-slate-900/60 my-6"></div>

    <!-- Barra de Edición de Parámetros -->
    <div v-if="active === 'design'" class="flex-1 flex flex-col gap-3.5 w-full px-3">
      <div v-for="item in params" :key="item.id" class="relative group flex justify-center">
        <button
          @click="$emit('toggle-param', item.id)"
          :class="[
            'w-12 h-12 flex items-center justify-center rounded-xl transition-all duration-200 cursor-pointer active:scale-90 border',
            activeParam === item.id
              ? 'bg-slate-900 text-amber-400 border-amber-500/30 shadow-md shadow-amber-950/40'
              : 'text-slate-500 hover:bg-slate-900/40 hover:text-slate-300 border-transparent'
          ]"
        >
          <!-- Icono Capas -->
          <svg v-if="item.id === 'layers'" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>

          <!-- Icono Estadísticas -->
          <svg v-else-if="item.id === 'stats'" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="20" x2="18" y2="10"/>
            <line x1="12" y1="20" x2="12" y2="4"/>
            <line x1="6" y1="20" x2="6" y2="14"/>
          </svg>

          <!-- Icono Serviciabilidad -->
          <svg v-else-if="item.id === 'serv'" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>

          <!-- Icono Tránsito -->
          <svg v-else-if="item.id === 'traffic'" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="1" y="3" width="15" height="13" rx="2"/>
            <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
            <circle cx="5.5" cy="18.5" r="2.5"/>
            <circle cx="18.5" cy="18.5" r="2.5"/>
          </svg>

          <!-- Icono Materiales -->
          <svg v-else-if="item.id === 'materials'" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="4" y1="21" x2="4" y2="14"/>
            <line x1="4" y1="10" x2="4" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12" y2="3"/>
            <line x1="20" y1="21" x2="20" y2="16"/>
            <line x1="20" y1="12" x2="20" y2="3"/>
            <line x1="1" y1="14" x2="7" y2="14"/>
            <line x1="9" y1="8" x2="15" y2="8"/>
            <line x1="17" y1="16" x2="23" y2="16"/>
          </svg>
        </button>
        <!-- Tooltip -->
        <span class="absolute left-16 top-1/2 -translate-y-1/2 bg-slate-900 text-slate-100 text-[10px] font-bold uppercase tracking-wider py-1.5 px-3 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150 pointer-events-none z-50 whitespace-nowrap border border-slate-800 shadow-xl">
          {{ item.label }}
        </span>
      </div>
    </div>
    <div v-else class="flex-1"></div>

    <!-- Footer Compacto -->
    <div class="mt-auto pt-6 text-center w-full border-t border-slate-900/60">
      <span class="text-slate-700 text-[8px] font-mono block">v1.0</span>
    </div>
  </aside>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  active: String,
  activeParam: String
})
defineEmits(['change', 'toggle-param'])

const nav = [
  { id: 'design',       label: 'Diseño' },
  { id: 'optimization', label: 'Optimización' },
  { id: 'report',       label: 'Reporte PDF' },
]

const params = [
  { id: 'layers',    label: 'Número de Capas' },
  { id: 'stats',     label: 'Estadísticas (R, So)' },
  { id: 'serv',      label: 'Serviciabilidad (ΔPSI)' },
  { id: 'traffic',   label: 'Tránsito (W18)' },
  { id: 'materials', label: 'Materiales' },
]
</script>
