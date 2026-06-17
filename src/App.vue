<template>
  <div class="flex h-screen bg-surface font-sans overflow-hidden relative">
    <!-- Sidebar Angosto -->
    <Sidebar
      :active="view"
      :active-param="activeParam"
      @change="changeView"
      @toggle-param="toggleParam"
    />

    <!-- Layout Principal -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden relative">
      <TopBar :active="view" />
      <main class="flex-1 overflow-auto">
        <DesignView       v-if="view === 'design'"       />
        <OptimizationView v-else-if="view === 'optimization'" />
        <ReportView       v-else-if="view === 'report'"  />
      </main>
    </div>

    <!-- Panel Flotante de Parámetros -->
    <Transition name="panel-slide">
      <div v-if="activeParam && view === 'design'"
        class="fixed left-24 top-16 bottom-16 z-40 bg-white rounded-2xl border border-slate-100 shadow-2xl p-6 w-[360px] select-none flex flex-col justify-between">
        
        <div class="flex-1 flex flex-col min-h-0">
          <div class="flex items-center justify-between border-b border-slate-100 pb-3 mb-5 shrink-0">
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400">
              {{ panelTitles[activeParam] }}
            </h3>
            <button @click="activeParam = null" class="w-5 h-5 flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full font-bold text-xs cursor-pointer transition-colors">✕</button>
          </div>

          <div class="flex-1 overflow-y-auto pr-1 flex flex-col">
            <!-- Capas Panel -->
            <div v-if="activeParam === 'layers'" class="space-y-4">
              <label class="field-label mb-2">Número de capas estructurales</label>
              <div class="flex gap-2">
                <button
                  v-for="n in [1, 2, 3]"
                  :key="n"
                  @click="s.numCapas = n"
                  :class="[
                    'flex-1 py-2.5 rounded-lg text-xs font-bold transition-all duration-150 cursor-pointer border active:scale-95',
                    s.numCapas === n
                      ? 'bg-secondary text-white border-secondary shadow-md shadow-secondary/15'
                      : 'bg-white text-slate-500 border-slate-200 hover:border-secondary hover:text-secondary hover:bg-slate-50/50'
                  ]"
                >{{ n }}</button>
              </div>
            </div>

            <!-- Stats Panel -->
            <div v-if="activeParam === 'stats'" class="flex flex-col h-full gap-4 pb-1">
              <!-- Gráfico de Confiabilidad (Campana de Gauss - Interactivo, Sin fondo, 90% ancho, Más alto y ancho) -->
              <div class="w-full h-[200px] md:flex-1 md:min-h-0 flex items-center justify-center py-1 select-none overflow-visible">
                <svg
                  ref="svgRef"
                  class="w-[92%] h-full max-h-[200px] md:max-h-[320px] cursor-ew-resize select-none overflow-visible touch-none"
                  viewBox="0 0 340 320"
                  @mousedown="startDrag"
                  @mousemove="onDrag"
                  @mouseup="endDrag"
                  @mouseleave="endDrag"
                  @touchstart="startDrag"
                  @touchmove="onDrag"
                  @touchend="endDrag"
                >
                  <defs>
                    <linearGradient id="shadedGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stop-color="#818cf8" stop-opacity="0.08" />
                      <stop offset="100%" stop-color="#4f46e5" stop-opacity="0.25" />
                    </linearGradient>
                  </defs>
                  
                  <!-- Área sombreada (Rellenado de izquierda a derecha) -->
                  <path :d="shadedPath" fill="url(#shadedGrad)" />
                  
                  <!-- Eje horizontal Z -->
                  <line x1="20" y1="280" x2="320" y2="280" stroke="#e2e8f0" stroke-width="1.5" />
                  
                  <!-- Ticks y etiquetas del eje Z -->
                  <g stroke="#cbd5e1" stroke-width="1">
                    <line v-for="z in [-3, -2, -1, 0, 1, 2, 3]" :key="z" :x1="getX(z)" y1="280" :x2="getX(z)" y2="284" />
                  </g>
                  <g fill="#94a3b8" font-size="8.5" font-family="monospace" text-anchor="middle">
                    <text v-for="z in [-3, -2, -1, 0, 1, 2, 3]" :key="z" :x="getX(z)" y="296">{{ z }}</text>
                  </g>
                  
                  <!-- Línea de la media (z = 0) -->
                  <line :x1="getX(0)" y1="40" :x2="getX(0)" y2="280" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="3,3" />
                  
                  <!-- Curva de distribución normal (Delineado con color Indigo del tema) -->
                  <path :d="outlinePath" fill="none" stroke="#4f46e5" stroke-width="2.5" />
                  
                  <!-- Línea divisoria de Confiabilidad (Z_r en color Amber de la paleta) -->
                  <line :x1="getX(-s.Zr)" :y1="getY(-s.Zr)" :x2="getX(-s.Zr)" y2="280" stroke="#f59e0b" stroke-width="2" />
                  
                  <!-- Marcador de Z_r con halo visual -->
                  <circle :cx="getX(-s.Zr)" :cy="getY(-s.Zr)" r="5.5" fill="#f59e0b" class="cursor-ew-resize drop-shadow" />
                  <circle :cx="getX(-s.Zr)" :cy="getY(-s.Zr)" r="2" fill="#ffffff" class="pointer-events-none" />
                  <g fill="#d97706" font-size="9" font-weight="bold" font-family="sans-serif" :text-anchor="-s.Zr > 0 ? 'start' : 'end'">
                    <text :x="getX(-s.Zr) + (-s.Zr > 0 ? 8 : -8)" :y="getY(-s.Zr) + 3">Z_r = {{ s.Zr.toFixed(3) }}</text>
                  </g>
                  
                  <!-- Texto informativo del área sombreada -->
                  <g fill="#4f46e5" font-size="10" font-weight="bold" font-family="sans-serif" text-anchor="end">
                    <text x="320" y="30">R = {{ s.reliability }}%</text>
                  </g>
                </svg>
              </div>

              <div class="relative relative-dropdown-container shrink-0">
                <div class="flex items-center justify-between mb-1.5">
                  <label class="field-label mb-0">Confiabilidad R (%)</label>
                  <button 
                    type="button" 
                    @click="isReliabilityHelpModalOpen = true" 
                    class="text-[10px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer bg-indigo-50 hover:bg-indigo-100/80 px-2 py-0.5 rounded-md transition-colors select-none"
                  >
                    <span>Guía</span>
                    <span class="w-3.5 h-3.5 flex items-center justify-center bg-indigo-600 text-white rounded-full text-[9px]">?</span>
                  </button>
                </div>
                <button 
                  type="button"
                  @click="isDropdownOpen = !isDropdownOpen"
                  class="field-input flex items-center justify-between cursor-pointer bg-slate-50/50 hover:bg-slate-50 transition-colors"
                >
                  <span class="font-medium text-slate-800">{{ s.reliability }}%</span>
                  <svg class="w-4 h-4 text-slate-400 transition-transform duration-200" :class="{ 'rotate-180': isDropdownOpen }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                
                <Transition name="dropdown-fade">
                  <div 
                    v-if="isDropdownOpen" 
                    class="absolute left-0 right-0 mt-1.5 bg-white border border-slate-100 rounded-xl shadow-xl z-50 max-h-60 overflow-y-auto py-1"
                  >
                    <div 
                      v-for="r in RELIABILITY_OPTIONS" 
                      :key="r"
                      @click="selectReliabilityOption(r)"
                      class="px-4 py-2 text-sm text-slate-700 hover:bg-indigo-50/70 hover:text-indigo-600 cursor-pointer transition-colors flex items-center justify-between"
                      :class="{ 'bg-indigo-50/50 text-indigo-600 font-semibold': s.reliability === r }"
                    >
                      <span>{{ r }}%</span>
                      <svg v-if="s.reliability === r" class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  </div>
                </Transition>
              </div>
              <div class="shrink-0">
                <label class="field-label">Desviación estándar normal (Zr)</label>
                <input v-model.number="s.Zr" type="number" step="0.001" class="field-input font-mono" readonly />
              </div>
              <div class="space-y-1.5 shrink-0">
                <div class="flex items-center justify-between">
                  <label class="field-label mb-0">Error estándar combinado (So)</label>
                  <button 
                    type="button" 
                    @click="isHelpModalOpen = true" 
                    class="text-[10px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer bg-indigo-50 hover:bg-indigo-100/80 px-2 py-0.5 rounded-md transition-colors select-none"
                  >
                    <span>Guía</span>
                    <span class="w-3.5 h-3.5 flex items-center justify-center bg-indigo-600 text-white rounded-full text-[9px]">?</span>
                  </button>
                </div>
                <input v-model.number="s.So" type="number" step="0.01" min="0.4" max="0.5" class="field-input font-mono" />
                <input v-model.number="s.So" type="range" step="0.01" min="0.4" max="0.5" class="w-full mt-1 accent-indigo-600 cursor-ew-resize h-1.5 bg-slate-100 rounded-lg appearance-none" />
              </div>
            </div>

            <!-- Serviciabilidad Panel -->
            <div v-if="activeParam === 'serv'" class="flex flex-col h-full gap-4 pb-1">
              <div class="flex items-center justify-between shrink-0">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Visualización de pérdida</span>
                <button 
                  type="button" 
                  @click="isServHelpModalOpen = true" 
                  class="text-[10px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer bg-indigo-50 hover:bg-indigo-100/80 px-2 py-0.5 rounded-md transition-colors select-none"
                >
                  <span>Guía</span>
                  <span class="w-3.5 h-3.5 flex items-center justify-center bg-indigo-600 text-white rounded-full text-[9px]">?</span>
                </button>
              </div>
              <!-- Gráfico de Pérdida de Serviciabilidad (Interactivo, Sin fondo, 92% ancho, Más alto) -->
              <div class="w-full h-[200px] md:flex-1 md:min-h-0 flex items-center justify-center py-1 select-none overflow-visible">
                <svg
                  ref="servSvgRef"
                  class="w-[92%] h-full max-h-[200px] md:max-h-[320px] select-none overflow-visible touch-none"
                  viewBox="0 0 340 320"
                  @mousemove="onDragServ"
                  @mouseup="endDragServ"
                  @mouseleave="endDragServ"
                  @touchmove="onDragServ"
                  @touchend="endDragServ"
                >
                  <defs>
                    <linearGradient id="servGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stop-color="#4f46e5" stop-opacity="0.25" />
                      <stop offset="100%" stop-color="#4f46e5" stop-opacity="0.0" />
                    </linearGradient>
                  </defs>

                  <!-- Relleno bajo la curva de serviciabilidad -->
                  <path :d="servFillPath" fill="url(#servGrad)" class="pointer-events-none" />

                  <!-- Líneas de cuadrícula horizontales de referencia (1 a 6) -->
                  <g stroke="#f1f5f9" stroke-width="1">
                    <line v-for="val in [1, 2, 3, 4, 5, 6]" :key="val" x1="40" :y1="getYp(val)" x2="300" :y2="getYp(val)" />
                  </g>

                  <!-- Ejes -->
                  <!-- Eje X (Tiempo) con flecha en el extremo -->
                  <line x1="40" y1="280" x2="300" y2="280" stroke="#cbd5e1" stroke-width="1.5" />
                  <path d="M 296,276 L 302,280 L 296,284" fill="none" stroke="#cbd5e1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                  <text x="302" y="296" fill="#475569" font-size="9.5" font-weight="bold" font-family="sans-serif" text-anchor="end">T(años)</text>

                  <!-- Eje Y (Serviciabilidad) con flecha en el extremo (proyectado hasta 6.0) -->
                  <line x1="40" y1="30" x2="40" y2="280" stroke="#cbd5e1" stroke-width="1.5" />
                  <path d="M 36,34 L 40,28 L 44,34" fill="none" stroke="#cbd5e1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                  <text transform="translate(16, 150) rotate(-90)" fill="#475569" font-size="9.5" font-weight="bold" font-family="sans-serif" text-anchor="middle">Serviciabilidad</text>

                  <!-- Ticks y etiquetas dinámicas en el eje Y para pi y pt -->
                  <line x1="36" :y1="getYp(s.pi)" x2="40" :y2="getYp(s.pi)" stroke="#4f46e5" stroke-width="1.5" />
                  <text x="32" :y="getYp(s.pi) + 3" fill="#4f46e5" font-size="8.5" font-weight="bold" font-family="monospace" text-anchor="end">{{ formatVal(s.pi) }}</text>

                  <line x1="36" :y1="getYp(s.pt)" x2="40" :y2="getYp(s.pt)" stroke="#f59e0b" stroke-width="1.5" />
                  <text x="32" :y="getYp(s.pt) + 3" fill="#f59e0b" font-size="8.5" font-weight="bold" font-family="monospace" text-anchor="end">{{ formatVal(s.pt) }}</text>

                  <!-- Línea horizontal punteada en X=300 (Fin del periodo T) -->
                  <line x1="300" y1="30" x2="300" y2="280" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="2,2" />

                  <!-- Curva de pérdida de serviciabilidad (Cóncava hacia abajo) -->
                  <path :d="servCurvePath" fill="none" stroke="#4f46e5" stroke-width="3" stroke-linecap="round" class="pointer-events-none" />

                  <!-- Línea horizontal de Serviciabilidad Inicial (pi) - INTERACTIVA -->
                  <!-- Línea visible -->
                  <line
                    x1="40"
                    :y1="getYp(s.pi)"
                    x2="300"
                    :y2="getYp(s.pi)"
                    stroke="#4f46e5"
                    :stroke-width="hoveredLine === 'pi' || activeHandleServ === 'pi' ? 3.5 : 2"
                    stroke-linecap="round"
                    class="pointer-events-none transition-all duration-150"
                    :opacity="hoveredLine === 'pi' || activeHandleServ === 'pi' ? 1.0 : 0.85"
                  />
                  <!-- Línea táctil invisible gruesa -->
                  <line
                    x1="40"
                    :y1="getYp(s.pi)"
                    x2="300"
                    :y2="getYp(s.pi)"
                    stroke="transparent"
                    stroke-width="14"
                    class="cursor-ns-resize"
                    @mousedown="startDragServ($event, 'pi')"
                    @touchstart="startDragServ($event, 'pi')"
                    @mouseenter="hoveredLine = 'pi'"
                    @mouseleave="hoveredLine = null"
                  />

                  <!-- Texto descriptivo Inicial -->
                  <text x="50" :y="getYp(s.pi) - 8" fill="#4f46e5" font-size="9" font-weight="bold" font-family="sans-serif" text-anchor="start" class="pointer-events-none">
                    Capacidad Original
                  </text>

                  <!-- Línea horizontal de Serviciabilidad Terminal (pt) - INTERACTIVA -->
                  <!-- Línea visible dashed -->
                  <line
                    x1="40"
                    :y1="getYp(s.pt)"
                    x2="300"
                    :y2="getYp(s.pt)"
                    stroke="#f59e0b"
                    :stroke-width="hoveredLine === 'pt' || activeHandleServ === 'pt' ? 3.5 : 2"
                    stroke-dasharray="4,4"
                    stroke-linecap="round"
                    class="pointer-events-none transition-all duration-150"
                    :opacity="hoveredLine === 'pt' || activeHandleServ === 'pt' ? 1.0 : 0.85"
                  />
                  <!-- Línea táctil invisible gruesa -->
                  <line
                    x1="40"
                    :y1="getYp(s.pt)"
                    x2="300"
                    :y2="getYp(s.pt)"
                    stroke="transparent"
                    stroke-width="14"
                    class="cursor-ns-resize"
                    @mousedown="startDragServ($event, 'pt')"
                    @touchstart="startDragServ($event, 'pt')"
                    @mouseenter="hoveredLine = 'pt'"
                    @mouseleave="hoveredLine = null"
                  />

                  <!-- Texto descriptivo Terminal -->
                  <text x="290" :y="getYp(s.pt) + 14" fill="#d97706" font-size="9" font-weight="bold" font-family="sans-serif" text-anchor="end" class="pointer-events-none">
                    Capacidad de falla
                  </text>

                  <!-- Indicador de ΔPSI (Acotador vertical entre ambas líneas) -->
                  <g v-if="getYp(s.pt) - getYp(s.pi) > 24" class="pointer-events-none">
                    <!-- Línea vertical con puntas de flecha en los extremos -->
                    <line x1="65" :y1="getYp(s.pi) + 6" x2="65" :y2="getYp(s.pt) - 6" stroke="#4f46e5" stroke-width="1.5" />
                    <path :d="`M 61,${getYp(s.pi) + 6} L 65,${getYp(s.pi)} L 69,${getYp(s.pi) + 6}`" fill="none" stroke="#4f46e5" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                    <path :d="`M 61,${getYp(s.pt) - 6} L 65,${getYp(s.pt)} L 69,${getYp(s.pt) - 6}`" fill="none" stroke="#4f46e5" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                    <!-- Rectángulo de fondo para el texto -->
                    <rect :x="71" :y="((getYp(s.pi) + getYp(s.pt)) / 2) - 8" width="45" height="15" fill="#ffffff" rx="3" opacity="0.9" />
                    <text x="73" :y="((getYp(s.pi) + getYp(s.pt)) / 2) + 3" fill="#4f46e5" font-size="9" font-weight="bold" font-family="sans-serif" text-anchor="start">
                      ΔPSI = {{ formatVal(s.DPSI) }}
                    </text>
                  </g>
                </svg>
              </div>

              <!-- Inputs Numéricos de Serviciabilidad -->
              <div class="grid grid-cols-2 gap-3 shrink-0">
                <div>
                  <label class="field-label">Servic. Inicial (pᵢ)</label>
                  <input v-model.number="s.pi" type="number" step="0.1" min="3.5" max="5.0" class="field-input font-mono" @change="validateServiciabilidad" />
                </div>
                <div>
                  <label class="field-label">Servic. Terminal (pₜ)</label>
                  <input v-model.number="s.pt" type="number" step="0.1" min="1.5" max="3.5" class="field-input font-mono" @change="validateServiciabilidad" />
                </div>
              </div>
              <div class="shrink-0">
                <label class="field-label">Pérdida de serviciabilidad (ΔPSI)</label>
                <input :value="s.DPSI" type="number" class="field-input font-mono" readonly />
              </div>
            </div>

            <!-- Tránsito Panel -->
            <div v-if="activeParam === 'traffic'" class="space-y-4">
              <div>
                <div class="flex items-center justify-between mb-1">
                  <label class="field-label mb-0">Ejes equivalentes (W₁₈)</label>
                  <button 
                    type="button" 
                    @click="isTrafficHelpModalOpen = true" 
                    class="text-[10px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer bg-indigo-50 hover:bg-indigo-100/80 px-2 py-0.5 rounded-md transition-colors select-none"
                  >
                    <span>Calculadora</span>
                    <span class="w-3.5 h-3.5 flex items-center justify-center bg-indigo-600 text-white rounded-full text-[9px]">?</span>
                  </button>
                </div>
                <input v-model.number="s.W18" type="number" step="100000" min="1000" class="field-input font-mono" />
              </div>
            </div>

            <!-- Materiales Panel -->
            <div v-if="activeParam === 'materials'" class="space-y-4 pr-1">
              <!-- Carpeta asfáltica -->
              <div class="p-3 bg-slate-50/30 border border-slate-100 rounded-xl space-y-2">
                <div class="flex justify-between items-center">
                  <span class="text-[10px] font-bold text-slate-800 uppercase tracking-wider block">Carpeta asfáltica</span>
                  <button type="button" @click="isA1HelpModalOpen = true" class="text-[9px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer bg-indigo-50 hover:bg-indigo-100/80 px-1.5 py-0.5 rounded-md transition-colors select-none">
                    <span>Guía</span><span class="w-3 h-3 flex items-center justify-center bg-indigo-600 text-white rounded-full text-[8px]">?</span>
                  </button>
                </div>
                <div class="flex items-center justify-between gap-4">
                  <span class="text-xs text-slate-500 font-medium">Coeficiente a₁</span>
                  <input type="number" step="0.001" v-model.number="s.a1" class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right" />
                </div>
              </div>

              <!-- Base granular -->
              <div v-if="s.numCapas >= 2" class="p-3 bg-slate-50/30 border border-slate-100 rounded-xl space-y-2">
                <div class="flex justify-between items-center">
                  <span class="text-[10px] font-bold text-stone-600 uppercase tracking-wider block">Base granular</span>
                  <button type="button" @click="isA2HelpModalOpen = true" class="text-[9px] font-bold text-stone-600 hover:text-stone-800 flex items-center gap-1 cursor-pointer bg-stone-100 hover:bg-stone-200 px-1.5 py-0.5 rounded-md transition-colors select-none">
                    <span>Guía</span><span class="w-3 h-3 flex items-center justify-center bg-stone-600 text-white rounded-full text-[8px]">?</span>
                  </button>
                </div>
                <div class="flex items-center justify-between gap-4">
                  <span class="text-xs text-slate-500 font-medium">Mr₁ (psi)</span>
                  <input type="number" step="1000" v-model.number="s.Mr1" class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right" />
                </div>
                <div class="flex items-center justify-between gap-4">
                  <span class="text-xs text-slate-500 font-medium">Coeficiente a₂</span>
                  <input type="number" step="0.001" v-model.number="s.a2" class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right" />
                </div>
                <div class="flex items-center justify-between gap-4">
                  <div class="flex items-center gap-1">
                    <span class="text-xs text-slate-500 font-medium">Drenaje m₂</span>
                    <button type="button" @click="openDrainageModal('m2')" class="text-slate-400 hover:text-slate-600 bg-slate-100 hover:bg-slate-200 w-4 h-4 rounded-full flex items-center justify-center text-[8px] font-bold transition-colors">?</button>
                  </div>
                  <input type="number" step="0.01" v-model.number="s.m2" class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right" />
                </div>
              </div>

              <!-- Sub-base -->
              <div v-if="s.numCapas === 3" class="p-3 bg-slate-50/30 border border-slate-100 rounded-xl space-y-2">
                <div class="flex justify-between items-center">
                  <span class="text-[10px] font-bold text-amber-800/80 uppercase tracking-wider block">Sub-base granular</span>
                  <button type="button" @click="isA3HelpModalOpen = true" class="text-[9px] font-bold text-amber-600 hover:text-amber-800 flex items-center gap-1 cursor-pointer bg-amber-50 hover:bg-amber-100/80 px-1.5 py-0.5 rounded-md transition-colors select-none">
                    <span>Guía</span><span class="w-3 h-3 flex items-center justify-center bg-amber-500 text-white rounded-full text-[8px]">?</span>
                  </button>
                </div>
                <div class="flex items-center justify-between gap-4">
                  <span class="text-xs text-slate-500 font-medium">Mr₂ (psi)</span>
                  <input type="number" step="1000" v-model.number="s.Mr2" class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right" />
                </div>
                <div class="flex items-center justify-between gap-4">
                  <span class="text-xs text-slate-500 font-medium">Coeficiente a₃</span>
                  <input type="number" step="0.001" v-model.number="s.a3" class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right" />
                </div>
                <div class="flex items-center justify-between gap-4">
                  <div class="flex items-center gap-1">
                    <span class="text-xs text-slate-500 font-medium">Drenaje m₃</span>
                    <button type="button" @click="openDrainageModal('m3')" class="text-slate-400 hover:text-slate-600 bg-slate-100 hover:bg-slate-200 w-4 h-4 rounded-full flex items-center justify-center text-[8px] font-bold transition-colors">?</button>
                  </div>
                  <input type="number" step="0.01" v-model.number="s.m3" class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right" />
                </div>
              </div>

              <!-- Subrasante -->
              <div class="p-3 bg-slate-50/30 border border-slate-100 rounded-xl space-y-2">
                <div class="flex justify-between items-center">
                  <span class="text-[10px] font-bold text-emerald-800 uppercase tracking-wider block">Subrasante</span>
                  <button type="button" @click="isMrHelpModalOpen = true" class="text-[9px] font-bold text-emerald-600 hover:text-emerald-800 flex items-center gap-1 cursor-pointer bg-emerald-50 hover:bg-emerald-100/80 px-1.5 py-0.5 rounded-md transition-colors select-none">
                    <span>Guía</span><span class="w-3 h-3 flex items-center justify-center bg-emerald-500 text-white rounded-full text-[8px]">?</span>
                  </button>
                </div>
                <div class="flex items-center justify-between gap-4">
                  <span class="text-xs text-slate-500 font-medium">Mr₃ (psi)</span>
                  <input type="number" step="500" v-model.number="s.Mr3" class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal de Guía de Valores So -->
    <Transition name="modal-fade">
      <div v-if="isHelpModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div @click.stop class="bg-white rounded-2xl border border-slate-100 shadow-2xl w-full max-w-md overflow-hidden flex flex-col">
          <!-- Cabecera -->
          <div class="px-6 py-4 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
            <h3 class="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Guía de Error Estándar Combinado (S₀)
            </h3>
            <button 
              @click="isHelpModalOpen = false" 
              class="w-6 h-6 flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-200/50 rounded-full font-bold text-sm cursor-pointer transition-colors"
            >
              ✕
            </button>
          </div>
          
          <!-- Contenido -->
          <div class="p-6 space-y-4 text-xs text-slate-600 leading-relaxed overflow-y-auto max-h-[70vh]">
            <p>
              El valor de <strong>S₀ (desviación estándar combinada)</strong> representa la incertidumbre acumulada en la predicción del tránsito (W₁₈) y el comportamiento estructural del pavimento a lo largo del tiempo.
            </p>
            
            <div class="border border-slate-100 rounded-xl overflow-hidden">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="bg-slate-50 text-[9px] uppercase font-bold text-slate-400 border-b border-slate-100">
                    <th class="px-4 py-2">Tipo de Pavimento</th>
                    <th class="px-4 py-2 text-center">Nuevos</th>
                    <th class="px-4 py-2 text-center">Rehabilitación</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="border-b border-slate-100/50 hover:bg-slate-50/30 transition-colors">
                    <td class="px-4 py-2.5 font-semibold text-slate-700">Flexible (Asfalto)</td>
                    <td class="px-4 py-2.5 text-center text-indigo-600 font-bold">0.45</td>
                    <td class="px-4 py-2.5 text-center text-slate-700">0.49</td>
                  </tr>
                  <tr class="hover:bg-slate-50/30 transition-colors">
                    <td class="px-4 py-2.5 font-semibold text-slate-700">Rígido (Concreto)</td>
                    <td class="px-4 py-2.5 text-center text-indigo-600 font-bold">0.35</td>
                    <td class="px-4 py-2.5 text-center text-slate-700">0.39</td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div class="p-3 bg-amber-50/50 border border-amber-100 rounded-xl space-y-1">
              <span class="text-[10px] font-bold text-amber-800 uppercase tracking-wider block">Nota de Diseño</span>
              <p class="text-amber-800/90 text-[11px] leading-relaxed">
                La Guía AASHTO 1993 recomienda usar <strong>0.45</strong> para pavimentos flexibles convencionales y <strong>0.49</strong> para sobrecapas o rehabilitaciones debido a la mayor variabilidad del pavimento existente.
              </p>
            </div>
            
            <div class="p-3 bg-slate-50 border border-slate-100 rounded-xl">
              <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Accesos Rápidos</span>
              <p class="text-slate-400 mb-2">Haz clic en un botón para aplicar el valor sugerido de inmediato:</p>
              <div class="flex flex-wrap gap-2">
                <button 
                  @click="applySoValue(0.45)"
                  class="px-2.5 py-1 bg-white border border-slate-200 hover:border-indigo-600 rounded-lg font-bold text-indigo-600 hover:bg-indigo-50/30 transition-all cursor-pointer shadow-sm active:scale-95"
                >
                  Flexible Nuevo (0.45)
                </button>
                <button 
                  @click="applySoValue(0.49)"
                  class="px-2.5 py-1 bg-white border border-slate-200 hover:border-indigo-600 rounded-lg font-bold text-slate-700 hover:bg-indigo-50/30 transition-all cursor-pointer shadow-sm active:scale-95"
                >
                  Flexible Rehab (0.49)
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal de Guía de Confiabilidad R -->
    <Transition name="modal-fade">
      <div v-if="isReliabilityHelpModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div @click.stop class="bg-white rounded-2xl border border-slate-100 shadow-2xl w-full max-w-md overflow-hidden flex flex-col">
          <!-- Cabecera -->
          <div class="px-6 py-4 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
            <h3 class="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Guía de Nivel de Confianza (R)
            </h3>
            <button 
              @click="isReliabilityHelpModalOpen = false" 
              class="w-6 h-6 flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-200/50 rounded-full font-bold text-sm cursor-pointer transition-colors"
            >
              ✕
            </button>
          </div>
          
          <!-- Contenido -->
          <div class="p-6 space-y-4 text-xs text-slate-600 leading-relaxed overflow-y-auto max-h-[70vh]">
            <p>
              La <strong>confiabilidad (R)</strong> se define como la probabilidad de que el pavimento diseñado se comporte de manera satisfactoria durante toda su vida de proyecto, bajo las solicitaciones de carga e intemperismo, o la probabilidad de que los problemas de deformación y fallas estén por debajo de los niveles permisibles.
            </p>
            
            <div class="p-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Valores del Nivel de Confianza R (%) recomendados:
            </div>

            <div class="border border-slate-100 rounded-xl overflow-hidden">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="bg-slate-50 text-[9px] uppercase font-bold text-slate-400 border-b border-slate-100">
                    <th class="px-4 py-2">Tipo de Camino</th>
                    <th class="px-4 py-2 text-center">Zonas Urbanas</th>
                    <th class="px-4 py-2 text-center">Zonas Rurales</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="border-b border-slate-100/50 hover:bg-slate-50/30 transition-colors">
                    <td class="px-4 py-2.5 font-semibold text-slate-700">Autopistas</td>
                    <td class="px-4 py-2.5 text-center text-indigo-600 font-bold">85 – 99.9%</td>
                    <td class="px-4 py-2.5 text-center text-slate-700">80 – 99.9%</td>
                  </tr>
                  <tr class="border-b border-slate-100/50 hover:bg-slate-50/30 transition-colors">
                    <td class="px-4 py-2.5 font-semibold text-slate-700">Carreteras de 1er Orden</td>
                    <td class="px-4 py-2.5 text-center text-indigo-600 font-bold">80 – 99%</td>
                    <td class="px-4 py-2.5 text-center text-slate-700">75 – 95%</td>
                  </tr>
                  <tr class="border-b border-slate-100/50 hover:bg-slate-50/30 transition-colors">
                    <td class="px-4 py-2.5 font-semibold text-slate-700">Carreteras Secundarias</td>
                    <td class="px-4 py-2.5 text-center text-indigo-600 font-bold">80 – 95%</td>
                    <td class="px-4 py-2.5 text-center text-slate-700">75 – 95%</td>
                  </tr>
                  <tr class="hover:bg-slate-50/30 transition-colors">
                    <td class="px-4 py-2.5 font-semibold text-slate-700">Caminos Vecinales</td>
                    <td class="px-4 py-2.5 text-center text-indigo-600 font-bold">50 – 80%</td>
                    <td class="px-4 py-2.5 text-center text-slate-700">50 – 80%</td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div class="text-[9px] text-slate-400 italic">
              Fuente: AASHTO, Guide for Design of Pavement Structures 1993.
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal de Guía de Serviciabilidad PSI -->
    <Transition name="modal-fade">
      <div v-if="isServHelpModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div @click.stop class="bg-white rounded-2xl border border-slate-100 shadow-2xl w-full max-w-md overflow-hidden flex flex-col">
          <!-- Cabecera -->
          <div class="px-6 py-4 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
            <h3 class="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Guía de Índice de Serviciabilidad (PSI)
            </h3>
            <button 
              @click="isServHelpModalOpen = false" 
              class="w-6 h-6 flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-200/50 rounded-full font-bold text-sm cursor-pointer transition-colors"
            >
              ✕
            </button>
          </div>
          
          <!-- Contenido -->
          <div class="p-6 space-y-4 text-xs text-slate-600 leading-relaxed overflow-y-auto max-h-[70vh]">
            <p>
              El <strong>Índice de Serviciabilidad</strong> se define como la condición necesaria de un pavimento para proveer a los usuarios un manejo seguro y confortable en un determinado momento. Escala de valoración original de la AASHTO:
            </p>
            
            <div class="border border-slate-100 rounded-xl overflow-hidden">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="bg-slate-50 text-[9px] uppercase font-bold text-slate-400 border-b border-slate-100">
                    <th class="px-4 py-2">Índice de Serviciabilidad (PSI)</th>
                    <th class="px-4 py-2 text-center">Calificación</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="border-b border-slate-100/50 hover:bg-slate-50/30 transition-colors">
                    <td class="px-4 py-2.5 font-semibold text-slate-700">5.0 – 4.0</td>
                    <td class="px-4 py-2.5 text-center text-indigo-600 font-bold">Muy buena</td>
                  </tr>
                  <tr class="border-b border-slate-100/50 hover:bg-slate-50/30 transition-colors">
                    <td class="px-4 py-2.5 font-semibold text-slate-700">4.0 – 3.0</td>
                    <td class="px-4 py-2.5 text-center text-indigo-600 font-bold">Buena</td>
                  </tr>
                  <tr class="border-b border-slate-100/50 hover:bg-slate-50/30 transition-colors">
                    <td class="px-4 py-2.5 font-semibold text-slate-700">3.0 – 2.0</td>
                    <td class="px-4 py-2.5 text-center text-slate-700 font-semibold">Regular</td>
                  </tr>
                  <tr class="border-b border-slate-100/50 hover:bg-slate-50/30 transition-colors">
                    <td class="px-4 py-2.5 font-semibold text-slate-700">2.0 – 1.0</td>
                    <td class="px-4 py-2.5 text-center text-amber-600 font-semibold">Mala</td>
                  </tr>
                  <tr class="hover:bg-slate-50/30 transition-colors">
                    <td class="px-4 py-2.5 font-semibold text-slate-700">1.0 – 0.0</td>
                    <td class="px-4 py-2.5 text-center text-red-500 font-bold">Muy mala</td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div class="text-[9px] text-slate-400 italic">
              Fuente: AASHTO, Guide for Design of Pavement Structures 1993.
            </div>

            <div class="p-3 bg-indigo-50/50 border border-indigo-100 rounded-xl space-y-2">
              <span class="text-[10px] font-bold text-indigo-800 uppercase tracking-wider block">Recomendaciones de Diseño</span>
              <ul class="list-disc pl-4 space-y-1.5 text-slate-600 text-[11px] leading-relaxed">
                <li><strong>Serviciabilidad Inicial (pᵢ)</strong>: Condición del pavimento recién construido. Recomendado: <strong>4.2</strong> para pavimentos flexibles.</li>
                <li><strong>Serviciabilidad Terminal (pₑ o pₜ)</strong>: Menor serviciabilidad aceptable antes de rehabilitación. Recomendado: <strong>2.5</strong> para vías principales y <strong>2.0</strong> para secundarias/vecinales.</li>
              </ul>
            </div>
            
            <div class="p-3 bg-slate-50 border border-slate-100 rounded-xl">
              <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Accesos Rápidos</span>
              <p class="text-slate-400 mb-2">Haz clic para aplicar la combinación de diseño recomendada:</p>
              <div class="flex flex-wrap gap-2">
                <button 
                  @click="applyServPresets(4.2, 2.5)"
                  class="px-2.5 py-1 bg-white border border-slate-200 hover:border-indigo-600 rounded-lg font-bold text-indigo-600 hover:bg-indigo-50/30 transition-all cursor-pointer shadow-sm active:scale-95 text-[10px]"
                >
                  Vía Principal / Autopista (4.2 - 2.5)
                </button>
                <button 
                  @click="applyServPresets(4.0, 2.0)"
                  class="px-2.5 py-1 bg-white border border-slate-200 hover:border-indigo-600 rounded-lg font-bold text-slate-700 hover:bg-indigo-50/30 transition-all cursor-pointer shadow-sm active:scale-95 text-[10px]"
                >
                  Vía Secundaria / Vecinal (4.0 - 2.0)
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal de Guía y Calculadora de W18 -->
    <Transition name="modal-fade">
      <div v-if="isTrafficHelpModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div @click.stop class="bg-white rounded-2xl border border-slate-100 shadow-2xl w-full max-w-lg overflow-hidden flex flex-col">
          <!-- Cabecera -->
          <div class="px-6 py-4 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
            <h3 class="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Estimación de Ejes Equivalentes (N)
            </h3>
            <button 
              @click="isTrafficHelpModalOpen = false" 
              class="w-6 h-6 flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-200/50 rounded-full font-bold text-sm cursor-pointer transition-colors"
            >
              ✕
            </button>
          </div>
          
          <!-- Contenido -->
          <div class="p-6 space-y-4 text-xs text-slate-600 leading-relaxed overflow-y-auto max-h-[75vh]">
            <p>
              Procedimiento de estimación basado en la Guía AASHTO 93 empleando integración continua para el crecimiento:
            </p>
            
            <div class="grid grid-cols-2 gap-4 gap-y-5">
              <!-- TPDS -->
              <div>
                <div class="flex items-center justify-between mb-1">
                  <label class="field-label text-[10px] mb-0">TPDS inicial</label>
                  <button type="button" @click="calcHelpKey = 'tpds'" class="text-[9px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer bg-indigo-50 hover:bg-indigo-100/80 px-1.5 py-0.5 rounded-md transition-colors select-none"><span>Guía</span><span class="w-3 h-3 flex items-center justify-center bg-indigo-600 text-white rounded-full text-[8px]">?</span></button>
                </div>
                <input v-model.number="calcTraffic.tpds" type="number" class="field-input font-mono w-full" />
              </div>
              <!-- Factor Camión FC -->
              <div>
                <div class="flex items-center justify-between mb-1">
                  <label class="field-label text-[10px] mb-0">Factor Camión (FC)</label>
                  <button type="button" @click="calcHelpKey = 'fc'" class="text-[9px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer bg-indigo-50 hover:bg-indigo-100/80 px-1.5 py-0.5 rounded-md transition-colors select-none"><span>Guía</span><span class="w-3 h-3 flex items-center justify-center bg-indigo-600 text-white rounded-full text-[8px]">?</span></button>
                </div>
                <input v-model.number="calcTraffic.fc" type="number" step="0.01" class="field-input font-mono w-full" />
              </div>
              <!-- k1 -->
              <div>
                <div class="flex items-center justify-between mb-1">
                  <label class="field-label text-[10px] mb-0">% Pesados (k₁)</label>
                  <button type="button" @click="calcHelpKey = 'k1'" class="text-[9px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer bg-indigo-50 hover:bg-indigo-100/80 px-1.5 py-0.5 rounded-md transition-colors select-none"><span>Guía</span><span class="w-3 h-3 flex items-center justify-center bg-indigo-600 text-white rounded-full text-[8px]">?</span></button>
                </div>
                <div class="flex items-center gap-2">
                  <input v-model.number="calcTraffic.k1" type="number" step="1" max="100" class="field-input font-mono w-full" />
                  <button @click="showK1Estimator = !showK1Estimator" class="px-2 py-[7px] bg-indigo-50 border border-indigo-100 hover:bg-indigo-100 text-indigo-600 rounded-lg text-[10px] font-bold shrink-0 transition-colors" title="Estimar k1">🧮</button>
                </div>
              </div>
              <!-- k2 -->
              <div>
                <div class="flex items-center justify-between mb-1">
                  <label class="field-label text-[10px] mb-0">% Carril (k₂)</label>
                  <button type="button" @click="calcHelpKey = 'k2'" class="text-[9px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer bg-indigo-50 hover:bg-indigo-100/80 px-1.5 py-0.5 rounded-md transition-colors select-none"><span>Guía</span><span class="w-3 h-3 flex items-center justify-center bg-indigo-600 text-white rounded-full text-[8px]">?</span></button>
                </div>
                <select v-model.number="calcTraffic.k2" class="field-input font-mono w-full text-[10px] py-[7px]">
                  <option :value="100">1 carril/dir (100%)</option>
                  <option :value="80">3 carr/1 dir (80%)</option>
                  <option :value="50">2 carr/1 dir (50%)</option>
                  <option :value="45">4 carr/2 dir (45%)</option>
                  <option :value="calcTraffic.k2" v-if="![100,80,50,45].includes(calcTraffic.k2)">Personalizado ({{calcTraffic.k2}}%)</option>
                </select>
              </div>
              <!-- r -->
              <div>
                <div class="flex items-center justify-between mb-1">
                  <label class="field-label text-[10px] mb-0">Crecimiento r (%)</label>
                  <button type="button" @click="calcHelpKey = 'r'" class="text-[9px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer bg-indigo-50 hover:bg-indigo-100/80 px-1.5 py-0.5 rounded-md transition-colors select-none"><span>Guía</span><span class="w-3 h-3 flex items-center justify-center bg-indigo-600 text-white rounded-full text-[8px]">?</span></button>
                </div>
                <input v-model.number="calcTraffic.r" type="number" step="0.1" class="field-input font-mono w-full" />
              </div>
              <!-- n -->
              <div>
                <div class="flex items-center justify-between mb-1">
                  <label class="field-label text-[10px] mb-0">Período n (años)</label>
                  <button type="button" @click="calcHelpKey = 'n'" class="text-[9px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 cursor-pointer bg-indigo-50 hover:bg-indigo-100/80 px-1.5 py-0.5 rounded-md transition-colors select-none"><span>Guía</span><span class="w-3 h-3 flex items-center justify-center bg-indigo-600 text-white rounded-full text-[8px]">?</span></button>
                </div>
                <input v-model.number="calcTraffic.n" type="number" step="1" class="field-input font-mono w-full" />
              </div>
            </div>

            <!-- Estimador k1 -->
            <div v-if="showK1Estimator" class="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
              <div class="flex justify-between items-center mb-1">
                 <h4 class="text-[10px] font-bold text-slate-700 uppercase">Estimador de k₁ (% Vehículos Pesados)</h4>
                 <button @click="showK1Estimator = false" class="text-slate-400 hover:text-slate-600 font-bold">✕</button>
              </div>
              <div class="grid grid-cols-2 gap-3">
                 <div><label class="field-label text-[9px] mb-1">Buses (%)</label><input v-model.number="calcK1.buses" type="number" class="field-input font-mono text-[10px] w-full" /></div>
                 <div><label class="field-label text-[9px] mb-1">Camiones C2 (%)</label><input v-model.number="calcK1.c2" type="number" class="field-input font-mono text-[10px] w-full" /></div>
                 <div><label class="field-label text-[9px] mb-1">Camiones C3+ (%)</label><input v-model.number="calcK1.c3" type="number" class="field-input font-mono text-[10px] w-full" /></div>
                 <div><label class="field-label text-[9px] mb-1">Articulados (%)</label><input v-model.number="calcK1.articulados" type="number" class="field-input font-mono text-[10px] w-full" /></div>
              </div>
              <div class="flex items-center justify-between mt-2 pt-2 border-t border-slate-200">
                <span class="text-[10px] text-slate-600 font-bold">Total estimado: <span class="text-indigo-600 text-sm">{{ estimatedK1Sum }}%</span></span>
                <button @click="applyEstimatedK1" class="px-3 py-1 bg-indigo-600 text-white rounded text-[9px] font-bold hover:bg-indigo-700">Aplicar</button>
              </div>
            </div>

            <!-- Fórmula Visual y Desarrollo -->
            <div id="pdf-equations-container" class="p-4 bg-slate-50 border border-slate-100 rounded-xl overflow-x-auto">
              <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-2 text-center">Ecuación General</span>
              <div v-html="formulaGeneralHtml" class="text-center"></div>
              
              <div class="mt-4 pt-3 border-t border-slate-200">
                <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-2 text-center">Desarrollo del Cálculo</span>
                <div v-html="formulaPasoHtml" class="text-center text-[10px] scale-90 sm:scale-100 transform origin-top"></div>
              </div>
            </div>

            <!-- Resultado -->
            <div class="p-4 bg-indigo-50 border border-indigo-100 rounded-xl flex items-center justify-between">
              <div>
                <span class="text-[10px] font-bold text-indigo-800 uppercase tracking-wider block">Resultado Estimado (N)</span>
                <span class="text-lg font-bold text-indigo-600 font-mono">{{ isNaN(calculatedW18) ? 0 : Math.round(calculatedW18).toLocaleString('en-US') }}</span>
              </div>
              <div class="flex items-center gap-2">
                <button 
                  @click="exportTrafficPDF"
                  class="px-3 py-2 bg-white border border-indigo-200 text-indigo-600 rounded-lg font-bold hover:bg-indigo-100 transition-colors shadow-sm active:scale-95 text-xs flex items-center gap-1"
                  title="Exportar memoria de cálculo a PDF"
                >
                  📄 PDF
                </button>
                <button 
                  @click="applyCalculatedTraffic"
                  class="px-4 py-2 bg-indigo-600 text-white rounded-lg font-bold hover:bg-indigo-700 transition-colors shadow-md shadow-indigo-200 active:scale-95 text-xs"
                >
                  Aplicar W₁₈
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal de Guías de Parámetros del Cálculo -->
    <Transition name="modal-fade">
      <div v-if="calcHelpKey" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div @click.stop class="bg-white rounded-2xl border border-slate-100 shadow-2xl w-full max-w-md overflow-hidden flex flex-col">
          <div class="px-6 py-4 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
            <h3 class="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Guía: {{ calcHelpTitles[calcHelpKey] }}
            </h3>
            <button 
              @click="calcHelpKey = null" 
              class="w-6 h-6 flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-200/50 rounded-full font-bold text-sm cursor-pointer transition-colors"
            >
              ✕
            </button>
          </div>
          
          <div class="p-6 space-y-4 text-xs text-slate-600 leading-relaxed overflow-y-auto max-h-[70vh]">
            <template v-if="calcHelpKey === 'tpds'">
              <p>El <strong>Tránsito Promedio Diario Semanal (TPDS)</strong> corresponde al volumen promedio diario de vehículos al inicio del período de diseño.</p>
              <ul class="list-disc pl-4 space-y-1">
                <li>Si el conteo incluye todos los vehículos (autos, motos, etc.), asegúrate de configurar correctamente el porcentaje de vehículos pesados (k₁).</li>
                <li>Si el TPDS ingresado contabiliza <em>únicamente</em> vehículos comerciales pesados, el parámetro k₁ debe ser 100%.</li>
              </ul>
            </template>
            <template v-else-if="calcHelpKey === 'fc'">
              <p>El <strong>Factor Camión (FC)</strong> o coeficiente de daño representa cuántos ejes equivalentes de 8.2 toneladas (18 kips) equivale el paso de un vehículo comercial promedio.</p>
              <p>Se puede determinar de dos formas:</p>
              <ul class="list-disc pl-4 space-y-1">
                <li>Promediando ponderadamente los factores de daño de cada tipo de camión respecto a su volumen.</li>
                <li>Con un estudio de pesaje por ejes, multiplicando la frecuencia de ejes por los Factores de Equivalencia de Carga (FEC).</li>
              </ul>
            </template>
            <template v-else-if="calcHelpKey === 'k1'">
              <p>El parámetro <strong>k₁</strong> es el porcentaje de vehículos pesados comerciales respecto al flujo vehicular total.</p>
              <div class="p-3 bg-indigo-50/50 border border-indigo-100 rounded-xl">
                <strong>Ejemplo:</strong> Si el TPDS es de 775 veh/día y los buses (9%) más los camiones (30%) suman 39%, entonces k₁ = 39%.
              </div>
            </template>
            <template v-else-if="calcHelpKey === 'k2'">
              <p>El parámetro <strong>k₂</strong> estima el porcentaje del tránsito pesado total que circulará exclusivamente por el <em>carril de diseño</em> (el carril más cargado).</p>
              <table class="w-full text-left border-collapse border border-slate-100 rounded-xl overflow-hidden mt-2">
                <thead>
                  <tr class="bg-slate-50 text-[9px] uppercase font-bold text-slate-400">
                    <th class="px-3 py-2 border-b border-slate-100">Configuración de la vía</th>
                    <th class="px-3 py-2 border-b border-slate-100">Valor de k₂ (%)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="border-b border-slate-100">
                    <td class="px-3 py-2">Dos carriles (uno por dirección)</td>
                    <td class="px-3 py-2 font-bold text-indigo-600">50%</td>
                  </tr>
                  <tr class="border-b border-slate-100">
                    <td class="px-3 py-2">Cuatro carriles (dos por dirección)</td>
                    <td class="px-3 py-2 font-bold text-indigo-600">45%</td>
                  </tr>
                  <tr>
                    <td class="px-3 py-2">Tres carriles (en una dirección)</td>
                    <td class="px-3 py-2 font-bold text-indigo-600">80%</td>
                  </tr>
                </tbody>
              </table>
            </template>
            <template v-else-if="calcHelpKey === 'r'">
              <p>La <strong>Tasa de Crecimiento (r)</strong> estima el aumento porcentual anual del tránsito comercial durante la vida útil del pavimento.</p>
              <p>Se obtiene normalmente mediante la regresión de series históricas del TPDS, o basándose en el crecimiento económico proyectado de la región. Valores comunes están entre 1% y 5%.</p>
            </template>
            <template v-else-if="calcHelpKey === 'n'">
              <p>El <strong>Período de diseño (n)</strong> es la vida útil estimada (en años) durante la cual el pavimento soportará las cargas sin requerir rehabilitación mayor.</p>
              <ul class="list-disc pl-4 space-y-1">
                <li>Vías de bajo volumen o rurales: <strong>10 a 15 años</strong></li>
                <li>Vías principales y autopistas: <strong>15 a 20 años o más</strong></li>
              </ul>
            </template>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal de Guía a1 (Carpeta Asfáltica) -->
    <Transition name="modal-fade">
      <div v-if="isA1HelpModalOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div @click.stop class="bg-white rounded-2xl border border-slate-100 shadow-2xl w-full max-w-md overflow-hidden flex flex-col">
          <div class="px-6 py-4 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
            <h3 class="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Estimación de a₁ (Concreto Asfáltico)
            </h3>
            <button 
              @click="isA1HelpModalOpen = false" 
              class="w-6 h-6 flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-200/50 rounded-full font-bold text-sm cursor-pointer transition-colors"
            >
              ✕
            </button>
          </div>
          
          <div class="p-6 space-y-4 text-xs text-slate-600 leading-relaxed overflow-y-auto max-h-[70vh]">
            <p>
              El coeficiente estructural <strong>a₁</strong> de la superficie de concreto asfáltico se correlaciona con su Módulo Elástico (E<sub>AC</sub>) a 68°F (20°C).
            </p>
            <p class="text-[10px] text-slate-500 italic">Basado en la Figura IV.3 de la Guía AASHTO 1993.</p>

            <div class="border border-slate-100 rounded-xl bg-white p-3 relative select-none shadow-sm">
              <div class="flex justify-between text-[8px] font-bold text-slate-400 mb-1 px-1 uppercase tracking-widest">
                <span>100k psi</span>
                <span>Módulo E_AC</span>
                <span>500k psi</span>
              </div>
              <svg 
                ref="svgGraphA1"
                viewBox="0 0 300 150" 
                class="w-full h-auto cursor-crosshair overflow-visible touch-none"
                @mousedown="isDraggingGraph = true; handleGraphMove($event)"
                @mousemove="isDraggingGraph && handleGraphMove($event)"
                @mouseup="isDraggingGraph = false"
                @mouseleave="isDraggingGraph = false"
                @touchstart.prevent="isDraggingGraph = true; handleGraphMove($event)"
                @touchmove.prevent="isDraggingGraph && handleGraphMove($event)"
                @touchend.prevent="isDraggingGraph = false"
              >
                <!-- Grid Lines -->
                <line x1="0" y1="30" x2="300" y2="30" stroke="#f1f5f9" stroke-width="1"/>
                <line x1="0" y1="60" x2="300" y2="60" stroke="#f1f5f9" stroke-width="1"/>
                <line x1="0" y1="90" x2="300" y2="90" stroke="#f1f5f9" stroke-width="1"/>
                <line x1="0" y1="120" x2="300" y2="120" stroke="#f1f5f9" stroke-width="1"/>
                
                <line x1="75" y1="0" x2="75" y2="150" stroke="#f1f5f9" stroke-width="1"/>
                <line x1="150" y1="0" x2="150" y2="150" stroke="#f1f5f9" stroke-width="1"/>
                <line x1="225" y1="0" x2="225" y2="150" stroke="#f1f5f9" stroke-width="1"/>

                <!-- AASHTO Curve -->
                <polyline :points="a1CurvePoints" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
                
                <!-- Definition for Gradient -->
                <defs>
                  <linearGradient id="gradient-a1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#4f46e5" stop-opacity="0.3"/>
                    <stop offset="100%" stop-color="#4f46e5" stop-opacity="0.0"/>
                  </linearGradient>
                </defs>

                <!-- Active area under curve -->
                <polygon :points="`0,150 ${a1CurvePoints} 300,150`" fill="url(#gradient-a1)"/>
                
                <!-- Current User Selection -->
                <line :x1="userPointA1.sx" y1="150" :x2="userPointA1.sx" :y2="userPointA1.sy" stroke="#4f46e5" stroke-width="1.5" stroke-dasharray="3,3" />
                <line x1="0" :y1="userPointA1.sy" :x2="userPointA1.sx" :y2="userPointA1.sy" stroke="#4f46e5" stroke-width="1.5" stroke-dasharray="3,3" />
                
                <!-- User Point -->
                <circle :cx="userPointA1.sx" :cy="userPointA1.sy" r="4.5" fill="#4f46e5" stroke="white" stroke-width="1.5" class="shadow-sm transition-transform hover:scale-110" />
                
                <!-- Floating tooltip on graph -->
                <g :transform="`translate(${userPointA1.sx < 150 ? userPointA1.sx + 8 : userPointA1.sx - 85}, ${Math.max(0, userPointA1.sy - 15)})`" class="pointer-events-none">
                  <rect x="0" y="0" width="80" height="32" rx="4" fill="#1e293b" opacity="0.95" />
                  <text x="40" y="13" fill="white" font-size="10" font-family="monospace" text-anchor="middle" font-weight="bold">a₁: {{ estimatedA1.toFixed(3) }}</text>
                  <text x="40" y="24" fill="#94a3b8" font-size="8" font-family="monospace" text-anchor="middle">{{ (calcEac/1000).toFixed(0) }}k psi</text>
                </g>

                <!-- Y-Axis labels inside SVG -->
                <text x="5" y="10" fill="#cbd5e1" font-size="8" font-family="sans-serif">0.5</text>
                <text x="5" y="145" fill="#cbd5e1" font-size="8" font-family="sans-serif">0.0</text>
              </svg>
            </div>

            <div class="p-3 bg-indigo-50 border border-indigo-100 rounded-xl flex items-center justify-between gap-3 shadow-sm">
              <div class="flex-1">
                <label class="field-label text-[9px] mb-0.5 text-indigo-900/80">Módulo E<sub>AC</sub> (psi)</label>
                <input v-model.number="calcEac" type="number" step="10000" class="field-input font-mono w-full text-xs py-1.5 px-2 border-indigo-200/60 shadow-inner" placeholder="Ej: 400000" />
              </div>

              <div class="flex flex-col items-center justify-center bg-white px-3 py-1.5 rounded-lg border border-indigo-100 shadow-sm">
                <span class="text-[8px] font-bold text-indigo-800/60 uppercase tracking-wider block mb-0.5">a₁ Estimado</span>
                <span class="text-base font-bold text-indigo-600 font-mono leading-none">{{ estimatedA1.toFixed(3) }}</span>
              </div>
              
              <button 
                @click="applyEstimatedA1"
                class="px-4 py-2 h-full bg-indigo-600 text-white rounded-lg font-bold hover:bg-indigo-700 transition-colors shadow-sm active:scale-95 text-[10px] flex items-center justify-center whitespace-nowrap self-stretch"
              >
                Aplicar
              </button>
            </div>

          </div>
        </div>
      </div>
    </Transition>
    <!-- Modal de Guía a2 (Base Granular) -->
    <Transition name="modal-fade">
      <div v-if="isA2HelpModalOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div @click.stop class="bg-white rounded-2xl border border-slate-100 shadow-2xl w-full max-w-md overflow-hidden flex flex-col">
          <div class="px-6 py-4 bg-stone-50 border-b border-slate-100 flex items-center justify-between">
            <h3 class="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Estimación de a₂ (Base Granular)
            </h3>
            <button 
              @click="isA2HelpModalOpen = false" 
              class="w-6 h-6 flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-200/50 rounded-full font-bold text-sm cursor-pointer transition-colors"
            >
              ✕
            </button>
          </div>
          
          <div class="p-6 space-y-4 text-xs text-slate-600 leading-relaxed overflow-y-auto max-h-[70vh]">
            <p>
              El coeficiente estructural <strong>a₂</strong> de la capa base granular se estima a partir de su Módulo Resiliente (E<sub>SB</sub> o M<sub>R</sub>).
            </p>
            <p class="text-[10px] text-slate-500 italic">Basado en la Figura IV.4 de la Guía AASHTO 1993.</p>

            <div class="p-2 bg-stone-100 rounded-lg text-[10px] text-center font-mono text-stone-600 border border-stone-200 shadow-inner">
              a₂ = 0.249 · log₁₀(M<sub>R</sub>) - 0.977
            </div>

            <div class="border border-slate-100 rounded-xl bg-white p-3 relative select-none shadow-sm">
              <div class="flex justify-between text-[8px] font-bold text-slate-400 mb-2 px-1 uppercase tracking-widest text-center">
                <span>Ábaco de Alineación - Desliza verticalmente</span>
              </div>
              <svg 
                ref="svgGraphA2"
                viewBox="0 0 300 150" 
                class="w-full h-auto cursor-ns-resize overflow-visible touch-none"
                @mousedown="isDraggingGraphA2 = true; handleGraphMoveA2($event)"
                @mousemove="isDraggingGraphA2 && handleGraphMoveA2($event)"
                @mouseup="isDraggingGraphA2 = false"
                @mouseleave="isDraggingGraphA2 = false"
                @touchstart.prevent="isDraggingGraphA2 = true; handleGraphMoveA2($event)"
                @touchmove.prevent="isDraggingGraphA2 && handleGraphMoveA2($event)"
                @touchend.prevent="isDraggingGraphA2 = false"
              >
                <!-- Background -->
                <rect x="0" y="0" width="300" height="150" fill="#fafaf9" rx="6" />

                <!-- Vertical Scale Lines -->
                <!-- 1. a2 -->
                <line x1="40" y1="20" x2="40" y2="130" stroke="#78716c" stroke-width="1.5" />
                <text x="40" y="12" fill="#57534e" font-size="7" font-family="sans-serif" text-anchor="middle" font-weight="bold">a₂</text>
                <path d="M36 20 L40 20 M36 34.6 L40 34.6 M36 49.3 L40 49.3 M36 64 L40 64 M36 78.6 L40 78.6 M36 93.3 L40 93.3 M36 108 L40 108 M36 122.6 L40 122.6 M36 130 L40 130" stroke="#78716c" stroke-width="1" />
                <text x="34" y="22" fill="#78716c" font-size="6" text-anchor="end">0.20</text>
                <text x="34" y="66" fill="#78716c" font-size="6" text-anchor="end">0.14</text>
                <text x="34" y="95" fill="#78716c" font-size="6" text-anchor="end">0.10</text>
                <text x="34" y="125" fill="#78716c" font-size="6" text-anchor="end">0.06</text>

                <!-- 2. CBR -->
                <line x1="95" y1="20" x2="95" y2="130" stroke="#78716c" stroke-width="1.5" />
                <text x="95" y="12" fill="#57534e" font-size="7" font-family="sans-serif" text-anchor="middle" font-weight="bold">CBR</text>
                <path d="M91 64 L95 64 M91 84.5 L95 84.5 M91 111.6 L95 111.6" stroke="#78716c" stroke-width="1" />
                <text x="89" y="66" fill="#78716c" font-size="6" text-anchor="end">100</text>
                <text x="89" y="86.5" fill="#78716c" font-size="6" text-anchor="end">50</text>
                <text x="89" y="113.6" fill="#78716c" font-size="6" text-anchor="end">20</text>

                <!-- 3. R-Value -->
                <line x1="150" y1="20" x2="150" y2="130" stroke="#78716c" stroke-width="1.5" />
                <text x="150" y="12" fill="#57534e" font-size="7" font-family="sans-serif" text-anchor="middle" font-weight="bold">Valor R</text>
                <path d="M146 64 L150 64 M146 95 L150 95 M146 115 L150 115" stroke="#78716c" stroke-width="1" />
                <text x="144" y="66" fill="#78716c" font-size="6" text-anchor="end">85</text>
                <text x="144" y="97" fill="#78716c" font-size="6" text-anchor="end">70</text>
                <text x="144" y="117" fill="#78716c" font-size="6" text-anchor="end">50</text>

                <!-- 4. Texas Triax -->
                <line x1="205" y1="20" x2="205" y2="130" stroke="#78716c" stroke-width="1.5" />
                <text x="205" y="12" fill="#57534e" font-size="7" font-family="sans-serif" text-anchor="middle" font-weight="bold">Texas T.</text>
                <path d="M201 64 L205 64 M201 95 L205 95 M201 115 L205 115" stroke="#78716c" stroke-width="1" />
                <text x="199" y="66" fill="#78716c" font-size="6" text-anchor="end">2.0</text>
                <text x="199" y="97" fill="#78716c" font-size="6" text-anchor="end">2.5</text>
                <text x="199" y="117" fill="#78716c" font-size="6" text-anchor="end">4.0</text>

                <!-- 5. MR -->
                <line x1="260" y1="20" x2="260" y2="130" stroke="#78716c" stroke-width="1.5" />
                <text x="260" y="12" fill="#57534e" font-size="7" font-family="sans-serif" text-anchor="middle" font-weight="bold">M_R (x10³)</text>
                <path d="M260 42.7 L264 42.7 M260 65.4 L264 65.4 M260 97.7 L264 97.7 M260 120.4 L264 120.4" stroke="#78716c" stroke-width="1" />
                <text x="267" y="44.7" fill="#78716c" font-size="6" text-anchor="start">40</text>
                <text x="267" y="67.4" fill="#78716c" font-size="6" text-anchor="start">30</text>
                <text x="267" y="99.7" fill="#78716c" font-size="6" text-anchor="start">20</text>
                <text x="267" y="122.4" fill="#78716c" font-size="6" text-anchor="start">15</text>

                <!-- Horizontal Indicator Line -->
                <line x1="20" :y1="nomographY" x2="280" :y2="nomographY" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="4,2" />
                <circle cx="40" :cy="nomographY" r="3" fill="#dc2626" />
                <circle cx="260" :cy="nomographY" r="3" fill="#dc2626" />
                
                <!-- Dynamic Values -->
                <text x="280" :y="nomographY - 4" fill="#dc2626" font-size="8" font-family="monospace" font-weight="bold" text-anchor="end">{{ (calcMrBase/1000).toFixed(1) }}k</text>
                <text x="100" :y="nomographY - 4" fill="#dc2626" font-size="8" font-family="monospace" font-weight="bold" text-anchor="start">{{ calcCbrBase }}</text>
                <text x="20" :y="nomographY - 4" fill="#dc2626" font-size="8" font-family="monospace" font-weight="bold" text-anchor="start">{{ estimatedA2.toFixed(3) }}</text>
              </svg>
            </div>

            <div class="p-3 bg-stone-50 border border-stone-100 rounded-xl flex items-center justify-between gap-3 shadow-sm">
              <div class="flex-1">
                <label class="field-label text-[9px] mb-0.5 text-stone-700">Módulo M<sub>R</sub> (psi)</label>
                <input v-model.number="calcMrBase" type="number" step="1000" class="field-input font-mono w-full text-xs py-1.5 px-2 border-stone-200/60 shadow-inner" placeholder="Ej: 30000" />
              </div>

              <div class="flex-1">
                <label class="field-label text-[9px] mb-0.5 text-stone-700">CBR (%)</label>
                <input v-model.number="calcCbrBase" type="number" step="1" class="field-input font-mono w-full text-xs py-1.5 px-2 border-stone-200/60 shadow-inner" placeholder="Ej: 100" />
              </div>

              <div class="flex flex-col items-center justify-center bg-white px-3 py-1.5 rounded-lg border border-stone-100 shadow-sm">
                <span class="text-[8px] font-bold text-stone-500 uppercase tracking-wider block mb-0.5">a₂ Estimado</span>
                <span class="text-base font-bold text-stone-600 font-mono leading-none">{{ estimatedA2.toFixed(3) }}</span>
              </div>
              
              <button 
                @click="applyEstimatedA2"
                class="px-4 py-2 h-full bg-stone-600 text-white rounded-lg font-bold hover:bg-stone-700 transition-colors shadow-sm active:scale-95 text-[10px] flex items-center justify-center whitespace-nowrap self-stretch"
              >
                Aplicar
              </button>
            </div>

          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal de Guía a3 (Sub-base Granular) -->
    <Transition name="modal-fade">
      <div v-if="isA3HelpModalOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div @click.stop class="bg-white rounded-2xl border border-slate-100 shadow-2xl w-full max-w-md overflow-hidden flex flex-col">
          <div class="px-6 py-4 bg-amber-50/50 border-b border-amber-100/50 flex items-center justify-between">
            <h3 class="text-xs font-bold text-amber-900 uppercase tracking-wider">
              Estimación de a₃ (Sub-base Granular)
            </h3>
            <button 
              @click="isA3HelpModalOpen = false" 
              class="w-6 h-6 flex items-center justify-center text-amber-600/50 hover:text-amber-700 hover:bg-amber-100 rounded-full font-bold text-sm cursor-pointer transition-colors"
            >
              ✕
            </button>
          </div>
          
          <div class="p-6 space-y-4 text-xs text-slate-600 leading-relaxed overflow-y-auto max-h-[70vh]">
            <p>
              El coeficiente estructural <strong>a₃</strong> de la sub-base granular se estima a partir de su Módulo Resiliente (E<sub>SB</sub> o M<sub>R</sub>) o ensayos de resistencia.
            </p>
            <p class="text-[10px] text-slate-500 italic">Basado en la Figura IV.5 de la Guía AASHTO 1993.</p>

            <div class="p-2 bg-amber-100/50 rounded-lg text-[10px] text-center font-mono text-amber-800/80 border border-amber-200/50 shadow-inner">
              a₃ = 0.227 · log₁₀(M<sub>R</sub>) - 0.839
            </div>

            <div class="border border-slate-100 rounded-xl bg-white p-3 relative select-none shadow-sm">
              <div class="flex justify-between text-[8px] font-bold text-amber-600/60 mb-2 px-1 uppercase tracking-widest text-center">
                <span>Ábaco de Alineación - Desliza verticalmente</span>
              </div>
              <svg 
                ref="svgGraphA3"
                viewBox="0 0 300 150" 
                class="w-full h-auto cursor-ns-resize overflow-visible touch-none"
                @mousedown="isDraggingGraphA3 = true; handleGraphMoveA3($event)"
                @mousemove="isDraggingGraphA3 && handleGraphMoveA3($event)"
                @mouseup="isDraggingGraphA3 = false"
                @mouseleave="isDraggingGraphA3 = false"
                @touchstart.prevent="isDraggingGraphA3 = true; handleGraphMoveA3($event)"
                @touchmove.prevent="isDraggingGraphA3 && handleGraphMoveA3($event)"
                @touchend.prevent="isDraggingGraphA3 = false"
              >
                <rect x="0" y="0" width="300" height="150" fill="#fffbeb" rx="6" />

                <!-- Vertical Scale Lines -->
                <!-- 1. a3 -->
                <line x1="40" y1="20" x2="40" y2="130" stroke="#b45309" stroke-width="1.5" />
                <text x="40" y="12" fill="#92400e" font-size="7" font-family="sans-serif" text-anchor="middle" font-weight="bold">a₃</text>
                <path d="M36 31 L40 31 M36 53 L40 53 M36 75 L40 75 M36 97 L40 97 M36 119 L40 119" stroke="#b45309" stroke-width="1" />
                <text x="34" y="33" fill="#b45309" font-size="6" text-anchor="end">0.14</text>
                <text x="34" y="55" fill="#b45309" font-size="6" text-anchor="end">0.12</text>
                <text x="34" y="77" fill="#b45309" font-size="6" text-anchor="end">0.10</text>
                <text x="34" y="99" fill="#b45309" font-size="6" text-anchor="end">0.08</text>
                <text x="34" y="121" fill="#b45309" font-size="6" text-anchor="end">0.06</text>

                <!-- 2. CBR -->
                <line x1="95" y1="20" x2="95" y2="130" stroke="#b45309" stroke-width="1.5" />
                <text x="95" y="12" fill="#92400e" font-size="7" font-family="sans-serif" text-anchor="middle" font-weight="bold">CBR</text>
                <path d="M91 31 L95 31 M91 52 L95 52 M91 66 L95 66 M91 78 L95 78 M91 99 L95 99 M91 119 L95 119" stroke="#b45309" stroke-width="1" />
                <text x="89" y="33" fill="#b45309" font-size="6" text-anchor="end">100</text>
                <text x="89" y="54" fill="#b45309" font-size="6" text-anchor="end">50</text>
                <text x="89" y="68" fill="#b45309" font-size="6" text-anchor="end">30</text>
                <text x="89" y="80" fill="#b45309" font-size="6" text-anchor="end">20</text>
                <text x="89" y="101" fill="#b45309" font-size="6" text-anchor="end">10</text>
                <text x="89" y="121" fill="#b45309" font-size="6" text-anchor="end">5</text>

                <!-- 3. R-Value -->
                <line x1="150" y1="20" x2="150" y2="130" stroke="#b45309" stroke-width="1.5" />
                <text x="150" y="12" fill="#92400e" font-size="7" font-family="sans-serif" text-anchor="middle" font-weight="bold">Valor R</text>
                <path d="M146 31 L150 31 M146 53 L150 53 M146 75 L150 75 M146 97 L150 97 M146 119 L150 119" stroke="#b45309" stroke-width="1" />
                <text x="144" y="33" fill="#b45309" font-size="6" text-anchor="end">90</text>
                <text x="144" y="55" fill="#b45309" font-size="6" text-anchor="end">70</text>
                <text x="144" y="77" fill="#b45309" font-size="6" text-anchor="end">60</text>
                <text x="144" y="99" fill="#b45309" font-size="6" text-anchor="end">50</text>
                <text x="144" y="121" fill="#b45309" font-size="6" text-anchor="end">30</text>

                <!-- 4. Texas Triax -->
                <line x1="205" y1="20" x2="205" y2="130" stroke="#b45309" stroke-width="1.5" />
                <text x="205" y="12" fill="#92400e" font-size="7" font-family="sans-serif" text-anchor="middle" font-weight="bold">Texas T.</text>
                <path d="M201 31 L205 31 M201 56 L205 56 M201 91 L205 91 M201 121 L205 121" stroke="#b45309" stroke-width="1" />
                <text x="199" y="33" fill="#b45309" font-size="6" text-anchor="end">2.0</text>
                <text x="199" y="58" fill="#b45309" font-size="6" text-anchor="end">3.0</text>
                <text x="199" y="93" fill="#b45309" font-size="6" text-anchor="end">4.0</text>
                <text x="199" y="123" fill="#b45309" font-size="6" text-anchor="end">5.0</text>

                <!-- 5. MR -->
                <line x1="260" y1="20" x2="260" y2="130" stroke="#b45309" stroke-width="1.5" />
                <text x="260" y="12" fill="#92400e" font-size="7" font-family="sans-serif" text-anchor="middle" font-weight="bold">M_R (x10³)</text>
                <path d="M260 10.1 L264 10.1 M260 34.3 L264 34.3 M260 65.1 L264 65.1 M260 109.1 L264 109.1" stroke="#b45309" stroke-width="1" />
                <text x="267" y="12.1" fill="#b45309" font-size="6" text-anchor="start">25</text>
                <text x="267" y="36.3" fill="#b45309" font-size="6" text-anchor="start">20</text>
                <text x="267" y="67.1" fill="#b45309" font-size="6" text-anchor="start">15</text>
                <text x="267" y="111.1" fill="#b45309" font-size="6" text-anchor="start">10</text>

                <!-- Horizontal Indicator Line -->
                <line x1="20" :y1="nomographYA3" x2="280" :y2="nomographYA3" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4,2" />
                <circle cx="40" :cy="nomographYA3" r="3" fill="#d97706" />
                <circle cx="260" :cy="nomographYA3" r="3" fill="#d97706" />
                
                <!-- Dynamic Values -->
                <text x="280" :y="nomographYA3 - 4" fill="#d97706" font-size="8" font-family="monospace" font-weight="bold" text-anchor="end">{{ (calcMrSubBase/1000).toFixed(1) }}k</text>
                <text x="100" :y="nomographYA3 - 4" fill="#d97706" font-size="8" font-family="monospace" font-weight="bold" text-anchor="start">{{ calcCbrSubBase }}</text>
                <text x="20" :y="nomographYA3 - 4" fill="#d97706" font-size="8" font-family="monospace" font-weight="bold" text-anchor="start">{{ estimatedA3.toFixed(3) }}</text>
              </svg>
            </div>

            <div class="p-3 bg-amber-50 border border-amber-100 rounded-xl flex items-center justify-between gap-3 shadow-sm">
              <div class="flex-1">
                <label class="field-label text-[9px] mb-0.5 text-amber-800">Módulo M<sub>R</sub> (psi)</label>
                <input v-model.number="calcMrSubBase" type="number" step="1000" class="field-input font-mono w-full text-xs py-1.5 px-2 border-amber-200/60 shadow-inner" placeholder="Ej: 15000" />
              </div>

              <div class="flex-1">
                <label class="field-label text-[9px] mb-0.5 text-amber-800">CBR (%)</label>
                <input v-model.number="calcCbrSubBase" type="number" step="1" class="field-input font-mono w-full text-xs py-1.5 px-2 border-amber-200/60 shadow-inner" placeholder="Ej: 50" />
              </div>

              <div class="flex flex-col items-center justify-center bg-white px-3 py-1.5 rounded-lg border border-amber-100 shadow-sm">
                <span class="text-[8px] font-bold text-amber-600 uppercase tracking-wider block mb-0.5">a₃ Estimado</span>
                <span class="text-base font-bold text-amber-600 font-mono leading-none">{{ estimatedA3.toFixed(3) }}</span>
              </div>
              
              <button 
                @click="applyEstimatedA3"
                class="px-4 py-2 h-full bg-amber-600 text-white rounded-lg font-bold hover:bg-amber-700 transition-colors shadow-sm active:scale-95 text-[10px] flex items-center justify-center whitespace-nowrap self-stretch"
              >
                Aplicar
              </button>
            </div>

          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal de Guía Subrasante (Mr) -->
    <Transition name="modal-fade">
      <div v-if="isMrHelpModalOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div @click.stop class="bg-white rounded-2xl border border-slate-100 shadow-2xl w-full max-w-md overflow-hidden flex flex-col">
          <div class="px-6 py-4 bg-emerald-50/50 border-b border-emerald-100/50 flex items-center justify-between">
            <h3 class="text-xs font-bold text-emerald-900 uppercase tracking-wider">
              Estimación de Módulo Resiliente (Subrasante)
            </h3>
            <button 
              @click="isMrHelpModalOpen = false" 
              class="w-6 h-6 flex items-center justify-center text-emerald-600/50 hover:text-emerald-700 hover:bg-emerald-100 rounded-full font-bold text-sm cursor-pointer transition-colors"
            >
              ✕
            </button>
          </div>
          
          <div class="p-6 space-y-4 text-xs text-slate-600 leading-relaxed overflow-y-auto max-h-[70vh]">
            <p>
              El <strong>Módulo Resiliente (M<sub>R</sub>)</strong> de la subrasante puede estimarse a partir del CBR mediante dos ecuaciones empíricas documentadas en manuales AASHTO.
            </p>

            <div class="space-y-3">
              <div>
                <label class="field-label text-[10px] mb-1 text-emerald-800">CBR de la Subrasante (%)</label>
                <input v-model.number="calcCbrMr" type="number" step="0.5" class="field-input font-mono w-full text-sm py-2 px-3 border-emerald-200/60 shadow-inner bg-emerald-50/30 text-emerald-900 font-bold" placeholder="Ej: 5" />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3 mt-4">
              <!-- Opción 1: Clásica -->
              <div class="border rounded-xl p-3 flex flex-col justify-between" :class="calcCbrMr <= 10 && calcCbrMr > 0 ? 'border-emerald-400 bg-emerald-50/50 shadow-sm relative' : 'border-slate-200 bg-slate-50 opacity-70'">
                <div v-if="calcCbrMr <= 10 && calcCbrMr > 0" class="absolute -top-2 -right-2 bg-emerald-500 text-white text-[8px] font-bold px-1.5 py-0.5 rounded-md uppercase shadow-sm">Recomendada</div>
                <div>
                  <h4 class="font-bold text-[10px] text-slate-800 mb-1">Ecuación Clásica</h4>
                  <p class="text-[9px] text-slate-500 mb-2 leading-tight">Ideal para suelos finos (CBR ≤ 10).</p>
                  <div class="p-1.5 bg-white rounded border border-slate-100 text-[9px] text-center font-mono text-slate-600 mb-2">
                    M<sub>R</sub> = 1,500 · CBR
                  </div>
                </div>
                <div class="flex items-end justify-between mt-2">
                  <div>
                    <span class="text-[8px] font-bold text-slate-400 uppercase block leading-none mb-1">Resultado</span>
                    <span class="font-mono font-bold text-sm leading-none block" :class="calcCbrMr <= 10 && calcCbrMr > 0 ? 'text-emerald-700' : 'text-slate-600'">{{ calcCbrMr ? Math.round(calcCbrMr * 1500).toLocaleString('en-US') : 0 }} <span class="text-[9px] font-normal">psi</span></span>
                  </div>
                  <button @click="applyMr(Math.round(calcCbrMr * 1500))" :disabled="!calcCbrMr" class="px-2 py-1 text-[9px] font-bold rounded cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed" :class="calcCbrMr <= 10 && calcCbrMr > 0 ? 'bg-emerald-600 text-white hover:bg-emerald-700' : 'bg-slate-200 text-slate-600 hover:bg-slate-300'">Aplicar</button>
                </div>
              </div>

              <!-- Opción 2: TRL -->
              <div class="border rounded-xl p-3 flex flex-col justify-between" :class="calcCbrMr > 10 ? 'border-emerald-400 bg-emerald-50/50 shadow-sm relative' : 'border-slate-200 bg-slate-50 opacity-70'">
                <div v-if="calcCbrMr > 10" class="absolute -top-2 -right-2 bg-emerald-500 text-white text-[8px] font-bold px-1.5 py-0.5 rounded-md uppercase shadow-sm">Recomendada</div>
                <div>
                  <h4 class="font-bold text-[10px] text-slate-800 mb-1">Modelo No Lineal</h4>
                  <p class="text-[9px] text-slate-500 mb-2 leading-tight">Ideal para granulares (CBR > 10).</p>
                  <div class="p-1.5 bg-white rounded border border-slate-100 text-[9px] text-center font-mono text-slate-600 mb-2">
                    M<sub>R</sub> = 2,555 · CBR<sup>0.64</sup>
                  </div>
                </div>
                <div class="flex items-end justify-between mt-2">
                  <div>
                    <span class="text-[8px] font-bold text-slate-400 uppercase block leading-none mb-1">Resultado</span>
                    <span class="font-mono font-bold text-sm leading-none block" :class="calcCbrMr > 10 ? 'text-emerald-700' : 'text-slate-600'">{{ calcCbrMr ? Math.round(2555 * Math.pow(calcCbrMr, 0.64)).toLocaleString('en-US') : 0 }} <span class="text-[9px] font-normal">psi</span></span>
                  </div>
                  <button @click="applyMr(Math.round(2555 * Math.pow(calcCbrMr, 0.64)))" :disabled="!calcCbrMr" class="px-2 py-1 text-[9px] font-bold rounded cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed" :class="calcCbrMr > 10 ? 'bg-emerald-600 text-white hover:bg-emerald-700' : 'bg-slate-200 text-slate-600 hover:bg-slate-300'">Aplicar</button>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal de Guía Drenaje (m2, m3) -->
    <Transition name="modal-fade">
      <div v-if="isDrainageHelpModalOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div @click.stop class="bg-white rounded-2xl border border-slate-100 shadow-2xl w-full max-w-md overflow-hidden flex flex-col">
          <div class="px-6 py-4 bg-blue-50/50 border-b border-blue-100/50 flex items-center justify-between">
            <h3 class="text-xs font-bold text-blue-900 uppercase tracking-wider">
              Estimación de Drenaje ({{ currentDrainageParam === 'm2' ? 'm₂ - Base' : 'm₃ - Sub-base' }})
            </h3>
            <button 
              @click="isDrainageHelpModalOpen = false" 
              class="w-6 h-6 flex items-center justify-center text-blue-600/50 hover:text-blue-700 hover:bg-blue-100 rounded-full font-bold text-sm cursor-pointer transition-colors"
            >
              ✕
            </button>
          </div>
          
          <div class="p-6 space-y-4 text-xs text-slate-600 leading-relaxed overflow-y-auto max-h-[70vh]">
            <p>
              El coeficiente de drenaje (<strong>{{ currentDrainageParam === 'm2' ? 'm₂' : 'm₃' }}</strong>) modifica el aporte estructural de las capas granulares según la eficiencia con la que el agua drena del pavimento.
            </p>
            <p class="text-[10px] text-slate-500 italic">Basado en las Tablas IV.6 y IV.7 de la Guía AASHTO 1993.</p>

            <div class="space-y-4 p-3 bg-blue-50/50 rounded-xl border border-blue-100 shadow-sm">
              <!-- Calidad -->
              <div>
                <label class="text-[9px] font-bold text-blue-800 uppercase block mb-2">Calidad del Drenaje</label>
                <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  <label v-for="(desc, q) in {'Excelente': '2 horas', 'Bueno': '1 día', 'Regular': '1 semana', 'Malo': '1 mes', 'Muy malo': 'No drena'}" :key="q" class="flex items-center gap-2 p-1.5 border rounded-lg cursor-pointer transition-colors" :class="calcDrainageQuality === q ? 'bg-blue-50 border-blue-300 shadow-sm' : 'bg-white border-slate-200 hover:bg-slate-50'">
                    <input type="radio" v-model="calcDrainageQuality" :value="q" class="text-blue-600 focus:ring-blue-500 w-3 h-3" />
                    <div class="flex flex-col">
                      <span class="font-bold text-slate-700 text-[10px] leading-tight">{{ q }}</span>
                      <span class="text-[8px] text-slate-500 leading-none mt-0.5">{{ desc }}</span>
                    </div>
                  </label>
                </div>
              </div>

              <!-- Días de lluvia -->
              <div>
                <label class="text-[9px] font-bold text-blue-800 uppercase block mb-1">Días Lluviosos / Año</label>
                <div class="relative w-full sm:w-1/2">
                  <input type="number" v-model.number="drainageRainyDays" min="0" max="365" class="w-full font-mono text-xs px-2 py-1.5 border border-blue-200 rounded text-blue-900 font-bold bg-white focus:ring-1 focus:ring-blue-500 pr-16 shadow-inner" placeholder="Ej: 30" />
                  <span class="absolute right-2 top-1.5 text-xs text-blue-400 font-mono pointer-events-none">días</span>
                </div>
              </div>
            </div>

            <div class="space-y-4">
              <div class="overflow-hidden rounded-xl border border-blue-100 shadow-sm">
                <table class="w-full text-center border-collapse">
                  <thead>
                    <tr class="bg-blue-50/80 border-b border-blue-100">
                      <th rowspan="2" class="p-2 text-[9px] text-blue-900 border-r border-blue-100 font-bold align-middle w-[28%] leading-tight">Calidad de<br/>Drenaje</th>
                      <th colspan="4" class="p-1.5 text-[9px] text-blue-800 border-b border-blue-100 font-bold">% Tiempo próximo a saturación</th>
                    </tr>
                    <tr class="bg-blue-50/40">
                      <th v-for="exp in ['<1%', '1-5%', '5-25%', '>25%']" :key="exp" class="p-1 text-[8px] font-semibold text-blue-700 border-r border-blue-100 last:border-0">{{ exp }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, q) in drainageMatrix" :key="q" class="border-b border-blue-50 last:border-0">
                      <td class="p-1.5 text-[9px] font-bold text-slate-600 bg-slate-50 border-r border-blue-50 leading-tight">
                        {{ q }}
                        <span class="block text-[7px] text-slate-400 font-normal mt-0.5">{{ {'Excelente':'2 horas','Bueno':'1 día','Regular':'1 semana','Malo':'1 mes','Muy malo':'No drena'}[q] }}</span>
                      </td>
                      <td v-for="(range, exp) in row" :key="exp" 
                          @click="handleDrainageCellClick(q, exp)"
                          class="p-1 text-[9px] font-mono cursor-pointer transition-colors border-r border-blue-50 last:border-0 select-none"
                          :class="(calcDrainageQuality === q && calcDrainageExposure === exp) ? 'bg-blue-600 text-white shadow-inner font-bold scale-[1.02]' : 'bg-white text-slate-600 hover:bg-blue-50'"
                      >
                        {{ range[0] === range[1] ? range[0].toFixed(2) : Math.max(range[0], range[1]).toFixed(2) + ' - ' + Math.min(range[0], range[1]).toFixed(2) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Compact Rango y Slider -->
              <div class="p-2 bg-slate-50 border border-slate-200 rounded-xl flex items-center gap-3 shadow-sm">
                <div class="flex-1 flex flex-col justify-center">
                  <div class="flex justify-between text-[8px] text-slate-400 font-mono mb-1 px-1">
                    <span>{{ Math.min(drainageRange[0], drainageRange[1]).toFixed(2) }}</span>
                    <span>{{ Math.max(drainageRange[0], drainageRange[1]).toFixed(2) }}</span>
                  </div>
                  <input type="range" v-model.number="estimatedDrainageValue" :min="Math.min(drainageRange[0], drainageRange[1])" :max="Math.max(drainageRange[0], drainageRange[1])" step="0.01" class="w-full accent-blue-600 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer" />
                </div>
                
                <div class="flex items-center gap-2 border-l border-slate-200 pl-3">
                  <div class="flex flex-col">
                    <span class="text-[8px] font-bold text-slate-400 uppercase leading-none mb-1">Ajuste</span>
                    <input type="number" step="0.01" v-model.number="estimatedDrainageValue" class="font-mono w-14 text-xs py-1 px-1.5 border border-slate-200/60 rounded text-blue-900 font-bold bg-white text-center shadow-inner" />
                  </div>
                  <button @click="applyDrainage" class="px-3 py-1.5 h-full bg-blue-600 text-white rounded font-bold hover:bg-blue-700 transition-colors shadow-sm text-[10px]">
                    Aplicar
                  </button>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import katex from 'katex'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import html2canvas from 'html2canvas'
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import TopBar  from '@/components/layout/TopBar.vue'
import DesignView       from '@/views/DesignView.vue'
import OptimizationView from '@/views/OptimizationView.vue'
import ReportView       from '@/views/ReportView.vue'

import { useAASHTODesign } from '@/composables/useAASHTODesign.js'

const { state: s, results, setReliability, RELIABILITY_OPTIONS } = useAASHTODesign()

// Validar límites y relación de serviciabilidad al cambiar los inputs
const validateServiciabilidad = () => {
  if (typeof s.pi !== 'number' || isNaN(s.pi)) s.pi = 4.2
  s.pi = Math.max(3.5, Math.min(5.0, parseFloat(s.pi.toFixed(2))))
  
  if (typeof s.pt !== 'number' || isNaN(s.pt)) s.pt = 2.5
  s.pt = Math.max(1.5, Math.min(3.5, parseFloat(s.pt.toFixed(2))))
  
  if (s.pt >= s.pi) {
    s.pt = parseFloat((s.pi - 0.1).toFixed(2))
  }
}

const formatVal = (val) => (typeof val === 'number' && !isNaN(val)) ? val.toFixed(2) : ''

const isServHelpModalOpen = ref(false)
const applyServPresets = (pi, pt) => {
  s.pi = pi
  s.pt = pt
  isServHelpModalOpen.value = false
}

// --- Calculadora de a1 (Carpeta Asfáltica) ---
const isA1HelpModalOpen = ref(false)
const calcEac = ref(400000)
const svgGraphA1 = ref(null)
const isDraggingGraph = ref(false)

const estimatedA1 = computed(() => {
  if (!calcEac.value || calcEac.value <= 0) return 0
  const a1 = 0.171 * Math.log(calcEac.value) - 1.784
  return Math.max(0, Math.min(0.5, a1))
})

const a1CurvePoints = computed(() => {
  let pts = []
  for(let x = 100000; x <= 500000; x += 10000) {
    const y = 0.171 * Math.log(x) - 1.784
    const clampedY = Math.max(0, Math.min(0.5, y))
    const sx = ((x - 100000) / 400000) * 300
    const sy = 150 - (clampedY / 0.5) * 150
    pts.push(`${sx},${sy}`)
  }
  return pts.join(' ')
})

const userPointA1 = computed(() => {
  const x = Math.max(100000, Math.min(500000, calcEac.value))
  const y = estimatedA1.value
  const sx = ((x - 100000) / 400000) * 300
  const sy = 150 - (y / 0.5) * 150
  return { sx, sy }
})

const handleGraphMove = (e) => {
  if (!svgGraphA1.value) return
  const rect = svgGraphA1.value.getBoundingClientRect()
  let clientX = e.clientX
  if (e.touches && e.touches.length > 0) {
    clientX = e.touches[0].clientX
  }
  if (clientX === undefined) return
  
  let x = clientX - rect.left
  x = Math.max(0, Math.min(rect.width, x))
  
  const eac = 100000 + (x / rect.width) * 400000
  calcEac.value = Math.round(eac / 1000) * 1000
}

const applyEstimatedA1 = () => {
  s.a1 = parseFloat(estimatedA1.value.toFixed(3))
  isA1HelpModalOpen.value = false
}

// --- Calculadora de a2 (Base Granular) ---
const isA2HelpModalOpen = ref(false)
const calcMrBase = ref(30000)
const svgGraphA2 = ref(null)
const isDraggingGraphA2 = ref(false)

watch(isA2HelpModalOpen, (val) => {
  if (val && s.Mr1) {
    calcMrBase.value = Math.max(10000, Math.min(45000, s.Mr1))
  }
})

const estimatedA2 = computed(() => {
  if (!calcMrBase.value || calcMrBase.value <= 0) return 0
  const a2 = 0.249 * Math.log10(calcMrBase.value) - 0.977
  return Math.max(0, Math.min(0.25, a2))
})

const calcCbrBase = computed({
  get: () => {
    const a2 = estimatedA2.value
    if (a2 <= 0) return 0
    const cbr = Math.pow(10, (a2 + 0.046) / 0.093)
    return Math.round(cbr)
  },
  set: (val) => {
    if (!val || val <= 0) return
    const a2 = 0.093 * Math.log10(val) - 0.046
    const mr = Math.pow(10, (a2 + 0.977) / 0.249)
    calcMrBase.value = Math.round(mr / 100) * 100
  }
})

const nomographY = computed(() => {
  const a2 = estimatedA2.value
  const clampedA2 = Math.max(0.05, Math.min(0.20, a2))
  return 20 + ((0.20 - clampedA2) / 0.15) * 110
})

const handleGraphMoveA2 = (e) => {
  if (!svgGraphA2.value) return
  const rect = svgGraphA2.value.getBoundingClientRect()
  let clientY = e.clientY
  if (e.touches && e.touches.length > 0) {
    clientY = e.touches[0].clientY
  }
  if (clientY === undefined) return
  
  let y = clientY - rect.top
  y = Math.max(20, Math.min(130, y))
  
  // y = 20 -> a2 = 0.20
  // y = 130 -> a2 = 0.05
  let a2 = 0.20 - ((y - 20) / 110) * 0.15
  let mr = Math.pow(10, (a2 + 0.977) / 0.249)
  
  calcMrBase.value = Math.round(mr / 100) * 100
}

const applyEstimatedA2 = () => {
  s.Mr1 = calcMrBase.value
  s.a2 = parseFloat(estimatedA2.value.toFixed(3))
  isA2HelpModalOpen.value = false
}

// --- Calculadora de a3 (Sub-base Granular) ---
const isA3HelpModalOpen = ref(false)
const calcMrSubBase = ref(15000)
const svgGraphA3 = ref(null)
const isDraggingGraphA3 = ref(false)

watch(isA3HelpModalOpen, (val) => {
  if (val && s.Mr2) {
    calcMrSubBase.value = Math.max(8000, Math.min(25000, s.Mr2))
  }
})

const estimatedA3 = computed(() => {
  if (!calcMrSubBase.value || calcMrSubBase.value <= 0) return 0
  const a3 = 0.227 * Math.log10(calcMrSubBase.value) - 0.839
  return Math.max(0, Math.min(0.25, a3))
})

const calcCbrSubBase = computed({
  get: () => {
    const a3 = estimatedA3.value
    if (a3 <= 0) return 0
    // a3 = 0.0615 * log10(CBR) + 0.017
    const cbr = Math.pow(10, (a3 - 0.017) / 0.0615)
    return Math.round(cbr)
  },
  set: (val) => {
    if (!val || val <= 0) return
    const a3 = 0.0615 * Math.log10(val) + 0.017
    const mr = Math.pow(10, (a3 + 0.839) / 0.227)
    calcMrSubBase.value = Math.round(mr / 100) * 100
  }
})

const nomographYA3 = computed(() => {
  const a3 = estimatedA3.value
  const clampedA3 = Math.max(0.04, Math.min(0.16, a3))
  // a3 = 0.15 -> y=20, a3=0.05 -> y=130
  return 20 + ((0.15 - clampedA3) / 0.10) * 110
})

const handleGraphMoveA3 = (e) => {
  if (!svgGraphA3.value) return
  const rect = svgGraphA3.value.getBoundingClientRect()
  let clientY = e.clientY
  if (e.touches && e.touches.length > 0) {
    clientY = e.touches[0].clientY
  }
  if (clientY === undefined) return
  
  let y = clientY - rect.top
  y = Math.max(20, Math.min(140, y))
  
  let a3 = 0.15 - ((y - 20) / 110) * 0.10
  let mr = Math.pow(10, (a3 + 0.839) / 0.227)
  
  calcMrSubBase.value = Math.round(mr / 100) * 100
}

const applyEstimatedA3 = () => {
  s.Mr2 = calcMrSubBase.value
  s.a3 = parseFloat(estimatedA3.value.toFixed(3))
  isA3HelpModalOpen.value = false
}

// --- Calculadora de Subrasante (Mr) ---
const isMrHelpModalOpen = ref(false)
const calcCbrMr = ref(5)

const applyMr = (value) => {
  if (value && value > 0) {
    s.Mr3 = value
    isMrHelpModalOpen.value = false
  }
}

// --- Calculadora de Drenaje (m2, m3) ---
const isDrainageHelpModalOpen = ref(false)
const currentDrainageParam = ref('m2') // 'm2' o 'm3'
const calcDrainageQuality = ref('Bueno')
const calcDrainageExposure = ref('5-25%')

const drainageExposureVal = ref(10)

const drainageRainyDays = computed({
  get: () => Math.round((drainageExposureVal.value / 100) * 365),
  set: (val) => {
    if (val >= 0 && val <= 365) {
      drainageExposureVal.value = (val / 365) * 100
    }
  }
})

watch(drainageExposureVal, (val) => {
  if (val < 1) calcDrainageExposure.value = '<1%'
  else if (val <= 5) calcDrainageExposure.value = '1-5%'
  else if (val <= 25) calcDrainageExposure.value = '5-25%'
  else calcDrainageExposure.value = '>25%'
}, { immediate: true })

const handleDrainageCellClick = (q, exp) => {
  calcDrainageQuality.value = q
  if (calcDrainageExposure.value !== exp) {
    if (exp === '<1%') drainageExposureVal.value = 0.5
    if (exp === '1-5%') drainageExposureVal.value = 3
    if (exp === '5-25%') drainageExposureVal.value = 15
    if (exp === '>25%') drainageExposureVal.value = 30
  }
}

const drainageMatrix = {
  'Excelente': { '<1%': [1.40, 1.35], '1-5%': [1.35, 1.30], '5-25%': [1.30, 1.20], '>25%': [1.20, 1.20] },
  'Bueno':     { '<1%': [1.35, 1.25], '1-5%': [1.25, 1.15], '5-25%': [1.15, 1.00], '>25%': [1.00, 1.00] },
  'Regular':   { '<1%': [1.25, 1.15], '1-5%': [1.15, 1.05], '5-25%': [1.00, 0.80], '>25%': [0.80, 0.80] },
  'Malo':      { '<1%': [1.15, 1.05], '1-5%': [1.05, 0.80], '5-25%': [0.80, 0.60], '>25%': [0.60, 0.60] },
  'Muy malo':  { '<1%': [1.05, 0.95], '1-5%': [0.95, 0.75], '5-25%': [0.75, 0.40], '>25%': [0.40, 0.40] }
}

const drainageRange = computed(() => {
  return drainageMatrix[calcDrainageQuality.value][calcDrainageExposure.value]
})

const estimatedDrainageValue = ref(1.00)

watch([calcDrainageQuality, calcDrainageExposure], () => {
  const range = drainageMatrix[calcDrainageQuality.value][calcDrainageExposure.value]
  estimatedDrainageValue.value = parseFloat(((range[0] + range[1]) / 2).toFixed(2))
})

const openDrainageModal = (param) => {
  currentDrainageParam.value = param
  isDrainageHelpModalOpen.value = true
  
  // Set quality manually or let it be default
  const range = drainageMatrix[calcDrainageQuality.value][calcDrainageExposure.value]
  estimatedDrainageValue.value = parseFloat(((range[0] + range[1]) / 2).toFixed(2))
}

const applyDrainage = () => {
  if (currentDrainageParam.value === 'm2') s.m2 = estimatedDrainageValue.value
  if (currentDrainageParam.value === 'm3') s.m3 = estimatedDrainageValue.value
  isDrainageHelpModalOpen.value = false
}

// --- Calculadora de Tránsito (W18) ---
const isTrafficHelpModalOpen = ref(false)
const calcTraffic = ref({ tpds: 775, k1: 39, k2: 45, r: 2.5, n: 10, fc: 1.78 })

// K1 Estimator
const showK1Estimator = ref(false)
const calcK1 = ref({ buses: 9, c2: 18, c3: 5, articulados: 7 })
const estimatedK1Sum = computed(() => {
  return (calcK1.value.buses || 0) + (calcK1.value.c2 || 0) + (calcK1.value.c3 || 0) + (calcK1.value.articulados || 0)
})
const applyEstimatedK1 = () => {
  calcTraffic.value.k1 = estimatedK1Sum.value
  showK1Estimator.value = false
}

// KaTeX Formulas
const formulaGeneralHtml = katex.renderToString(
  String.raw`N = \text{TPDS} \times \left(\frac{k_1}{100}\right) \times \left(\frac{k_2}{100}\right) \times 365 \times \left[ \frac{(1+r)^n - 1}{\ln(1+r)} \right] \times FC`,
  { throwOnError: false, displayMode: true }
)

const formulaPasoHtml = computed(() => {
  const t = calcTraffic.value
  const r_dec = t.r / 100
  const eq = String.raw`N = ${t.tpds} \times \left(\frac{${t.k1}}{100}\right) \times \left(\frac{${t.k2}}{100}\right) \times 365 \times \left[ \frac{(1+${r_dec})^{${t.n}} - 1}{\ln(1+${r_dec})} \right] \times ${t.fc}`
  return katex.renderToString(eq, { throwOnError: false, displayMode: true })
})

const calculatedW18 = computed(() => {
  const t = calcTraffic.value
  const r_decimal = t.r / 100
  const fc_growth = r_decimal === 0 ? t.n : (Math.pow(1 + r_decimal, t.n) - 1) / Math.log(1 + r_decimal)
  return t.tpds * (t.k1 / 100) * (t.k2 / 100) * 365 * fc_growth * t.fc
})

const applyCalculatedTraffic = () => {
  if (!isNaN(calculatedW18.value)) {
    s.W18 = Math.round(calculatedW18.value)
  }
  isTrafficHelpModalOpen.value = false
}

const exportTrafficPDF = async () => {
  const doc = new jsPDF()
  const t = calcTraffic.value
  const r_dec = t.r / 100
  const fc_growth = r_dec === 0 ? t.n : (Math.pow(1 + r_dec, t.n) - 1) / Math.log(1 + r_dec)
  const W18 = Math.round(t.tpds * (t.k1 / 100) * (t.k2 / 100) * 365 * fc_growth * t.fc)
  
  doc.setFontSize(16)
  doc.text('Memoria de Calculo - Ejes Equivalentes (W18)', 14, 20)
  
  doc.setFontSize(11)
  doc.text('Metodologia: Guia AASHTO 93 (con crecimiento exponencial continuo)', 14, 28)
  
  autoTable(doc, {
    startY: 35,
    head: [['Parametro', 'Descripcion', 'Valor']],
    body: [
      ['TPDS', 'Transito Promedio Diario Semanal', `${t.tpds} veh/dia`],
      ['FC', 'Factor Camion (Dano Equivalente)', t.fc.toFixed(2)],
      ['k1', 'Porcentaje de Vehiculos Pesados', `${t.k1} %`],
      ['k2', 'Factor Direccional y de Carril', `${t.k2} %`],
      ['r', 'Tasa de Crecimiento Anual', `${t.r} %`],
      ['n', 'Periodo de Diseno', `${t.n} anos`]
    ],
    theme: 'grid',
    headStyles: { fillColor: [79, 70, 229] }
  })
  
  let finalY = doc.lastAutoTable.finalY || 35
  
  doc.setFontSize(12)
  doc.text('Desarrollo del Calculo Paso a Paso:', 14, finalY + 10)
  finalY += 15
  
  // Agregar imagen de las ecuaciones de KaTeX
  const eqContainer = document.getElementById('pdf-equations-container')
  if (eqContainer) {
    try {
      const canvas = await html2canvas(eqContainer, { scale: 2, backgroundColor: '#f8fafc' })
      const imgData = canvas.toDataURL('image/png')
      
      const pdfWidth = 182 // Ancho casi total de la página A4 (210 - 28)
      const imgWidth = pdfWidth
      const imgHeight = (canvas.height * imgWidth) / canvas.width
      
      doc.addImage(imgData, 'PNG', 14, finalY, imgWidth, imgHeight)
      finalY += imgHeight + 15
    } catch(e) {
      console.error('Error capturando ecuaciones para PDF', e)
    }
  }
  
  // Detalle textual
  doc.setFontSize(10)
  doc.setTextColor(100, 100, 100)
  const vehPesadosCarril = t.tpds * (t.k1/100) * (t.k2/100)
  doc.text(`1. Vehiculos pesados en el carril = TPDS x (k1/100) x (k2/100) = ${vehPesadosCarril.toFixed(2)} veh/dia`, 14, finalY)
  
  doc.text(`2. Volumen anual de pesados en el carril = ${vehPesadosCarril.toFixed(2)} x 365 = ${(vehPesadosCarril * 365).toFixed(2)} veh/ano`, 14, finalY + 8)
  
  doc.text(`3. Factor de Crecimiento Acumulado = ((1+r)^n - 1) / ln(1+r) = ${fc_growth.toFixed(4)}`, 14, finalY + 16)
  
  const totalPesados = vehPesadosCarril * 365 * fc_growth
  doc.text(`4. Total de vehiculos pesados = Volumen Anual x Factor Crecimiento = ${totalPesados.toFixed(2)}`, 14, finalY + 24)
  
  doc.text(`5. Ejes Equivalentes = Total vehiculos x FC = ${totalPesados.toFixed(2)} x ${t.fc} = ${W18.toLocaleString('en-US')}`, 14, finalY + 32)
  
  doc.setFontSize(14)
  doc.setTextColor(79, 70, 229)
  doc.text(`Resultado Final (N) = ${W18.toLocaleString('en-US')} ejes equivalentes`, 14, finalY + 45)
  
  doc.save('Memoria_Calculo_W18.pdf')
}

const calcHelpKey = ref(null)
const calcHelpTitles = {
  tpds: 'TPDS Inicial',
  fc: 'Factor Camión (FC)',
  k1: 'Vehículos Pesados (k₁)',
  k2: 'Factor Direccional/Carril (k₂)',
  r: 'Tasa de Crecimiento (r)',
  n: 'Período de Diseño (n)'
}

// --- Campana de Gauss para Confiabilidad R% (Interactiva y Taller) ---
const getX = (z) => 170 + z * 45 // z=-3 -> 35, z=3 -> 305
const getY = (z) => 280 - 200 * Math.exp(-z * z / 2) // Peak at y=80, base at y=280 (Escala vertical duplicada)

const outlinePath = computed(() => {
  let points = []
  for (let z = -3.0; z <= 3.0; z += 0.1) {
    points.push(`${getX(z).toFixed(1)},${getY(z).toFixed(1)}`)
  }
  return `M ${points.join(' L ')}`
})

const shadedPath = computed(() => {
  const Zr = Math.max(-3.0, Math.min(3.0, s.Zr || 0)) // Limitar en el rango visible del gráfico
  const zLimit = -Zr
  let points = []
  
  // Punto inicial en el eje Z (-3.0)
  points.push(`${getX(-3.0).toFixed(1)},280`)
  
  // Seguir la curva desde -3.0 hasta zLimit
  for (let z = -3.0; z <= zLimit; z += 0.05) {
    points.push(`${getX(z).toFixed(1)},${getY(z).toFixed(1)}`)
  }
  points.push(`${getX(zLimit).toFixed(1)},${getY(zLimit).toFixed(1)}`)
  
  // Bajar al eje Z en zLimit
  points.push(`${getX(zLimit).toFixed(1)},280`)
  
  return `M ${points.join(' L ')} Z`
})

// --- Interacción con el Gráfico de Gauss ---
const isDragging = ref(false)
const svgRef = ref(null)

const startDrag = (e) => {
  isDragging.value = true
  handleInteraction(e)
}

const onDrag = (e) => {
  if (!isDragging.value) return
  handleInteraction(e)
}

const endDrag = () => {
  isDragging.value = false
}

const handleInteraction = (e) => {
  if (!svgRef.value) return
  
  const rect = svgRef.value.getBoundingClientRect()
  const clientX = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left
  const svgX = (clientX / rect.width) * 340 // viewBox width is 340
  
  // Mapeo inverso de x = 170 + z * 45 => z = (x - 170) / 45
  const z = (svgX - 170) / 45
  
  // Se rellena de izquierda a derecha, por lo que el límite del sombreado zLimit = -Zr.
  // Es decir, Zr = -z
  const targetZr = -z
  
  // Mapear al valor de confiabilidad más cercano en las opciones de la AASHTO
  const ZR_TABLE = {
    50: 0, 60: -0.253, 70: -0.524, 75: -0.674,
    80: -0.841, 85: -1.037, 90: -1.282, 91: -1.340,
    92: -1.405, 93: -1.476, 94: -1.555, 95: -1.645,
    96: -1.751, 97: -1.881, 98: -2.054, 99: -2.327
  }
  const RELIABILITY_OPTIONS = [50, 60, 70, 75, 80, 85, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
  
  let closestR = 90
  let minDiff = Infinity
  for (const r of RELIABILITY_OPTIONS) {
    const rZr = ZR_TABLE[r]
    const diff = Math.abs(rZr - targetZr)
    if (diff < minDiff) {
      minDiff = diff
      closestR = r
    }
  }
  
  setReliability(closestR)
}

// --- Selector de Confiabilidad Premium (Dropdown) ---
const isDropdownOpen = ref(false)
const selectReliabilityOption = (r) => {
  setReliability(r)
  isDropdownOpen.value = false
}

// --- Guía de Valores So y Modal ---
const isHelpModalOpen = ref(false)
const applySoValue = (val) => {
  s.So = val
  isHelpModalOpen.value = false
}

const isReliabilityHelpModalOpen = ref(false)

// --- Curva de Pérdida de Serviciabilidad (AASHTO 93) ---
const getXt = (t) => 40 + t * 13 // t=0 -> 40, t=20 -> 300
const getYp = (p) => 280 - p * 40 // p=6 -> 40, p=5 -> 80, p=0 -> 280 (Escala vertical hasta 6.0)

// Calculamos el SN aportado por las capas reales actuales
const actualSN = computed(() => {
  const layers = results.value?.capas || []
  if (!layers.length) return 4.0 // fallback
  
  // Carpeta CA
  const CA_cm = layers[0]?.cm || 0
  const D1 = CA_cm / 2.54
  let sn = D1 * s.a1
  
  if (s.numCapas >= 2 && layers[1]) {
    const BG_cm = layers[1].cm
    const D2 = BG_cm / 2.54
    sn += D2 * s.a2 * s.m2
  }
  if (s.numCapas === 3 && layers[2]) {
    const SBG_cm = layers[2].cm
    const D3 = SBG_cm / 2.54
    sn += D3 * s.a3 * s.m3
  }
  return Math.max(1.0, sn)
})

const servCurvePath = computed(() => {
  const pi = s.pi || 4.2
  const pt = s.pt || 2.5
  
  let points = []
  // Usamos un exponente de 2.5 para dar la forma cóncava típica (como en el diagrama de referencia)
  for (let t = 0; t <= 20; t += 0.5) {
    const pVal = pi - (pi - pt) * Math.pow(t / 20, 2.5)
    points.push(`${getXt(t).toFixed(1)},${getYp(pVal).toFixed(1)}`)
  }
  return `M ${points.join(' L ')}`
})

const servFillPath = computed(() => {
  const pi = s.pi || 4.2
  const pt = s.pt || 2.5
  
  let points = []
  // Comenzar en t=0 (x=40) sobre el eje X (y=280)
  points.push(`40.0,280.0`)
  
  // Trazar curva de deterioro
  for (let t = 0; t <= 20; t += 0.5) {
    const pVal = pi - (pi - pt) * Math.pow(t / 20, 2.5)
    points.push(`${getXt(t).toFixed(1)},${getYp(pVal).toFixed(1)}`)
  }
  
  // Terminar en t=20 (x=300) sobre el eje X (y=280)
  points.push(`300.0,280.0`)
  
  return `M ${points.join(' L ')} Z`
})

// --- Interacción con el Gráfico de Serviciabilidad ---
const isDraggingServ = ref(false)
const activeHandleServ = ref(null) // 'pi' o 'pt'
const hoveredLine = ref(null) // 'pi' o 'pt' o null (Para iluminar al pasar cursor)
const servSvgRef = ref(null)

const startDragServ = (e, target) => {
  activeHandleServ.value = target // 'pi' o 'pt'
  isDraggingServ.value = true
  handleInteractionServ(e)
}

const onDragServ = (e) => {
  if (!isDraggingServ.value) return
  handleInteractionServ(e)
}

const endDragServ = () => {
  isDraggingServ.value = false
  activeHandleServ.value = null
}

const handleInteractionServ = (e) => {
  if (!servSvgRef.value || !activeHandleServ.value) return
  
  const rect = servSvgRef.value.getBoundingClientRect()
  const clientY = (e.touches ? e.touches[0].clientY : e.clientY) - rect.top
  const svgY = (clientY / rect.height) * 320 // viewBox height is 320
  
  let p = (280 - svgY) / 40
  
  if (activeHandleServ.value === 'pi') {
    p = Math.max(3.5, Math.min(5.0, parseFloat(p.toFixed(2))))
    if (p > s.pt) {
      s.pi = p
    }
  } else {
    p = Math.max(1.5, Math.min(3.5, parseFloat(p.toFixed(2))))
    if (p < s.pi) {
      s.pt = p
    }
  }
}

const view = ref('design')
const activeParam = ref(null)

// Cerrar panel flotante con ESC
const handleKeyDown = (e) => {
  if (e.key === 'Escape') {
    activeParam.value = null
  }
}

// Cerrar al hacer click por fuera
const handleClickOutside = (e) => {
  // Cerrar el dropdown si se hace clic fuera del contenedor dropdown
  const dropdownContainer = document.querySelector('.relative-dropdown-container')
  if (dropdownContainer && !dropdownContainer.contains(e.target)) {
    isDropdownOpen.value = false
  }

  if (!activeParam.value) return
  
  // No cerrar el panel si hay algún modal de guía abierto
  if (isHelpModalOpen.value || isReliabilityHelpModalOpen.value || isServHelpModalOpen.value || isTrafficHelpModalOpen.value || calcHelpKey.value || isA1HelpModalOpen.value || isA2HelpModalOpen.value || isA3HelpModalOpen.value || isMrHelpModalOpen.value || isDrainageHelpModalOpen.value) {
    return
  }

  const panel = document.querySelector('.fixed.left-24')
  const sidebar = document.querySelector('aside')
  if (panel && !panel.contains(e.target) && sidebar && !sidebar.contains(e.target)) {
    activeParam.value = null
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  document.addEventListener('mousedown', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  document.removeEventListener('mousedown', handleClickOutside)
})

const panelTitles = {
  layers:    'Capas estructurales',
  stats:     'Propiedades estadísticas',
  serv:      'Serviciabilidad',
  traffic:   'Tránsito y Carga (W18)',
  materials: 'Materiales de capa',
}

function changeView(newView) {
  view.value = newView
  activeParam.value = null
}

function toggleParam(paramId) {
  if (activeParam.value === paramId) {
    activeParam.value = null
  } else {
    activeParam.value = paramId
  }
}
</script>

<style scoped>
/* Animación deslizante del panel flotante */
.panel-slide-enter-active {
  transition: all 0.3s var(--ease-drawer);
}
.panel-slide-leave-active {
  transition: all 0.25s cubic-bezier(0.25, 0, 1, 1);
}
.panel-slide-enter-from,
.panel-slide-leave-to {
  opacity: 0;
  transform: translateX(-24px) scale(0.98);
}

/* Animación de desvanecimiento para el dropdown custom */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: all 0.15s cubic-bezier(0.16, 1, 0.3, 1);
}
.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Animación para el modal de ayuda */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
  backdrop-filter: blur(0px);
}
.modal-fade-enter-active .bg-white,
.modal-fade-leave-active .bg-white {
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}
.modal-fade-enter-from .bg-white,
.modal-fade-leave-to .bg-white {
  transform: scale(0.95) translateY(12px);
  opacity: 0;
}
</style>
