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

          <div class="flex-1 overflow-auto pr-1">
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
            <div v-if="activeParam === 'stats'" class="space-y-4">
              <!-- Gráfico de Confiabilidad (Campana de Gauss - Interactivo, Sin fondo, 90% ancho, Más alto y ancho) -->
              <div class="w-full flex justify-center py-1 select-none overflow-visible">
                <svg
                  ref="svgRef"
                  class="w-[92%] h-[320px] cursor-ew-resize select-none overflow-visible touch-none"
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

              <div class="relative relative-dropdown-container">
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
              <div>
                <label class="field-label">Desviación estándar normal (Zr)</label>
                <input v-model.number="s.Zr" type="number" step="0.001" class="field-input font-mono" readonly />
              </div>
              <div class="space-y-1.5">
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
            <div v-if="activeParam === 'serv'" class="space-y-4">
              <div class="flex items-center justify-between">
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
              <div class="w-full flex justify-center py-1 select-none overflow-visible">
                <svg
                  ref="servSvgRef"
                  class="w-[92%] h-[320px] select-none overflow-visible touch-none"
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
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="field-label">Servic. Inicial (pᵢ)</label>
                  <input v-model.number="s.pi" type="number" step="0.1" min="3.5" max="5.0" class="field-input font-mono" @change="validateServiciabilidad" />
                </div>
                <div>
                  <label class="field-label">Servic. Terminal (pₜ)</label>
                  <input v-model.number="s.pt" type="number" step="0.1" min="1.5" max="3.5" class="field-input font-mono" @change="validateServiciabilidad" />
                </div>
              </div>
              <div>
                <label class="field-label">Pérdida de serviciabilidad (ΔPSI)</label>
                <input :value="s.DPSI" type="number" class="field-input font-mono" readonly />
              </div>
            </div>

            <!-- Tránsito Panel -->
            <div v-if="activeParam === 'traffic'" class="space-y-4">
              <div>
                <label class="field-label">Ejes equivalentes (W₁₈)</label>
                <input v-model.number="s.W18" type="number" step="100000" min="1000" class="field-input font-mono" />
              </div>
            </div>

            <!-- Materiales Panel -->
            <div v-if="activeParam === 'materials'" class="space-y-4 pr-1">
              <!-- Carpeta asfáltica -->
              <div class="p-3 bg-slate-50/30 border border-slate-100 rounded-xl space-y-2">
                <span class="text-[10px] font-bold text-slate-800 uppercase tracking-wider block">Carpeta asfáltica</span>
                <div class="flex items-center justify-between gap-4">
                  <span class="text-xs text-slate-500 font-medium">Coeficiente a₁</span>
                  <input type="number" step="0.001" v-model.number="s.a1" class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right" />
                </div>
              </div>

              <!-- Base granular -->
              <div v-if="s.numCapas >= 2" class="p-3 bg-slate-50/30 border border-slate-100 rounded-xl space-y-2">
                <span class="text-[10px] font-bold text-stone-600 uppercase tracking-wider block">Base granular</span>
                <div class="flex items-center justify-between gap-4">
                  <span class="text-xs text-slate-500 font-medium">Mr₁ (psi)</span>
                  <input type="number" step="1000" v-model.number="s.Mr1" class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right" />
                </div>
                <div class="flex items-center justify-between gap-4">
                  <span class="text-xs text-slate-500 font-medium">Coeficiente a₂</span>
                  <input type="number" step="0.001" v-model.number="s.a2" class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right" />
                </div>
                <div class="flex items-center justify-between gap-4">
                  <span class="text-xs text-slate-500 font-medium">Drenaje m₂</span>
                  <input type="number" step="0.01" v-model.number="s.m2" class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right" />
                </div>
              </div>

              <!-- Sub-base -->
              <div v-if="s.numCapas === 3" class="p-3 bg-slate-50/30 border border-slate-100 rounded-xl space-y-2">
                <span class="text-[10px] font-bold text-amber-800/80 uppercase tracking-wider block">Sub-base granular</span>
                <div class="flex items-center justify-between gap-4">
                  <span class="text-xs text-slate-500 font-medium">Mr₂ (psi)</span>
                  <input type="number" step="1000" v-model.number="s.Mr2" class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right" />
                </div>
                <div class="flex items-center justify-between gap-4">
                  <span class="text-xs text-slate-500 font-medium">Coeficiente a₃</span>
                  <input type="number" step="0.001" v-model.number="s.a3" class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right" />
                </div>
                <div class="flex items-center justify-between gap-4">
                  <span class="text-xs text-slate-500 font-medium">Drenaje m₃</span>
                  <input type="number" step="0.01" v-model.number="s.m3" class="w-24 border border-slate-200 rounded-lg px-2 py-1 text-xs font-mono text-right" />
                </div>
              </div>

              <!-- Subrasante -->
              <div class="p-3 bg-slate-50/30 border border-slate-100 rounded-xl space-y-2">
                <span class="text-[10px] font-bold text-emerald-800 uppercase tracking-wider block">Subrasante</span>
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
  </div>
</template>

<script setup>
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
