<template>
  <div class="flex flex-col gap-4 p-4 h-[calc(100vh-4rem)] overflow-hidden select-none">
    <!-- Fila Superior: 3D Izquierda, 2D Derecha -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-4 flex-1 min-h-0">
      <div class="xl:col-span-2 h-full">
        <Pavement3D class="h-full" />
      </div>
      <div class="xl:col-span-1 h-full">
        <PavementDiagram class="h-full" />
      </div>
    </div>

    <!-- Fila Inferior: Tabla -->
    <div class="w-full shrink-0">
      <SummaryTable />
    </div>
  </div>
</template>

<script setup>
import PavementDiagram from '@/components/design/PavementDiagram.vue'
import SummaryTable    from '@/components/design/SummaryTable.vue'
import Pavement3D      from '@/components/design/Pavement3D.vue'
</script>
