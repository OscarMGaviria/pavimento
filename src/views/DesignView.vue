<template>
  <div class="flex flex-col gap-6 p-6 min-h-full overflow-y-auto select-none">
    <!-- Sección Superior: Visor 3D Interactivo a Ancho Completo -->
    <div class="w-full shrink-0">
      <Pavement3D />
    </div>

    <!-- Sección Inferior: Diagrama 2D y Tabla Resumen Consolidadora -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6 items-start">
      <PavementDiagram class="xl:col-span-1" />
      <SummaryTable class="xl:col-span-2" />
    </div>
  </div>
</template>

<script setup>
import PavementDiagram from '@/components/design/PavementDiagram.vue'
import SummaryTable    from '@/components/design/SummaryTable.vue'
import Pavement3D      from '@/components/design/Pavement3D.vue'
</script>
