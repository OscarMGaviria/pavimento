<template>
  <div class="bg-white rounded-2xl border border-slate-100 shadow-sm shadow-slate-100/40 p-4 select-none flex flex-col h-full overflow-hidden">
    <!-- Controles Superiores -->
    <div class="flex flex-wrap items-center justify-between mb-4 gap-4 shrink-0">
      <div class="flex items-center gap-2">
        <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400">Modelo 3D (Carga)</h2>
      </div>

      <div class="flex items-center gap-2">
        <!-- Selector de Eje Vehicular -->
        <div class="flex gap-1.5 bg-slate-100 p-0.5 rounded-lg text-[10px] font-bold">
          <button
            @click="axleType = 'single'"
            :class="[
              'px-2.5 py-1 rounded-md transition-all cursor-pointer select-none',
              axleType === 'single' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-700'
            ]"
          >Eje Simple</button>
          <button
            @click="axleType = 'double'"
            :class="[
              'px-2.5 py-1 rounded-md transition-all cursor-pointer select-none',
              axleType === 'double' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-700'
            ]"
          >Eje Tándem</button>
          <button
            @click="axleType = 'c3s2'"
            :class="[
              'px-2.5 py-1 rounded-md transition-all cursor-pointer select-none',
              axleType === 'c3s2' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-700'
            ]"
          >Camión C3-S2</button>
        </div>

        <!-- Selector de Bulbo de Presión -->
        <button
          @click="showStressBulb = !showStressBulb"
          :class="[
            'px-2.5 py-1 rounded-md transition-all cursor-pointer select-none text-[10px] font-bold border',
            showStressBulb 
              ? 'bg-slate-900 text-amber-500 border-amber-500/30 shadow-sm shadow-amber-500/5' 
              : 'bg-slate-100 text-slate-500 border-transparent hover:text-slate-700'
          ]"
        >
          Bulbo Presión: {{ showStressBulb ? 'Sí' : 'No' }}
        </button>
      </div>
    </div>

    <!-- Contenedor WebGL con fondo claro -->
    <div ref="container" class="w-full flex-1 min-h-0 bg-slate-50/50 border border-slate-100 rounded-xl overflow-hidden relative shadow-inner">
      <!-- Instrucciones de Cámara -->
      <span class="absolute bottom-3 left-3 text-[9px] font-bold text-slate-500 uppercase tracking-widest pointer-events-none select-none bg-white/80 border border-slate-200/50 shadow-sm px-2.5 py-1 rounded-lg backdrop-blur-sm z-10">
        Arrastra para rotar • Click Der para desplazar
      </span>
      
      <div v-if="!results" class="absolute inset-0 flex items-center justify-center text-slate-400 text-xs font-semibold bg-slate-50/50 z-20">
        Ingresa parámetros para iniciar render 3D
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { useAASHTODesign } from '@/composables/useAASHTODesign.js'

const { results } = useAASHTODesign()

const container = ref(null)
const axleType = ref('single') // 'single' | 'double'
const showStressBulb = ref(true)

let scene, camera, renderer, controls
let animId
let layerGroup, vehicleGroup
let wheelsList = []
let roadDashes = []
let roadSigns = []
let hazardLights = []
let grass3DList = []

// Dimensiones SVG/3D
const SCALE_Y = 0.05 // 10 cm = 0.5 unidades de alto
const WIDTH_3D = 7
const DEPTH_3D = 5

// --- Generador de Texturas Procedurales en Canvas ---
let textures = {}

function createProceduralTextures() {
  // 1. Textura Asfalto (CA)
  const asphaltCanvas = document.createElement('canvas')
  asphaltCanvas.width = 256
  asphaltCanvas.height = 256
  const asphaltCtx = asphaltCanvas.getContext('2d')
  asphaltCtx.fillStyle = '#2d333f' // Asfalto gris oscuro
  asphaltCtx.fillRect(0, 0, 256, 256)
  // Añadir grano/piedra
  for (let i = 0; i < 1500; i++) {
    const x = Math.random() * 256
    const y = Math.random() * 256
    const size = Math.random() * 2 + 0.5
    asphaltCtx.fillStyle = Math.random() > 0.6 ? '#1b1e25' : '#4f5869'
    asphaltCtx.fillRect(x, y, size, size)
  }
  const asphaltTex = new THREE.CanvasTexture(asphaltCanvas)
  asphaltTex.wrapS = THREE.RepeatWrapping
  asphaltTex.wrapT = THREE.RepeatWrapping
  asphaltTex.repeat.set(4, 3)
  textures.asphalt = asphaltTex

  // 2. Textura Base Granular (Arena/Gravas)
  const baseCanvas = document.createElement('canvas')
  baseCanvas.width = 128
  baseCanvas.height = 128
  const baseCtx = baseCanvas.getContext('2d')
  baseCtx.fillStyle = '#b0a38c'
  baseCtx.fillRect(0, 0, 128, 128)
  for (let i = 0; i < 800; i++) {
    const x = Math.random() * 128
    const y = Math.random() * 128
    const size = Math.random() * 3 + 1
    baseCtx.fillStyle = Math.random() > 0.5 ? '#8f816a' : '#cbd5e1'
    baseCtx.fillRect(x, y, size, size)
  }
  const baseTex = new THREE.CanvasTexture(baseCanvas)
  baseTex.wrapS = THREE.RepeatWrapping
  baseTex.wrapT = THREE.RepeatWrapping
  baseTex.repeat.set(2, 2)
  textures.base = baseTex

  // 3. Textura Sub-base Granular (Tierra pedregosa)
  const subCanvas = document.createElement('canvas')
  subCanvas.width = 128
  subCanvas.height = 128
  const subCtx = subCanvas.getContext('2d')
  subCtx.fillStyle = '#826550'
  subCtx.fillRect(0, 0, 128, 128)
  for (let i = 0; i < 600; i++) {
    const x = Math.random() * 128
    const y = Math.random() * 128
    const size = Math.random() * 4 + 1.5
    subCtx.fillStyle = Math.random() > 0.5 ? '#5c4636' : '#9a826f'
    subCtx.fillRect(x, y, size, size)
  }
  const subTex = new THREE.CanvasTexture(subCanvas)
  subTex.wrapS = THREE.RepeatWrapping
  subTex.wrapT = THREE.RepeatWrapping
  subTex.repeat.set(2, 2)
  textures.subbase = subTex

  // 4. Textura de Banda de Rodadura (Tread) Bridgestone M-DRIVE (Cocos/Bloques 3D)
  const treadCanvas = document.createElement('canvas')
  treadCanvas.width = 512
  treadCanvas.height = 256
  const treadCtx = treadCanvas.getContext('2d')
  treadCtx.fillStyle = '#18191d' // Gris oscuro carbón
  treadCtx.fillRect(0, 0, 512, 256)
  
  // Dibujar 4 líneas longitudinales principales en negro para canales
  treadCtx.fillStyle = '#090a0c'
  const linesY = [35, 90, 166, 221]
  linesY.forEach(y => {
    treadCtx.fillRect(0, y, 512, 10)
  })
  
  // Bloques de tracción (cocos) desfasados con biseles de volumen
  const secHeights = [0, 35, 90, 166, 221, 256]
  for (let s = 0; s < 5; s++) {
    const topY = secHeights[s]
    const botY = secHeights[s+1]
    const h = botY - topY
    const offset = s * 16
    
    for (let x = 0; x < 512; x += 32) {
      const bx = (x + offset) % 512
      
      // Ranura transversal
      treadCtx.fillStyle = '#090a0c'
      treadCtx.fillRect(bx, topY, 8, h)
      
      // Bisel de luz (volumen 3D)
      treadCtx.fillStyle = 'rgba(255, 255, 255, 0.08)'
      treadCtx.fillRect(bx + 8, topY + 2, 3, h - 4)
      treadCtx.fillRect(bx + 8, topY + 2, 20, 3)
      
      // Bisel de sombra
      treadCtx.fillStyle = 'rgba(0, 0, 0, 0.4)'
      treadCtx.fillRect(bx + 29, topY + 2, 3, h - 4)
      treadCtx.fillRect(bx + 8, topY + h - 5, 24, 3)
    }
  }
  const treadTex = new THREE.CanvasTexture(treadCanvas)
  treadTex.wrapS = THREE.RepeatWrapping
  treadTex.wrapT = THREE.RepeatWrapping
  treadTex.repeat.set(3, 1) // Repetir el patrón a lo largo de la rueda
  textures.tireTread = treadTex

  // 5. Textura Lateral del Neumático (Sidewall) con Relieves y Textos
  const sideCanvas = document.createElement('canvas')
  sideCanvas.width = 512
  sideCanvas.height = 512
  const sideCtx = sideCanvas.getContext('2d')
  sideCtx.fillStyle = '#18191d'
  sideCtx.fillRect(0, 0, 512, 512)
  
  const cx = 256
  const cy = 256
  
  // Relieves concéntricos
  sideCtx.strokeStyle = '#0a0b0d'
  sideCtx.lineWidth = 5
  for (let r of [240, 225, 210, 195, 180, 165]) {
    sideCtx.beginPath()
    sideCtx.arc(cx, cy, r, 0, Math.PI * 2)
    sideCtx.stroke()
  }
  
  sideCtx.strokeStyle = '#2d2f38'
  sideCtx.lineWidth = 1.5
  for (let r of [238, 223, 208, 178, 163]) {
    sideCtx.beginPath()
    sideCtx.arc(cx, cy, r, 0, Math.PI * 2)
    sideCtx.stroke()
  }

  // Rayas radiales finas en el hombro del neumático
  sideCtx.strokeStyle = '#0a0b0d'
  sideCtx.lineWidth = 2
  for (let a = 0; a < Math.PI * 2; a += Math.PI / 60) {
    const x1 = cx + Math.cos(a) * 242
    const y1 = cy + Math.sin(a) * 242
    const x2 = cx + Math.cos(a) * 250
    const y2 = cy + Math.sin(a) * 250
    sideCtx.beginPath()
    sideCtx.moveTo(x1, y1)
    sideCtx.lineTo(x2, y2)
    sideCtx.stroke()
  }

  // Función auxiliar para texto circular
  function drawCircularText(ctx, text, cx, cy, radius, startAngle, bottomAlign = false) {
    ctx.save()
    ctx.translate(cx, cy)
    
    let totalAngle = 0
    for(let i = 0; i < text.length; i++) {
      totalAngle += ctx.measureText(text[i]).width / radius
    }
    
    if (bottomAlign) {
      ctx.rotate(startAngle + totalAngle / 2)
      for(let i = 0; i < text.length; i++) {
        const char = text[i]
        const theta = ctx.measureText(char).width / radius
        ctx.rotate(-theta / 2)
        ctx.fillText(char, 0, radius)
        ctx.rotate(-theta / 2)
      }
    } else {
      ctx.rotate(startAngle - totalAngle / 2)
      for(let i = 0; i < text.length; i++) {
        const char = text[i]
        const theta = ctx.measureText(char).width / radius
        ctx.rotate(theta / 2)
        ctx.fillText(char, 0, -radius)
        ctx.rotate(theta / 2)
      }
    }
    ctx.restore()
  }

  // Textos grabados Bridgestone (Circulares)
  sideCtx.fillStyle = '#a1a1aa'
  sideCtx.font = 'bold 24px Arial, sans-serif'
  sideCtx.textAlign = 'center'
  sideCtx.textBaseline = 'middle'
  
  // Arriba (Lee de izq a der)
  drawCircularText(sideCtx, 'BRIDGESTONE', cx, cy, 188, 0, false)
  // Abajo (Lee de izq a der, derecho)
  drawCircularText(sideCtx, 'M-DRIVE 002', cx, cy, 188, 0, true)

  sideCtx.font = 'bold 12px Arial, sans-serif'
  sideCtx.fillStyle = '#71717a'
  
  // Izquierda (Lee de abajo hacia arriba)
  drawCircularText(sideCtx, '315 / 80 R 22.5', cx, cy, 188, -Math.PI / 2, false)
  // Derecha (Lee de arriba hacia abajo)
  drawCircularText(sideCtx, 'REGIONAL / LONG HAUL', cx, cy, 188, Math.PI / 2, false)

  const sideTex = new THREE.CanvasTexture(sideCanvas)
  textures.tireSidewall = sideTex

  // 6. Textura de Rin Galvanizado de Alta Fidelidad (10 Tuercas + 10 Agujeros)
  const rimCanvas = document.createElement('canvas')
  rimCanvas.width = 256
  rimCanvas.height = 256
  const rimCtx = rimCanvas.getContext('2d')
  
  // Degradado radial cromado/aluminio pulido para base
  const rimGradient = rimCtx.createRadialGradient(128, 128, 10, 128, 128, 128)
  rimGradient.addColorStop(0, '#334155')
  rimGradient.addColorStop(0.2, '#64748b')
  rimGradient.addColorStop(0.4, '#f1f5f9') // Banda brillante
  rimGradient.addColorStop(0.5, '#475569') // Sombra
  rimGradient.addColorStop(0.7, '#ffffff') // Brillo metálico máximo
  rimGradient.addColorStop(0.9, '#cbd5e1')
  rimGradient.addColorStop(1.0, '#334155')
  rimCtx.fillStyle = rimGradient
  rimCtx.fillRect(0, 0, 256, 256)

  // Superponer patrón procedural de cristales de zinc (galvanizado)
  rimCtx.save()
  rimCtx.globalCompositeOperation = 'source-atop'
  rimCtx.globalAlpha = 0.18 // Transparencia para mezclarse con el degradado radial
  for (let i = 0; i < 400; i++) {
    const rx = Math.random() * 256
    const ry = Math.random() * 256
    const size = Math.random() * 12 + 4
    
    rimCtx.fillStyle = Math.random() > 0.5 ? '#ffffff' : '#475569'
    
    // Dibujar un polígono triangular pequeño (cristal de zinc)
    rimCtx.beginPath()
    rimCtx.moveTo(rx, ry)
    rimCtx.lineTo(rx + Math.random() * size - size/2, ry + Math.random() * size - size/2)
    rimCtx.lineTo(rx + Math.random() * size - size/2, ry + Math.random() * size - size/2)
    rimCtx.closePath()
    rimCtx.fill()
  }
  rimCtx.restore()
  
  // Dibujar 10 agujeros de ventilación ovalados (hand holes) dispuestos radialmente
  rimCtx.fillStyle = '#090a0f' // Oscuridad interior del neumático/tambor
  rimCtx.strokeStyle = '#475569'
  rimCtx.lineWidth = 2
  for (let a = 0; a < Math.PI * 2; a += (Math.PI * 2) / 10) {
    const hx = 128 + Math.cos(a) * 80
    const hy = 128 + Math.sin(a) * 80
    
    rimCtx.save()
    rimCtx.translate(hx, hy)
    rimCtx.rotate(a + Math.PI / 2)
    rimCtx.beginPath()
    rimCtx.roundRect(-12, -22, 24, 44, 12)
    rimCtx.fill()
    rimCtx.stroke()
    
    // Brillo blanco en el contorno del orificio
    rimCtx.strokeStyle = 'rgba(255, 255, 255, 0.4)'
    rimCtx.lineWidth = 1
    rimCtx.beginPath()
    rimCtx.roundRect(-12, -22, 24, 44, 12)
    rimCtx.stroke()
    rimCtx.restore()
  }
  
  // Dibujar 10 tuercas (lug nuts) en un círculo interior
  for (let a = 0; a < Math.PI * 2; a += (Math.PI * 2) / 10) {
    const bx = 128 + Math.cos(a) * 42
    const by = 128 + Math.sin(a) * 42
    
    // Sombra proyectada del perno
    rimCtx.fillStyle = 'rgba(0, 0, 0, 0.5)'
    rimCtx.beginPath()
    rimCtx.arc(bx + 1.5, by + 1.5, 7.5, 0, Math.PI * 2)
    rimCtx.fill()
    
    // Cuerpo metálico de la tuerca
    const nutGrad = rimCtx.createRadialGradient(bx - 1.5, by - 1.5, 0.5, bx, by, 6)
    nutGrad.addColorStop(0, '#ffffff')
    nutGrad.addColorStop(0.5, '#cbd5e1')
    nutGrad.addColorStop(1, '#475569')
    rimCtx.fillStyle = nutGrad
    rimCtx.beginPath()
    rimCtx.arc(bx, by, 6.5, 0, Math.PI * 2)
    rimCtx.fill()
    
    // Centro del perno roscado interior
    rimCtx.fillStyle = '#1e293b'
    rimCtx.beginPath()
    rimCtx.arc(bx, by, 2.5, 0, Math.PI * 2)
    rimCtx.fill()
  }
  
  // Línea de borde del centro
  rimCtx.strokeStyle = '#1e293b'
  rimCtx.lineWidth = 2
  rimCtx.beginPath()
  rimCtx.arc(128, 128, 30, 0, Math.PI * 2)
  rimCtx.stroke()
  
  const rimTex = new THREE.CanvasTexture(rimCanvas)
  textures.rim = rimTex

  // Textura de Grama/Pasto de Alta Definición
  const grassCanvas = document.createElement('canvas')
  grassCanvas.width = 256
  grassCanvas.height = 256
  const grassCtx = grassCanvas.getContext('2d')
  grassCtx.fillStyle = '#15803d' // Base verde rica
  grassCtx.fillRect(0, 0, 256, 256)
  
  // Dibujar hojas de pasto individuales y ruido de tonos
  for (let i = 0; i < 4000; i++) {
    const gx = Math.random() * 256
    const gy = Math.random() * 256
    const angle = (Math.random() - 0.5) * 0.5
    const len = Math.random() * 5 + 3
    const w = Math.random() * 1.0 + 0.4
    
    // Variación de verdes
    grassCtx.strokeStyle = Math.random() > 0.5 ? '#166534' : (Math.random() > 0.4 ? '#16a34a' : '#14532d')
    grassCtx.lineWidth = w
    grassCtx.beginPath()
    grassCtx.moveTo(gx, gy)
    grassCtx.lineTo(gx + Math.sin(angle) * len, gy - Math.cos(angle) * len)
    grassCtx.stroke()
  }
  const grassTex = new THREE.CanvasTexture(grassCanvas)
  grassTex.wrapS = THREE.RepeatWrapping
  grassTex.wrapT = THREE.RepeatWrapping
  textures.grass = grassTex

  // 7. Texturas de señales viales reglamentarias
  textures.signSpeed30 = createSpeedLimitTexture(30)
  textures.signSpeed40 = createSpeedLimitTexture(40)
  textures.signPare = createRegulatoryTexture('pare')
  textures.signNoParquear = createRegulatoryTexture('no_parquear')
  textures.signNoAdelantar = createRegulatoryTexture('no_adelantar')
  textures.signNoPase = createRegulatoryTexture('no_pase')

  // 8. Texturas del pórtico transversal y advertencia
  textures.hazardStripe = createHazardStripeTexture()
  textures.gantryLeft = createGantrySignTexture('Costa Atlántica', 'Medellín', 'up')
  textures.gantryRight = createGantrySignTexture('Manizales', 'Bogotá', 'right')

  // 9. Texturas del contenedor de carga (Shipping Container)
  textures.containerSideLeft = createContainerSideTexture('left')
  textures.containerSideRight = createContainerSideTexture('right')
  textures.containerSideBump = createContainerBumpTexture()
  textures.containerFront = createContainerFrontTexture()
  textures.containerFrontBump = createContainerFrontBumpTexture()
  textures.containerDoor = createContainerDoorTexture()
}

function createSpeedLimitTexture(num) {
  const canvas = document.createElement('canvas')
  canvas.width = 128
  canvas.height = 128
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, 128, 128)
  
  // Aro rojo exterior
  ctx.fillStyle = '#d32f2f'
  ctx.beginPath()
  ctx.arc(64, 64, 60, 0, Math.PI * 2)
  ctx.fill()
  
  // Fondo blanco interior
  ctx.fillStyle = '#ffffff'
  ctx.beginPath()
  ctx.arc(64, 64, 46, 0, Math.PI * 2)
  ctx.fill()
  
  // Texto del número
  ctx.fillStyle = '#1a1a1a'
  ctx.font = 'bold 54px sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(num.toString(), 64, 64)
  
  const tex = new THREE.CanvasTexture(canvas)
  tex.center.set(0.5, 0.5)
  tex.rotation = Math.PI / 2
  return tex
}

function createRegulatoryTexture(type) {
  const canvas = document.createElement('canvas')
  canvas.width = 256
  canvas.height = 256
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, 256, 256)
  
  if (type === 'pare') {
    // Octágono rojo (SR-01 PARE)
    ctx.fillStyle = '#d32f2f'
    drawOctagon(ctx, 128, 128, 115)
    ctx.fill()
    
    // Borde blanco interior
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = 6
    drawOctagon(ctx, 128, 128, 105)
    ctx.stroke()
    
    // Texto PARE
    ctx.fillStyle = '#ffffff'
    ctx.font = 'bold 80px sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText('PARE', 128, 128)
  }
  else if (type === 'no_parquear') {
    // Círculo blanco (SR-28 Prohibido parquear)
    ctx.fillStyle = '#ffffff'
    ctx.beginPath()
    ctx.arc(128, 128, 115, 0, Math.PI * 2)
    ctx.fill()
    
    // Anillo rojo exterior
    ctx.strokeStyle = '#d32f2f'
    ctx.lineWidth = 18
    ctx.beginPath()
    ctx.arc(128, 128, 106, 0, Math.PI * 2)
    ctx.stroke()
    
    // Letra P
    ctx.fillStyle = '#1a1a1a'
    ctx.font = 'bold 125px sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText('P', 128, 122)
    
    // Barra diagonal roja
    ctx.strokeStyle = '#d32f2f'
    ctx.lineWidth = 16
    ctx.beginPath()
    ctx.moveTo(128 - 75, 128 - 75)
    ctx.lineTo(128 + 75, 128 + 75)
    ctx.stroke()
  }
  else if (type === 'no_adelantar') {
    // Círculo blanco (SR-26 No adelantar)
    ctx.fillStyle = '#ffffff'
    ctx.beginPath()
    ctx.arc(128, 128, 115, 0, Math.PI * 2)
    ctx.fill()
    
    // Anillo rojo
    ctx.strokeStyle = '#d32f2f'
    ctx.lineWidth = 18
    ctx.beginPath()
    ctx.arc(128, 128, 106, 0, Math.PI * 2)
    ctx.stroke()
    
    // Dos autos en negro
    ctx.fillStyle = '#1a1a1a'
    drawMiniCar(ctx, 92, 140)
    drawMiniCar(ctx, 164, 140)
    
    // Barra diagonal
    ctx.strokeStyle = '#d32f2f'
    ctx.lineWidth = 16
    ctx.beginPath()
    ctx.moveTo(128 - 75, 128 - 75)
    ctx.lineTo(128 + 75, 128 + 75)
    ctx.stroke()
  }
  else if (type === 'no_pase') {
    // Círculo rojo (SR-04 No pase)
    ctx.fillStyle = '#d32f2f'
    ctx.beginPath()
    ctx.arc(128, 128, 115, 0, Math.PI * 2)
    ctx.fill()
    
    // Borde blanco
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = 6
    ctx.beginPath()
    ctx.arc(128, 128, 108, 0, Math.PI * 2)
    ctx.stroke()
    
    // Barra blanca central
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(40, 113, 176, 30)
    
    // Texto NO y PASE
    ctx.fillStyle = '#ffffff'
    ctx.font = 'bold 36px sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText('NO', 128, 75)
    ctx.fillText('PASE', 128, 181)
  }
  
  const tex = new THREE.CanvasTexture(canvas)
  tex.center.set(0.5, 0.5)
  tex.rotation = Math.PI / 2
  return tex
}

function drawOctagon(ctx, cx, cy, r) {
  ctx.beginPath()
  for (let i = 0; i < 8; i++) {
    const angle = (i * Math.PI) / 4 + Math.PI / 8
    const x = cx + Math.cos(angle) * r
    const y = cy + Math.sin(angle) * r
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  }
  ctx.closePath()
}

function drawMiniCar(ctx, cx, cy) {
  ctx.save()
  ctx.translate(cx, cy)
  
  // Carrocería
  ctx.beginPath()
  ctx.roundRect(-22, -10, 44, 20, 4)
  ctx.fill()
  
  // Cabina
  ctx.beginPath()
  ctx.roundRect(-14, -22, 28, 14, 4)
  ctx.fill()
  
  // Ventanas
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(-10, -18, 20, 8)
  
  // Llantas
  ctx.fillStyle = '#1a1a1a'
  ctx.fillRect(-18, 10, 8, 4)
  ctx.fillRect(10, 10, 8, 4)
  
  ctx.restore()
}

function createHazardStripeTexture() {
  const canvas = document.createElement('canvas')
  canvas.width = 128
  canvas.height = 128
  const ctx = canvas.getContext('2d')
  
  // Fondo amarillo
  ctx.fillStyle = '#eab308' // Amarillo brillante
  ctx.fillRect(0, 0, 128, 128)
  
  // Rayas negras diagonales
  ctx.fillStyle = '#0f172a'
  const stripeWidth = 16
  for (let x = -128; x < 256; x += stripeWidth * 2) {
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x + stripeWidth, 0)
    ctx.lineTo(x + stripeWidth + 128, 128)
    ctx.lineTo(x + 128, 128)
    ctx.closePath()
    ctx.fill()
  }
  
  const tex = new THREE.CanvasTexture(canvas)
  tex.wrapS = THREE.RepeatWrapping
  tex.wrapT = THREE.RepeatWrapping
  tex.repeat.set(4, 1)
  return tex
}

function createGantrySignTexture(textLine1, textLine2, arrowDir) {
  const canvas = document.createElement('canvas')
  canvas.width = 512
  canvas.height = 256
  const ctx = canvas.getContext('2d')
  
  // Fondo verde informativo vial
  ctx.fillStyle = '#015c3a'
  ctx.fillRect(0, 0, 512, 256)
  
  // Margen blanco exterior doble
  ctx.strokeStyle = '#ffffff'
  ctx.lineWidth = 8
  ctx.strokeRect(10, 10, 492, 236)
  
  ctx.lineWidth = 3
  ctx.strokeRect(18, 18, 476, 220)
  
  // Texto y flechas
  ctx.fillStyle = '#ffffff'
  ctx.textBaseline = 'middle'
  
  if (arrowDir === 'up') {
    // Flechas arriba a la izquierda
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = 6
    ctx.fillStyle = '#ffffff'
    
    drawArrowUp(ctx, 60, 80)
    drawArrowUp(ctx, 60, 176)
    
    ctx.font = 'bold 36px Arial, sans-serif'
    ctx.textAlign = 'left'
    ctx.fillText(textLine1, 120, 80)
    ctx.fillText(textLine2, 120, 176)
  } else {
    // Flechas a la derecha a la derecha
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = 6
    ctx.fillStyle = '#ffffff'
    
    drawArrowRight(ctx, 430, 80)
    drawArrowRight(ctx, 430, 176)
    
    ctx.font = 'bold 36px Arial, sans-serif'
    ctx.textAlign = 'left'
    ctx.fillText(textLine1, 50, 80)
    ctx.fillText(textLine2, 50, 176)
  }
  
  const tex = new THREE.CanvasTexture(canvas)
  return tex
}

function drawArrowUp(ctx, x, y) {
  ctx.save()
  ctx.translate(x, y)
  ctx.beginPath()
  ctx.moveTo(0, 20)
  ctx.lineTo(0, -15)
  ctx.stroke()
  
  ctx.beginPath()
  ctx.moveTo(-12, -5)
  ctx.lineTo(0, -22)
  ctx.lineTo(12, -5)
  ctx.stroke()
  ctx.restore()
}

function drawArrowRight(ctx, x, y) {
  ctx.save()
  ctx.translate(x, y)
  ctx.beginPath()
  ctx.moveTo(-20, 0)
  ctx.lineTo(15, 0)
  ctx.stroke()
  
  ctx.beginPath()
  ctx.moveTo(5, -12)
  ctx.lineTo(22, 0)
  ctx.lineTo(5, 12)
  ctx.stroke()
  ctx.restore()
}

function createContainerSideTexture(side) {
  const canvas = document.createElement('canvas')
  canvas.width = 1024
  canvas.height = 512
  const ctx = canvas.getContext('2d')
  
  // 1. Fondo rojo anaranjado
  ctx.fillStyle = '#d03d25'
  ctx.fillRect(0, 0, 1024, 512)
  
  // 2. Dibujar textos y marcas
  ctx.fillStyle = '#ffffff'
  ctx.textBaseline = 'middle'
  
  if (side === 'right') {
    // Etiqueta vertical blanca a la izquierda (frente)
    ctx.fillRect(80, 50, 26, 300)
    ctx.fillStyle = '#000000'
    ctx.font = 'bold 16px "Courier New", monospace'
    ctx.textAlign = 'center'
    const labelText = "SUDU 681410 6"
    for (let i = 0; i < labelText.length; i++) {
      ctx.fillText(labelText[i], 93, 75 + i * 20)
    }
    
    // Texto HAMBURG
    ctx.fillStyle = '#ffffff'
    ctx.font = 'bold 125px Georgia, serif'
    ctx.textAlign = 'center'
    ctx.fillText('HAMBURG', 620, 256)
  } else {
    // Etiqueta vertical blanca a la derecha (frente)
    ctx.fillRect(1024 - 80 - 26, 50, 26, 300)
    ctx.fillStyle = '#000000'
    ctx.font = 'bold 16px "Courier New", monospace'
    ctx.textAlign = 'center'
    const labelText = "SUDU 681410 6"
    for (let i = 0; i < labelText.length; i++) {
      ctx.fillText(labelText[i], 1024 - 93, 75 + i * 20)
    }
    
    // Texto HAMBURG
    ctx.fillStyle = '#ffffff'
    ctx.font = 'bold 125px Georgia, serif'
    ctx.textAlign = 'center'
    ctx.fillText('HAMBURG', 404, 256)
  }
  
  // 3. Sombras y brillos de corrugaciones (con marco liso de 16px)
  const numRibs = 40
  const cycle = 1024 / numRibs
  const borderX = 16
  const borderY = 16
  
  ctx.save()
  for (let i = 0; i < numRibs; i++) {
    const valleyStart = i * cycle + cycle * 0.45
    const valleyWidth = cycle * 0.45
    const rx = Math.max(borderX, valleyStart)
    const rw = Math.min(1024 - borderX, valleyStart + valleyWidth) - rx
    if (rw > 0) {
      ctx.globalAlpha = 0.24 // Sombras
      ctx.fillStyle = '#000000'
      ctx.fillRect(rx, borderY, rw, 512 - 2 * borderY)
    }
    
    const hillStart = i * cycle
    const hillWidth = cycle * 0.45
    const hx = Math.max(borderX, hillStart)
    const hw = Math.min(1024 - borderX, hillStart + hillWidth) - hx
    if (hw > 0) {
      ctx.globalAlpha = 0.15 // Brillos
      ctx.fillStyle = '#ffffff'
      ctx.fillRect(hx, borderY, hw, 512 - 2 * borderY)
    }
  }
  ctx.restore()
  
  const tex = new THREE.CanvasTexture(canvas)
  return tex
}

function createContainerBumpTexture() {
  const canvas = document.createElement('canvas')
  canvas.width = 1024
  canvas.height = 512
  const ctx = canvas.getContext('2d')
  
  // Fondo plano (gris medio)
  ctx.fillStyle = '#808080'
  ctx.fillRect(0, 0, 1024, 512)
  
  const borderX = 16
  const borderY = 16
  const numRibs = 40
  const cycle = 1024 / numRibs
  
  for (let x = borderX; x < 1024 - borderX; x++) {
    const phase = (x % cycle) / cycle
    let h = 128
    if (phase < 0.45) {
      h = 220
    } else if (phase < 0.55) {
      h = 220 - (phase - 0.45) * 10 * 180
    } else if (phase < 0.9) {
      h = 40
    } else {
      h = 40 + (phase - 0.9) * 10 * 180
    }
    ctx.fillStyle = `rgb(${h}, ${h}, ${h})`
    ctx.fillRect(x, borderY, 1, 512 - 2 * borderY)
  }
  
  const tex = new THREE.CanvasTexture(canvas)
  return tex
}

function createContainerFrontTexture() {
  const canvas = document.createElement('canvas')
  canvas.width = 512
  canvas.height = 512
  const ctx = canvas.getContext('2d')
  
  ctx.fillStyle = '#d03d25'
  ctx.fillRect(0, 0, 512, 512)
  
  const numRibs = 13
  const cycle = 512 / numRibs
  const border = 12
  
  ctx.fillStyle = '#000000'
  ctx.save()
  for (let i = 0; i < numRibs; i++) {
    const valleyStart = i * cycle + cycle * 0.45
    const valleyWidth = cycle * 0.45
    const rx = Math.max(border, valleyStart)
    const rw = Math.min(512 - border, valleyStart + valleyWidth) - rx
    if (rw > 0) {
      ctx.globalAlpha = 0.24
      ctx.fillRect(rx, border, rw, 512 - 2 * border)
    }
    
    const hillStart = i * cycle
    const hillWidth = cycle * 0.45
    const hx = Math.max(border, hillStart)
    const hw = Math.min(512 - border, hillStart + hillWidth) - hx
    if (hw > 0) {
      ctx.globalAlpha = 0.15
      ctx.fillStyle = '#ffffff'
      ctx.fillRect(hx, border, hw, 512 - 2 * border)
    }
  }
  ctx.restore()
  
  const tex = new THREE.CanvasTexture(canvas)
  return tex
}

function createContainerFrontBumpTexture() {
  const canvas = document.createElement('canvas')
  canvas.width = 512
  canvas.height = 512
  const ctx = canvas.getContext('2d')
  
  ctx.fillStyle = '#808080'
  ctx.fillRect(0, 0, 512, 512)
  
  const border = 12
  const numRibs = 13
  const cycle = 512 / numRibs
  
  for (let x = border; x < 512 - border; x++) {
    const phase = (x % cycle) / cycle
    let h = 128
    if (phase < 0.45) {
      h = 220
    } else if (phase < 0.55) {
      h = 220 - (phase - 0.45) * 10 * 180
    } else if (phase < 0.9) {
      h = 40
    } else {
      h = 40 + (phase - 0.9) * 10 * 180
    }
    ctx.fillStyle = `rgb(${h}, ${h}, ${h})`
    ctx.fillRect(x, border, 1, 512 - 2 * border)
  }
  
  const tex = new THREE.CanvasTexture(canvas)
  return tex
}

function createContainerDoorTexture() {
  const canvas = document.createElement('canvas')
  canvas.width = 512
  canvas.height = 512
  const ctx = canvas.getContext('2d')
  
  // Fondo rojo anaranjado
  ctx.fillStyle = '#d03d25'
  ctx.fillRect(0, 0, 512, 512)
  
  // Marco perimetral liso
  ctx.fillStyle = '#b6301b'
  ctx.fillRect(0, 0, 512, 12)
  ctx.fillRect(0, 500, 512, 12)
  ctx.fillRect(0, 0, 12, 512)
  ctx.fillRect(500, 0, 12, 512)
  
  // Línea de junta central
  ctx.strokeStyle = '#230704'
  ctx.lineWidth = 3
  ctx.beginPath()
  ctx.moveTo(256, 0)
  ctx.lineTo(256, 512)
  ctx.stroke()
  
  // Barras metálicas verticales
  ctx.fillStyle = '#cccccc'
  ctx.strokeStyle = '#475569'
  ctx.lineWidth = 1.5
  
  const barX = [95, 185, 327, 417]
  barX.forEach(x => {
    // Barra
    ctx.fillRect(x, 12, 12, 488)
    ctx.strokeRect(x, 12, 12, 488)
    
    // Bisagras de sujeción
    ctx.fillStyle = '#475569'
    ctx.fillRect(x - 3, 50, 18, 12)
    ctx.fillRect(x - 3, 250, 18, 12)
    ctx.fillRect(x - 3, 450, 18, 12)
    ctx.fillStyle = '#cccccc'
  })
  
  // Cerrojos y manillas
  ctx.fillStyle = '#334155'
  ctx.fillRect(145, 270, 50, 10)
  ctx.fillRect(317, 270, 50, 10)
  
  const tex = new THREE.CanvasTexture(canvas)
  return tex
}

function createTubeBetweenPoints(p1, p2, radius, material) {
  const direction = new THREE.Vector3().subVectors(p2, p1)
  const length = direction.length()
  
  const geom = new THREE.CylinderGeometry(radius, radius, length, 6)
  geom.translate(0, length / 2, 0)
  geom.rotateX(Math.PI / 2)
  
  const mesh = new THREE.Mesh(geom, material)
  mesh.position.copy(p1)
  mesh.lookAt(p2)
  
  mesh.castShadow = true
  mesh.receiveShadow = true
  return mesh
}

function createTandemFender(zCenter, sideX, material, R_WHEEL) {
  const fenderGroup = new THREE.Group()
  
  // Top flat plate
  const topGeom = new THREE.BoxGeometry(0.8, 0.08, 2.8)
  const topMesh = new THREE.Mesh(topGeom, material)
  topMesh.position.set(0, R_WHEEL + 0.12, 0)
  topMesh.castShadow = true
  topMesh.receiveShadow = true
  fenderGroup.add(topMesh)
  
  // Front angled plate
  const frontGeom = new THREE.BoxGeometry(0.8, 0.08, 0.6)
  const frontMesh = new THREE.Mesh(frontGeom, material)
  frontMesh.position.set(0, R_WHEEL - 0.1, -1.5)
  frontMesh.rotation.x = Math.PI / 6
  frontMesh.castShadow = true
  frontMesh.receiveShadow = true
  fenderGroup.add(frontMesh)
  
  // Rear angled plate
  const rearMesh = new THREE.Mesh(frontGeom, material)
  rearMesh.position.set(0, R_WHEEL - 0.1, 1.5)
  rearMesh.rotation.x = -Math.PI / 6
  rearMesh.castShadow = true
  rearMesh.receiveShadow = true
  fenderGroup.add(rearMesh)
  
  fenderGroup.position.set(sideX, 0, zCenter)
  return fenderGroup
}

// Inicializar Three
function initThree() {
  if (!container.value) return

  createProceduralTextures()

  const width = container.value.clientWidth
  const height = container.value.clientHeight

  // 1. Escena
  scene = new THREE.Scene()
  scene.background = new THREE.Color('#ffffff') // Fondo blanco del modelo

  // 2. Cámara
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
  camera.position.set(9, 7, 10.5)

  // 3. Renderizador
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFShadowMap
  renderer.localClippingEnabled = true // Activar planos de recorte local en la GPU
  container.value.appendChild(renderer.domElement)

  // 4. Controles de Órbita
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.maxPolarAngle = Math.PI / 2 - 0.02
  controls.minDistance = 3
  controls.maxDistance = 22

  // 5. Luces (Ajustadas para fondo blanco)
  const ambient = new THREE.AmbientLight(0xffffff, 0.5)
  scene.add(ambient)

  const hemi = new THREE.HemisphereLight(0xffffff, 0xe2e8f0, 0.4)
  hemi.position.set(0, 20, 0)
  scene.add(hemi)

  const sun = new THREE.DirectionalLight(0xffffff, 0.7)
  sun.position.set(10, 15, 5)
  sun.castShadow = true
  sun.shadow.mapSize.width = 1024
  sun.shadow.mapSize.height = 1024
  sun.shadow.camera.near = 0.5
  sun.shadow.camera.far = 40
  const d = 6
  sun.shadow.camera.left = -d
  sun.shadow.camera.right = d
  sun.shadow.camera.top = d
  sun.shadow.camera.bottom = -d
  scene.add(sun)

  // 6. Grupos
  layerGroup = new THREE.Group()
  scene.add(layerGroup)

  vehicleGroup = new THREE.Group()
  scene.add(vehicleGroup)

  updatePavement()
  updateVehicle()

  // Velocidad de movimiento del carril
  const ROAD_SPEED = 0.072
  const DEPTH_3D_VAL = 5.0

  // Bucle de animación (con rotación de ruedas en su plano y simulación de movimiento de carretera)
  function animate() {
    animId = requestAnimationFrame(animate)
    
    const isC3S2 = axleType.value === 'c3s2'
    const currentDepth = isC3S2 ? 35 : 5

    // 1. Rotar los neumáticos respecto a su centro en el eje X
    wheelsList.forEach(wheel => {
      wheel.rotation.x -= 0.08
    })

    // Hacer parpadear las luces intermitentes traseras (cada 500ms) cambiando el color (encendido/apagado)
    const lightsOn = Math.floor(Date.now() / 500) % 2 === 0
    hazardLights.forEach(light => {
      if (light.material) {
        light.material.color.setHex(lightsOn ? 0xf97316 : 0x4a2305)
      }
    })

    // 2. Desplazar la textura del asfalto en V (eje Y del canvas) para simular movimiento
    if (textures.asphalt) {
      textures.asphalt.offset.y += ROAD_SPEED * textures.asphalt.repeat.y / currentDepth
    }

    // 3. Desplazar los guiones amarillos y blancos en el eje Z (movimiento continuo)
    roadDashes.forEach(dash => {
      dash.position.z += ROAD_SPEED
      const limit = currentDepth / 2 + 0.5
      if (dash.position.z > limit) {
        // Enviar al principio (borde trasero)
        dash.position.z -= (currentDepth + 1.0)
      }
    })

    // Desplazar la grama 3D
    grass3DList.forEach(cluster => {
      cluster.position.z += ROAD_SPEED
      const limit = currentDepth / 2
      if (cluster.position.z > limit) {
        cluster.position.z -= currentDepth
      }
    })

    // 4. Desplazar las señales de tránsito laterales en el eje Z
    roadSigns.forEach(sign => {
      sign.position.z += ROAD_SPEED
      const limit = currentDepth / 2 + 2.0
      
      if (sign.userData.isGantry) {
        if (sign.position.z > limit) {
          // El pórtico debe salir cada 15 segundos. 15s * 60fps * 0.072 = 64.8 unidades de ciclo
          sign.position.z -= 64.8
        }
        // Ocultar si está fuera de la calzada para no verlo flotando en el aire
        sign.visible = (sign.position.z >= -currentDepth / 2 && sign.position.z <= limit)
      } else {
        // Señal vertical
        if (sign.position.z > limit) {
          // Separación triple (ciclo de 120 unidades para las 4 señales espaciadas 30 c/u)
          sign.position.z -= 120.0
        }
        // Ocultar si está fuera de la calzada para no verla flotando en el aire
        sign.visible = (sign.position.z >= -currentDepth / 2 && sign.position.z <= limit)
      }
    })
    
    controls.update()
    renderer.render(scene, camera)
  }
  animate()

  // Resize handler
  window.addEventListener('resize', onResize)
}

function onResize() {
  if (!container.value || !renderer) return
  const width = container.value.clientWidth
  const height = container.value.clientHeight
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

// Dibujar Capas con Texturas
function updatePavement() {
  if (!layerGroup) return

  while (layerGroup.children.length > 0) {
    const obj = layerGroup.children[0]
    disposeObject3D(obj)
    layerGroup.remove(obj)
  }

  if (!results.value) return

  const isC3S2 = axleType.value === 'c3s2'
  const currentDepth = isC3S2 ? 35 : 5
  const currentWidth = isC3S2 ? 26.8 : 7

  // Ajustar la densidad de la textura de forma de cuadrícula proporcional para evitar estiramientos
  if (textures.asphalt) {
    textures.asphalt.repeat.set((currentWidth / 7) * 4, (currentDepth / 5) * 3)
  }
  if (textures.base) {
    textures.base.repeat.set((currentWidth / 7) * 2, (currentDepth / 5) * 2)
  }
  if (textures.subbase) {
    textures.subbase.repeat.set((currentWidth / 7) * 2, (currentDepth / 5) * 2)
  }

  const capas = results.value.capas
  let yOffset = 0

  capas.forEach((capa) => {
    const h = capa.cm * SCALE_Y
    const geom = new THREE.BoxGeometry(currentWidth, h, currentDepth)

    // Asignar textura de acuerdo a la capa
    let tex = textures.asphalt
    let roughness = 0.8
    if (capa.nombre.includes('Base granular')) {
      tex = textures.base
      roughness = 0.9
    } else if (capa.nombre.includes('Sub-base')) {
      tex = textures.subbase
      roughness = 0.95
    }

    const mat = new THREE.MeshStandardMaterial({
      map: tex,
      roughness: roughness,
      metalness: 0.15
    })

    const mesh = new THREE.Mesh(geom, mat)
    mesh.position.y = -yOffset - h / 2
    mesh.castShadow = true
    mesh.receiveShadow = true
    layerGroup.add(mesh)

    yOffset += h
  })

  // Subrasante
  const subH = 1.5
  const subGeom = new THREE.BoxGeometry(currentWidth, subH, currentDepth)
  const subMat = new THREE.MeshStandardMaterial({
    color: 0x15803d, // Verde oscuro
    roughness: 0.98,
    metalness: 0.05
  })
  const subMesh = new THREE.Mesh(subGeom, subMat)
  subMesh.position.y = -yOffset - subH / 2
  subMesh.receiveShadow = true
  layerGroup.add(subMesh)

  // --- Capas de Grama / Bermas y Separador Central (solo C3S2) ---
  grass3DList = []
  if (isC3S2) {
    // Berma Izquierda: X = -11.8, ancho 3.2
    const leftGrassGeom = new THREE.BoxGeometry(3.2, 0.02, currentDepth)
    const leftGrassTex = textures.grass.clone()
    leftGrassTex.repeat.set(3.2 * 1.5, currentDepth * 1.5)
    leftGrassTex.needsUpdate = true
    const leftGrassMat = new THREE.MeshStandardMaterial({
      map: leftGrassTex,
      roughness: 0.95,
      metalness: 0.05
    })
    const leftGrass = new THREE.Mesh(leftGrassGeom, leftGrassMat)
    leftGrass.position.set(-11.8, 0.01, 0)
    leftGrass.receiveShadow = true
    leftGrass.castShadow = true
    layerGroup.add(leftGrass)

    // Separador Central: X = 0.0, ancho 2.4
    const centerGrassGeom = new THREE.BoxGeometry(2.4, 0.02, currentDepth)
    const centerGrassTex = textures.grass.clone()
    centerGrassTex.repeat.set(2.4 * 1.5, currentDepth * 1.5)
    centerGrassTex.needsUpdate = true
    const centerGrassMat = new THREE.MeshStandardMaterial({
      map: centerGrassTex,
      roughness: 0.95,
      metalness: 0.05
    })
    const centerGrass = new THREE.Mesh(centerGrassGeom, centerGrassMat)
    centerGrass.position.set(0, 0.01, 0)
    centerGrass.receiveShadow = true
    centerGrass.castShadow = true
    layerGroup.add(centerGrass)

    // Berma Derecha: X = 11.8, ancho 3.2
    const rightGrassGeom = new THREE.BoxGeometry(3.2, 0.02, currentDepth)
    const rightGrassTex = textures.grass.clone()
    rightGrassTex.repeat.set(3.2 * 1.5, currentDepth * 1.5)
    rightGrassTex.needsUpdate = true
    const rightGrassMat = new THREE.MeshStandardMaterial({
      map: rightGrassTex,
      roughness: 0.95,
      metalness: 0.05
    })
    const rightGrass = new THREE.Mesh(rightGrassGeom, rightGrassMat)
    rightGrass.position.set(11.8, 0.01, 0)
    rightGrass.receiveShadow = true
    rightGrass.castShadow = true
    layerGroup.add(rightGrass)

    // --- Grama 3D ---
    const colors = [0x166534, 0x15803d, 0x14532d]
    const bladeGeom = new THREE.ConeGeometry(0.025, 0.22, 4)
    bladeGeom.translate(0, 0.11, 0)
    
    function populateGrass3D(xCenter, xWidth, count) {
      for (let k = 0; k < count; k++) {
        const cluster = new THREE.Group()
        const col = colors[Math.floor(Math.random() * colors.length)]
        const grassMat = new THREE.MeshStandardMaterial({
          color: col,
          roughness: 0.9,
          metalness: 0.05
        })
        
        const numBlades = 3 + Math.floor(Math.random() * 3)
        for (let b = 0; b < numBlades; b++) {
          const blade = new THREE.Mesh(bladeGeom, grassMat)
          blade.rotation.x = (Math.random() - 0.5) * 0.3
          blade.rotation.z = (Math.random() - 0.5) * 0.3
          blade.rotation.y = Math.random() * Math.PI * 2
          
          blade.position.set(
            (Math.random() - 0.5) * 0.15,
            0,
            (Math.random() - 0.5) * 0.15
          )
          
          const s = 0.6 + Math.random() * 0.6
          blade.scale.set(s, s, s)
          blade.castShadow = true
          blade.receiveShadow = true
          cluster.add(blade)
        }
        
        const rx = xCenter + (Math.random() - 0.5) * xWidth
        const rz = (Math.random() - 0.5) * currentDepth
        cluster.position.set(rx, 0.02, rz)
        
        layerGroup.add(cluster)
        grass3DList.push(cluster)
      }
    }
    
    populateGrass3D(-11.8, 2.8, 120) // Césped Izquierdo
    populateGrass3D(0.0, 2.0, 60)     // Separador Central
    populateGrass3D(11.8, 2.8, 120)  // Césped Derecho
  }

  // --- Líneas de Demarcación Vial ---
  const clipLimit = currentDepth / 2
  const clipPlanes = [
    new THREE.Plane(new THREE.Vector3(0, 0, -1), clipLimit),
    new THREE.Plane(new THREE.Vector3(0, 0, 1), clipLimit)
  ]

  const lineMat = new THREE.MeshBasicMaterial({ color: 0xf8fafc, clippingPlanes: clipPlanes })

  roadDashes = []
  if (isC3S2) {
    // Cuatro líneas blancas discontinuas que delimitan el carril de circulación de las bermas laterales e internas (doble de largas)
    const whiteLinesX = [-8.8, -2.6, 2.6, 8.8]
    const whiteDashLength = 2.0
    const whiteDashGeom = new THREE.BoxGeometry(0.12, 0.002, whiteDashLength)
    const whiteDashMat = new THREE.MeshBasicMaterial({ color: 0xf8fafc, clippingPlanes: clipPlanes })
    
    // Spacing de 4.0 unidades para dividir exactamente a 36.0 (evita desfases en el horizonte)
    const whiteSpacing = 4.0
    const numWhiteDashes = Math.ceil(currentDepth / whiteSpacing) + 1
    const startOffset = -currentDepth / 2
    
    whiteLinesX.forEach(xPos => {
      for (let i = 0; i < numWhiteDashes; i++) {
        const dashMesh = new THREE.Mesh(whiteDashGeom, whiteDashMat)
        const startZ = startOffset + i * whiteSpacing
        dashMesh.position.set(xPos, 0.021, startZ) // Ligeramente encima de la grama si se solapa en el borde
        dashMesh.receiveShadow = true
        layerGroup.add(dashMesh)
        roadDashes.push(dashMesh)
      }
    })
  } else {
    // Eje simple/tándem: líneas laterales normales
    const lineOffset = currentWidth / 2 - 0.4
    const lineGeom = new THREE.BoxGeometry(0.12, 0.002, currentDepth)
    
    const lineLeftMesh = new THREE.Mesh(lineGeom, lineMat)
    lineLeftMesh.position.set(-lineOffset, 0.001, 0)
    lineLeftMesh.receiveShadow = true
    layerGroup.add(lineLeftMesh)

    const lineRightMesh = new THREE.Mesh(lineGeom, lineMat)
    lineRightMesh.position.set(lineOffset, 0.001, 0)
    lineRightMesh.receiveShadow = true
    layerGroup.add(lineRightMesh)
  }

  // --- Líneas Centrales Amarillas (Discontinuas y Sincronizadas - doble de largas) ---
  const dashLength = 1.0
  const dashGeom = new THREE.BoxGeometry(0.10, 0.002, dashLength)
  const dashMat = new THREE.MeshBasicMaterial({ color: 0xeab308, clippingPlanes: clipPlanes })
  
  // Spacing de 2.4 unidades para dividir exactamente a 36.0 (evita desfases en el horizonte)
  const yellowSpacing = 2.4
  const numDashes = Math.ceil(currentDepth / yellowSpacing) + 1
  const startOffset = -currentDepth / 2
  
  // No hay líneas amarillas para la doble calzada C3S2, solo para simple/tándem
  const centerOffsets = isC3S2 ? [] : [0]
  centerOffsets.forEach(cx => {
    for (let i = 0; i < numDashes; i++) {
      const dashMesh = new THREE.Mesh(dashGeom, dashMat)
      const startZ = startOffset + i * yellowSpacing
      dashMesh.position.set(cx, 0.001, startZ)
      dashMesh.receiveShadow = true
      layerGroup.add(dashMesh)
      roadDashes.push(dashMesh)
    }
  })

  // --- Señales de Tránsito Laterales (Reglamentarias) ---
  roadSigns = []
  
  // Dibujar 4 señales separadas el triple (30 unidades de separación: 15, -15, -45, -75)
  const signSpacing = isC3S2 ? [ 15, -15, -45, -75 ] : []
  
  const signBackMat = new THREE.MeshStandardMaterial({ color: 0xd1d5db, roughness: 0.4, metalness: 0.6 })
  const signEdgeMat = new THREE.MeshStandardMaterial({ color: 0xd1d5db, roughness: 0.4, metalness: 0.6 })
  
  const postGeom = new THREE.CylinderGeometry(0.04, 0.04, 2.7, 8)
  const postMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.4 })
  
  const discGeom = new THREE.CylinderGeometry(0.5, 0.5, 0.04, 24)
  discGeom.rotateX(Math.PI / 2) // Orientar de cara a la vía (eje Z)
  
  const signTextures = [
    textures.signSpeed30,
    textures.signPare,
    textures.signNoAdelantar,
    textures.signNoParquear,
    textures.signNoPase
  ]
  
  signSpacing.forEach((zOffset, i) => {
    const signGroup = new THREE.Group()
    signGroup.userData.isVerticalSign = true
    
    // Poste
    const postMesh = new THREE.Mesh(postGeom, postMat)
    postMesh.position.y = 1.35
    postMesh.castShadow = true
    postMesh.receiveShadow = true
    signGroup.add(postMesh)
    
    // Disco
    const faceTex = signTextures[i % signTextures.length]
    const signFaceMat = new THREE.MeshStandardMaterial({ map: faceTex, roughness: 0.2, metalness: 0.1 })
    const signMaterials = [signEdgeMat, signFaceMat, signBackMat]
    
    const discMesh = new THREE.Mesh(discGeom, signMaterials)
    discMesh.position.y = 3.2
    discMesh.castShadow = true
    discMesh.receiveShadow = true
    signGroup.add(discMesh)
    
    // Posicionar en la banquina derecha (apoyado en la grama en Y=0.02)
    const signX = 11.8
    signGroup.position.set(signX, 0.02, zOffset)
    
    layerGroup.add(signGroup)
    roadSigns.push(signGroup)
  })

  // --- Pórtico Transversal Elevado (Solo C3S2) ---
  if (isC3S2) {
    const gantryGroup = new THREE.Group()
    gantryGroup.userData.isGantry = true
    
    const metalMat = new THREE.MeshStandardMaterial({
      color: 0x94a3b8,
      roughness: 0.3,
      metalness: 0.8
    })
    
    const hazardMat = new THREE.MeshStandardMaterial({
      map: textures.hazardStripe,
      roughness: 0.5,
      metalness: 0.1
    })
    
    // Altura del pórtico aumentada en un 30% (Luz libre inferior a 7.2, columnas a 8.5)
    const postCylGeom = new THREE.CylinderGeometry(0.1, 0.1, 8.5, 12)
    const sleeveGeom = new THREE.CylinderGeometry(0.15, 0.15, 2.0, 12) // Camisa de protección escalada
    
    // Columna izquierda (desplazada a la nueva grama exterior en X = -11.8)
    const leftCol = new THREE.Mesh(postCylGeom, metalMat)
    leftCol.position.set(-11.8, 4.25, 0)
    leftCol.castShadow = true
    leftCol.receiveShadow = true
    gantryGroup.add(leftCol)
    
    const leftSleeve = new THREE.Mesh(sleeveGeom, hazardMat)
    leftSleeve.position.set(-11.8, 1.0, 0)
    leftSleeve.castShadow = true
    leftSleeve.receiveShadow = true
    gantryGroup.add(leftSleeve)
    
    // Columna derecha (desplazada a la nueva grama exterior en X = 11.8)
    const rightCol = new THREE.Mesh(postCylGeom, metalMat)
    rightCol.position.set(11.8, 4.25, 0)
    rightCol.castShadow = true
    rightCol.receiveShadow = true
    gantryGroup.add(rightCol)
    
    const rightSleeve = new THREE.Mesh(sleeveGeom, hazardMat)
    rightSleeve.position.set(11.8, 1.0, 0)
    rightSleeve.castShadow = true
    rightSleeve.receiveShadow = true
    gantryGroup.add(rightSleeve)
    
    // Viga horizontal superior (Y = 8.0, ensanchada a 23.6 unidades de largo)
    const topCordGeom = new THREE.CylinderGeometry(0.06, 0.06, 23.6, 8)
    topCordGeom.rotateZ(Math.PI / 2)
    const topCord = new THREE.Mesh(topCordGeom, metalMat)
    topCord.position.set(0, 8.0, 0)
    topCord.castShadow = true
    topCord.receiveShadow = true
    gantryGroup.add(topCord)
    
    // Viga horizontal inferior (Y = 7.2, ensanchada a 23.6 unidades de largo)
    const botCordGeom = new THREE.CylinderGeometry(0.06, 0.06, 23.6, 8)
    botCordGeom.rotateZ(Math.PI / 2)
    const botCord = new THREE.Mesh(botCordGeom, metalMat)
    botCord.position.set(0, 7.2, 0)
    botCord.castShadow = true
    botCord.receiveShadow = true
    gantryGroup.add(botCord)
    
    // Celosía horizontal (diagonales adaptadas a la luz de 23.6 unidades)
    const segs = 16
    const segWidth = 23.6 / segs
    for (let i = 0; i < segs; i++) {
      const x1 = -11.8 + i * segWidth
      const x2 = -11.8 + (i + 1) * segWidth
      const p1 = new THREE.Vector3(x1, (i % 2 === 0) ? 7.2 : 8.0, 0)
      const p2 = new THREE.Vector3(x2, (i % 2 === 0) ? 8.0 : 7.2, 0)
      
      const diagonalTube = createTubeBetweenPoints(p1, p2, 0.035, metalMat)
      gantryGroup.add(diagonalTube)
    }
    
    // Cartel Izquierdo: "Ibagué / Armenia" (X = -5.7, Y = 7.6)
    const signPlateGeom = new THREE.BoxGeometry(4.0, 1.8, 0.06)
    
    const signLeftFaceMat = new THREE.MeshStandardMaterial({
      map: textures.gantryLeft,
      roughness: 0.3,
      metalness: 0.1
    })
    const signLeftMaterials = [
      metalMat,
      metalMat,
      metalMat,
      metalMat,
      signLeftFaceMat,
      metalMat
    ]
    const signLeft = new THREE.Mesh(signPlateGeom, signLeftMaterials)
    signLeft.position.set(-5.7, 7.6, 0.08)
    signLeft.castShadow = true
    signLeft.receiveShadow = true
    gantryGroup.add(signLeft)
    
    // Cartel Derecho: "Espinal / Girardot" (X = 5.7, Y = 7.6)
    const signRightFaceMat = new THREE.MeshStandardMaterial({
      map: textures.gantryRight,
      roughness: 0.3,
      metalness: 0.1
    })
    const signRightMaterials = [
      metalMat,
      metalMat,
      metalMat,
      metalMat,
      signRightFaceMat,
      metalMat
    ]
    const signRight = new THREE.Mesh(signPlateGeom, signRightMaterials)
    signRight.position.set(5.7, 7.6, 0.08)
    signRight.castShadow = true
    signRight.receiveShadow = true
    gantryGroup.add(signRight)
    
    // Apoyado en la grama (posición Y = 0.02)
    gantryGroup.position.set(0, 0.02, 0)
    
    layerGroup.add(gantryGroup)
    roadSigns.push(gantryGroup)
  }
}

// Dibujar Eje Ruedas en 3D
function updateVehicle() {
  if (!vehicleGroup) return

  // Limpiar
  while (vehicleGroup.children.length > 0) {
    const obj = vehicleGroup.children[0]
    if (obj.geometry) obj.geometry.dispose()
    if (obj.material) {
      if (Array.isArray(obj.material)) {
        obj.material.forEach(m => m.dispose())
      } else {
        obj.material.dispose()
      }
    }
    vehicleGroup.remove(obj)
  }

  wheelsList = []
  hazardLights = []
  const isDouble = axleType.value === 'double'
  const isC3S2 = axleType.value === 'c3s2'
  const currentDepth = isC3S2 ? 22 : 5

  // Materiales...
  const tireTreadMat = new THREE.MeshStandardMaterial({ map: textures.tireTread, roughness: 0.8, metalness: 0.1 })
  const tireSidewallMat = new THREE.MeshStandardMaterial({ map: textures.tireSidewall, roughness: 0.8, metalness: 0.1 })
  const tireMaterials = [tireTreadMat, tireSidewallMat, tireSidewallMat]

  const rimFaceMat = new THREE.MeshStandardMaterial({ map: textures.rim, roughness: 0.3, metalness: 0.5 })
  const rimSideMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: 0.4, metalness: 0.8 })
  const rimMaterials = [rimSideMat, rimFaceMat, rimFaceMat]

  const hubMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.2, metalness: 0.9 })
  const axleMat = new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.3, metalness: 0.8 })

  const R_WHEEL = 0.90
  const TIRE_GEOM = new THREE.CylinderGeometry(R_WHEEL, R_WHEEL, 0.40, 32)
  TIRE_GEOM.rotateZ(Math.PI / 2)
  const RIM_GEOM = new THREE.CylinderGeometry(0.48, 0.48, 0.404, 24)
  RIM_GEOM.rotateZ(Math.PI / 2)

  const labelCanvas = document.createElement('canvas')
  labelCanvas.width = 256
  labelCanvas.height = 128
  const labelCtx = labelCanvas.getContext('2d')
  labelCtx.fillStyle = '#ef4444'
  labelCtx.beginPath()
  labelCtx.roundRect(8, 8, 240, 112, 16)
  labelCtx.fill()
  labelCtx.lineWidth = 6
  labelCtx.strokeStyle = '#ffffff'
  labelCtx.stroke()
  labelCtx.fillStyle = '#ffffff'
  labelCtx.font = 'bold 38px sans-serif'
  labelCtx.textAlign = 'center'
  labelCtx.textBaseline = 'middle'
  labelCtx.shadowColor = 'rgba(0, 0, 0, 0.5)'
  labelCtx.shadowBlur = 6
  labelCtx.shadowOffsetX = 2
  labelCtx.shadowOffsetY = 2
  labelCtx.fillText('8.2 Ton', 128, 64)
  const labelTex = new THREE.CanvasTexture(labelCanvas)
  const labelMat = new THREE.SpriteMaterial({ map: labelTex })

  function buildAxle(zPos, isSingleWheels = false, hideLabel = false) {
    const axleLength = isSingleWheels ? 5.2 : 6.0
    const axleGeom = new THREE.CylinderGeometry(0.12, 0.12, axleLength, 12)
    axleGeom.rotateZ(Math.PI / 2)
    const axleMesh = new THREE.Mesh(axleGeom, axleMat)
    axleMesh.position.set(0, R_WHEEL, zPos)
    axleMesh.castShadow = true
    vehicleGroup.add(axleMesh)

    const xOffsets = isSingleWheels ? [-2.5, 2.5] : [-2.85, -2.35, 2.35, 2.85]
    xOffsets.forEach((x, i) => {
      const tireMesh = new THREE.Mesh(TIRE_GEOM, tireMaterials)
      tireMesh.position.set(x, R_WHEEL, zPos)
      tireMesh.castShadow = true

      const rimMesh = new THREE.Mesh(RIM_GEOM, rimMaterials)
      rimMesh.castShadow = true
      tireMesh.add(rimMesh)

      const isOuter = isSingleWheels ? true : (i === 0 || i === 3)
      if (isOuter) {
        const hubGeom = new THREE.CylinderGeometry(0.18, 0.18, 0.05, 12)
        hubGeom.rotateZ(Math.PI / 2)
        const hubMesh = new THREE.Mesh(hubGeom, hubMat)
        hubMesh.position.set(i === 0 ? -0.19 : 0.19, 0, 0)
        tireMesh.add(hubMesh)
      }
      vehicleGroup.add(tireMesh)
      wheelsList.push(tireMesh)
    })

    if (!hideLabel) {
      const arrowGroup = new THREE.Group()
      const arrowMat = new THREE.MeshStandardMaterial({ color: 0xef4444, emissive: 0x991b1b, roughness: 0.15, metalness: 0.8 })
      const coneGeom = new THREE.ConeGeometry(0.22, 0.4, 16)
      const coneMesh = new THREE.Mesh(coneGeom, arrowMat)
      coneMesh.rotation.z = Math.PI
      coneMesh.position.y = 0.2
      coneMesh.castShadow = true
      arrowGroup.add(coneMesh)
      const shaftGeom = new THREE.CylinderGeometry(0.08, 0.08, 0.8, 16)
      const shaftMesh = new THREE.Mesh(shaftGeom, arrowMat)
      shaftMesh.position.y = 0.8
      shaftMesh.castShadow = true
      arrowGroup.add(shaftMesh)
      arrowGroup.position.set(0, R_WHEEL + 0.15, zPos)
      vehicleGroup.add(arrowGroup)

      const labelSprite = new THREE.Sprite(labelMat)
      labelSprite.scale.set(2.8, 1.4, 1)
      labelSprite.position.set(0, R_WHEEL + 1.6, zPos)
      vehicleGroup.add(labelSprite)
    }
  }

  if (isC3S2) {
    // Front Axle
    buildAxle(-7.5, true, true)
    
    // Tractor Tandem (Separado a 2.0 unidades para evitar superposición)
    buildAxle(-3.8, false, true)
    buildAxle(-1.8, false, true)

    // Trailer Tandem (Separado a 2.0 unidades para evitar superposición)
    buildAxle(6.5, false, true)
    buildAxle(8.5, false, true)

    // --- TRACTOCAMIÓN (CABEZOTE) ---
    // Chasis Tractor (Estructura base)
    const tBedGeom = new THREE.BoxGeometry(2.0, 0.4, 8.0)
    const tBedMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.6, metalness: 0.5 })
    const tBed = new THREE.Mesh(tBedGeom, tBedMat)
    tBed.position.set(0, R_WHEEL + 0.4, -4.0)
    tBed.castShadow = true
    vehicleGroup.add(tBed)

    // ── Materiales: azul acero plástico (toy/claymorphism – imagen de referencia) ──
    const cabColor = 0x5B9BD5
    const cabMat   = new THREE.MeshStandardMaterial({ color: cabColor, roughness: 0.28, metalness: 0.0 })
    const glassMat = new THREE.MeshStandardMaterial({ color: 0x0d1b2a, roughness: 0.05, metalness: 0.6, transparent: true, opacity: 0.90 })
    const chromeMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.1, metalness: 1.0 })
    const whiteMat  = new THREE.MeshStandardMaterial({ color: 0xf0f4f8, roughness: 0.30, metalness: 0.0 })
    const grilleMat = new THREE.MeshStandardMaterial({ color: 0x1a2433, roughness: 0.75, metalness: 0.15 })
    const toyRimMat = new THREE.MeshStandardMaterial({ color: 0xdde3ea, roughness: 0.30, metalness: 0.0 })

    // Cabina Principal (proporciones toy – imagen de referencia)
    const cabGeom = new THREE.BoxGeometry(3.6, 3.6, 3.8)
    const cab = new THREE.Mesh(cabGeom, cabMat)
    cab.position.set(0, 1.3 + 1.80, -4.1)
    cab.castShadow = true
    vehicleGroup.add(cab)

    // Redondeo del techo (borde superior frontal)
    const cabRoofEdgeGeom = new THREE.CylinderGeometry(0.28, 0.28, 3.6, 16, 1, false, 0, Math.PI)
    cabRoofEdgeGeom.rotateZ(Math.PI / 2)
    const cabRoofEdge = new THREE.Mesh(cabRoofEdgeGeom, cabMat)
    cabRoofEdge.position.set(0, 1.3 + 3.60, -6.00)
    cabRoofEdge.castShadow = true
    vehicleGroup.add(cabRoofEdge)

    // Trompa (Capó) – compacta, toy
    const hoodGeom = new THREE.BoxGeometry(3.1, 1.75, 1.7)
    const hood = new THREE.Mesh(hoodGeom, cabMat)
    hood.position.set(0, 1.3 + 0.875, -7.0)
    hood.castShadow = true
    vehicleGroup.add(hood)

    // Arista superior redondeada del capó
    const hoodCurveGeom = new THREE.CylinderGeometry(0.28, 0.28, 3.1, 16, 1, false, -Math.PI / 2, Math.PI)
    hoodCurveGeom.rotateZ(Math.PI / 2)
    const hoodCurve = new THREE.Mesh(hoodCurveGeom, cabMat)
    hoodCurve.position.set(0, 1.3 + 1.75, -7.82)
    hoodCurve.castShadow = true
    vehicleGroup.add(hoodCurve)

    // Zona inferior frontal blanca (entre rejilla y parachoques)
    const noseLowerGeom = new THREE.BoxGeometry(3.1, 0.50, 0.20)
    const noseLower = new THREE.Mesh(noseLowerGeom, whiteMat)
    noseLower.position.set(0, 1.3 + 0.25, -7.96)
    noseLower.castShadow = true
    vehicleGroup.add(noseLower)

    // Rejilla frontal oscura (fondo oscuro + barras cromadas)
    const grilleBackGeom = new THREE.BoxGeometry(2.7, 1.40, 0.10)
    const grilleBack = new THREE.Mesh(grilleBackGeom, grilleMat)
    grilleBack.position.set(0, 2.20, -7.91)
    grilleBack.castShadow = true
    vehicleGroup.add(grilleBack)
    const gBarGeom = new THREE.BoxGeometry(0.07, 1.30, 0.08)
    for (let bx = -1.1; bx <= 1.1; bx += 0.37) {
      const bar = new THREE.Mesh(gBarGeom, chromeMat)
      bar.position.set(bx, 2.20, -7.85)
      vehicleGroup.add(bar)
    }

    // Parachoques delantero – blanco, prominente (imagen de referencia)
    const bumperGeom = new THREE.BoxGeometry(3.5, 0.55, 0.40)
    const bumper = new THREE.Mesh(bumperGeom, whiteMat)
    bumper.position.set(0, 1.3 - 0.28, -7.90)
    bumper.castShadow = true
    vehicleGroup.add(bumper)

    // Guardabarros delanteros curvos (azul, igual que cabina)
    const fenderGeom = new THREE.TorusGeometry(1.05, 0.14, 8, 14, Math.PI)
    fenderGeom.rotateY(Math.PI / 2)
    const leftFender = new THREE.Mesh(fenderGeom, cabMat)
    leftFender.position.set(-2.55, R_WHEEL, -7.5)
    leftFender.castShadow = true
    vehicleGroup.add(leftFender)
    const rightFender = new THREE.Mesh(fenderGeom, cabMat)
    rightFender.position.set(2.55, R_WHEEL, -7.5)
    rightFender.castShadow = true
    vehicleGroup.add(rightFender)

    // Visera solar (azul)
    const visorGeom = new THREE.BoxGeometry(3.4, 0.18, 0.45)
    const visor = new THREE.Mesh(visorGeom, cabMat)
    visor.position.set(0, 1.3 + 3.48, -6.10)
    visor.rotation.x = Math.PI / 10
    vehicleGroup.add(visor)

    // Parabrisas grande (imagen: ocupa casi toda la cara frontal de la cabina)
    const windGeom = new THREE.PlaneGeometry(3.15, 1.80)
    const wind = new THREE.Mesh(windGeom, glassMat)
    wind.position.set(0, 1.3 + 2.70, -6.02)
    wind.rotation.y = Math.PI
    vehicleGroup.add(wind)

    // Espejos laterales blancos prominentes
    const mirrorArmGeom = new THREE.BoxGeometry(0.55, 0.08, 0.08)
    const mirrorFaceGeom = new THREE.BoxGeometry(0.12, 0.50, 0.30)
    const mirrorLA = new THREE.Mesh(mirrorArmGeom, whiteMat)
    mirrorLA.position.set(-2.08, 1.3 + 2.85, -6.25)
    vehicleGroup.add(mirrorLA)
    const mirrorLF = new THREE.Mesh(mirrorFaceGeom, whiteMat)
    mirrorLF.position.set(-2.35, 1.3 + 2.85, -6.25)
    vehicleGroup.add(mirrorLF)
    const mirrorRA = new THREE.Mesh(mirrorArmGeom, whiteMat)
    mirrorRA.position.set(2.08, 1.3 + 2.85, -6.25)
    vehicleGroup.add(mirrorRA)
    const mirrorRF = new THREE.Mesh(mirrorFaceGeom, whiteMat)
    mirrorRF.position.set(2.35, 1.3 + 2.85, -6.25)
    vehicleGroup.add(mirrorRF)

    // Vidrios laterales
    const sideWinGeom = new THREE.PlaneGeometry(1.45, 1.55)
    const winLeft = new THREE.Mesh(sideWinGeom, glassMat)
    winLeft.position.set(-1.81, 1.3 + 2.55, -4.60)
    winLeft.rotation.y = -Math.PI / 2
    vehicleGroup.add(winLeft)
    const winRight = new THREE.Mesh(sideWinGeom, glassMat)
    winRight.position.set(1.81, 1.3 + 2.55, -4.60)
    winRight.rotation.y = Math.PI / 2
    vehicleGroup.add(winRight)

    // Chimeneas de escape cromadas
    function createExhaust(xOff) {
      const g = new THREE.Group()
      const pGeom = new THREE.CylinderGeometry(0.08, 0.08, 3.8, 12)
      const p = new THREE.Mesh(pGeom, chromeMat)
      p.position.set(xOff, 3.2, -3.5)
      p.castShadow = true
      g.add(p)
      const elbGeom = new THREE.CylinderGeometry(0.08, 0.08, 0.5, 12)
      elbGeom.rotateX(Math.PI / 4)
      const elb = new THREE.Mesh(elbGeom, chromeMat)
      elb.position.set(xOff, 5.12, -3.62)
      g.add(elb)
      return g
    }
    vehicleGroup.add(createExhaust(-1.95))
    vehicleGroup.add(createExhaust(1.95))

    // Tanques de combustible laterales (azul cabina)
    const tankGeom = new THREE.CylinderGeometry(0.44, 0.44, 1.6, 16)
    tankGeom.rotateZ(Math.PI / 2)
    const tankLeft = new THREE.Mesh(tankGeom, cabMat)
    tankLeft.position.set(-1.42, 1.0, -4.7)
    tankLeft.castShadow = true
    vehicleGroup.add(tankLeft)
    const tankRight = new THREE.Mesh(tankGeom, cabMat)
    tankRight.position.set(1.42, 1.0, -4.7)
    tankRight.castShadow = true
    vehicleGroup.add(tankRight)

    // Quinta rueda
    const fwGeom = new THREE.CylinderGeometry(0.8, 0.8, 0.1, 16)
    const fw = new THREE.Mesh(fwGeom, new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.8 }))
    fw.position.set(0, 1.55, -2.25)
    vehicleGroup.add(fw)

    // Guardabarros traseros del tractor (azul)
    vehicleGroup.add(createTandemFender(-2.8, -2.6, cabMat, R_WHEEL))
    vehicleGroup.add(createTandemFender(-2.8, 2.6, cabMat, R_WHEEL))

    // Luces demarcadoras: 5 puntos dorados en el techo (imagen de referencia)
    const markerLightGeom = new THREE.CylinderGeometry(0.075, 0.075, 0.06, 10)
    markerLightGeom.rotateX(Math.PI / 2)
    const markerLightMat = new THREE.MeshBasicMaterial({ color: 0xf5c518 })
    const xOffsetsLights = [-1.2, -0.6, 0, 0.6, 1.2]
    xOffsetsLights.forEach(x => {
      const light = new THREE.Mesh(markerLightGeom, markerLightMat)
      light.position.set(x, 1.3 + 3.66, -6.02)
      vehicleGroup.add(light)
    })

    // Faros delanteros rectangulares blancos
    const lightGeom = new THREE.BoxGeometry(0.55, 0.32, 0.08)
    const lightMat = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xfff8e1, emissiveIntensity: 1.5, roughness: 0.1 })
    const headlightL = new THREE.Mesh(lightGeom, lightMat)
    headlightL.position.set(-1.28, 1.3 + 0.55, -7.94)
    vehicleGroup.add(headlightL)
    const headlightR = new THREE.Mesh(lightGeom, lightMat)
    headlightR.position.set(1.28, 1.3 + 0.55, -7.94)
    vehicleGroup.add(headlightR)

    // Fuentes de luz reales (faros de luz) apuntando hacia adelante (-Z)
    const spotLightL = new THREE.SpotLight(0xfffae0, 35.0, 50.0, Math.PI / 6, 0.5, 1.0)
    spotLightL.position.set(-1.28, 1.3 + 0.55, -7.94)
    const targetL = new THREE.Object3D()
    targetL.position.set(-1.28, 1.3 + 0.55, -35.0)
    vehicleGroup.add(targetL)
    spotLightL.target = targetL
    spotLightL.castShadow = true
    spotLightL.shadow.mapSize.width = 512
    spotLightL.shadow.mapSize.height = 512
    spotLightL.shadow.camera.near = 0.5
    spotLightL.shadow.camera.far = 40
    vehicleGroup.add(spotLightL)

    const spotLightR = new THREE.SpotLight(0xfffae0, 35.0, 50.0, Math.PI / 6, 0.5, 1.0)
    spotLightR.position.set(1.28, 1.3 + 0.55, -7.94)
    const targetR = new THREE.Object3D()
    targetR.position.set(1.28, 1.3 + 0.55, -35.0)
    vehicleGroup.add(targetR)
    spotLightR.target = targetR
    spotLightR.castShadow = true
    spotLightR.shadow.mapSize.width = 512
    spotLightR.shadow.mapSize.height = 512
    spotLightR.shadow.camera.near = 0.5
    spotLightR.shadow.camera.far = 40
    vehicleGroup.add(spotLightR)

    // Rines blancos toy sobre las ruedas del tractor y remolque
    wheelsList.forEach(tireMesh => {
      tireMesh.children.forEach(child => {
        if (!child.isMesh) return
        const newMat = toyRimMat.clone()
        if (Array.isArray(child.material)) {
          child.material = child.material.map(() => newMat)
        } else {
          child.material = newMat
        }
      })
    })

    // --- SEMIRREMOLQUE (FURGÓN) ---
    // Plataforma del remolque (azul tenue)
    const pBedGeom = new THREE.BoxGeometry(4.1, 0.30, 12.5)
    const pBedMat = new THREE.MeshStandardMaterial({ color: 0x3a6ea5, roughness: 0.55, metalness: 0.0 })
    const pBed = new THREE.Mesh(pBedGeom, pBedMat)
    pBed.position.set(0, 1.75, 3.875)
    pBed.castShadow = true
    vehicleGroup.add(pBed)

    // Caja de carga – Contenedor marítimo naranja-rojo (HAMBURG)
    const rightSideMat = new THREE.MeshStandardMaterial({
      map: textures.containerSideRight,
      bumpMap: textures.containerSideBump,
      bumpScale: 0.06,
      roughness: 0.5,
      metalness: 0.2
    })
    
    const leftSideMat = new THREE.MeshStandardMaterial({
      map: textures.containerSideLeft,
      bumpMap: textures.containerSideBump,
      bumpScale: 0.06,
      roughness: 0.5,
      metalness: 0.2
    })
    
    const plainOrangeMat = new THREE.MeshStandardMaterial({
      color: 0xd03d25,
      roughness: 0.5,
      metalness: 0.2
    })
    
    const backDoorMat = new THREE.MeshStandardMaterial({
      map: textures.containerDoor,
      roughness: 0.5,
      metalness: 0.3
    })
    
    const frontFaceMat = new THREE.MeshStandardMaterial({
      map: textures.containerFront,
      bumpMap: textures.containerFrontBump,
      bumpScale: 0.06,
      roughness: 0.5,
      metalness: 0.2
    })
    
    const containerMaterials = [
      rightSideMat,    // +X (Right side)
      leftSideMat,     // -X (Left side)
      plainOrangeMat,  // +Y (Top)
      plainOrangeMat,  // -Y (Bottom)
      backDoorMat,     // +Z (Back door)
      frontFaceMat     // -Z (Front face)
    ]
    
    const boxGeom = new THREE.BoxGeometry(4.1, 4.5, 12.5)
    const cargoBox = new THREE.Mesh(boxGeom, containerMaterials)
    cargoBox.position.set(0, 1.90 + 2.25, 3.875)
    cargoBox.castShadow = true
    vehicleGroup.add(cargoBox)

    // Guardabarros traseros del remolque (azul)
    vehicleGroup.add(createTandemFender(7.5, -2.6, cabMat, R_WHEEL))
    vehicleGroup.add(createTandemFender(7.5, 2.6, cabMat, R_WHEEL))

    // Soportes del remolque (Landing Gear) en Z = -1.0
    const legGeom = new THREE.CylinderGeometry(0.08, 0.08, 1.2, 8)
    const legMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8 })
    
    const legLeft = new THREE.Mesh(legGeom, legMat)
    legLeft.position.set(-1.2, 1.15, -1.0)
    legLeft.castShadow = true
    vehicleGroup.add(legLeft)
    
    const legRight = new THREE.Mesh(legGeom, legMat)
    legRight.position.set(1.2, 1.15, -1.0)
    legRight.castShadow = true
    vehicleGroup.add(legRight)
    
    const footGeom = new THREE.BoxGeometry(0.3, 0.1, 0.3)
    const footLeft = new THREE.Mesh(footGeom, legMat)
    footLeft.position.set(-1.2, 0.55, -1.0)
    vehicleGroup.add(footLeft)
    const footRight = new THREE.Mesh(footGeom, legMat)
    footRight.position.set(1.2, 0.55, -1.0)
    vehicleGroup.add(footRight)

    const crossGeom = new THREE.CylinderGeometry(0.04, 0.04, 2.4, 8)
    crossGeom.rotateZ(Math.PI / 2)
    const crossBar = new THREE.Mesh(crossGeom, legMat)
    crossBar.position.set(0, 1.15, -1.0)
    vehicleGroup.add(crossBar)

    // Cinta reflectiva blanca y roja en los laterales inferiores del contenedor
    const tapeGeom = new THREE.BoxGeometry(0.01, 0.08, 12.4)
    const tapeMat = new THREE.MeshBasicMaterial({ color: 0xf8fafc })
    
    const tapeL = new THREE.Mesh(tapeGeom, tapeMat)
    tapeL.position.set(-2.01, 1.65, 3.875)
    vehicleGroup.add(tapeL)
    
    const tapeR = new THREE.Mesh(tapeGeom, tapeMat)
    tapeR.position.set(2.01, 1.65, 3.875)
    vehicleGroup.add(tapeR)

    const redSegGeom = new THREE.BoxGeometry(0.012, 0.08, 0.2)
    const redSegMat = new THREE.MeshBasicMaterial({ color: 0xef4444 })
    for (let z = -2.2; z <= 10.0; z += 1.0) {
      const segL = new THREE.Mesh(redSegGeom, redSegMat)
      segL.position.set(-2.015, 1.65, z)
      vehicleGroup.add(segL)

      const segR = new THREE.Mesh(redSegGeom, redSegMat)
      segR.position.set(2.015, 1.65, z)
      vehicleGroup.add(segR)
    }

    // Mangueras conectoras en espiral (Roja y Azul) entre cabina y remolque
    const numTurns = 8
    const radius = 0.15
    const pointsCount = 60
    for (let i = 0; i < pointsCount; i++) {
      const t = i / pointsCount
      const angle = t * numTurns * Math.PI * 2
      const x = Math.cos(angle) * radius
      const y = Math.sin(angle) * radius
      const z = -3.4 + t * 0.95 // de -3.4 a -2.45 en Z
      
      // Manguera Roja (Freno)
      const redDotGeom = new THREE.SphereGeometry(0.026, 4, 4)
      const redDotMat = new THREE.MeshBasicMaterial({ color: 0xef4444 })
      const redDot = new THREE.Mesh(redDotGeom, redDotMat)
      redDot.position.set(x - 0.2, y + 1.8, z)
      vehicleGroup.add(redDot)
      
      // Manguera Azul (Servicio)
      const blueDotGeom = new THREE.SphereGeometry(0.026, 4, 4)
      const blueDotMat = new THREE.MeshBasicMaterial({ color: 0x3b82f6 })
      const blueDot = new THREE.Mesh(blueDotGeom, blueDotMat)
      blueDot.position.set(x + 0.2, y + 1.8, z)
      vehicleGroup.add(blueDot)
    }

    // Luces Traseras Circulares en el remolque (Rojas y Naranjas)
    const lightSphereGeom = new THREE.SphereGeometry(0.08, 8, 8)
    const amberLightMat = new THREE.MeshBasicMaterial({ color: 0xf97316 })
    const redLightMat = new THREE.MeshBasicMaterial({ color: 0xef4444 })
    
    // Luces izquierdas
    const l1 = new THREE.Mesh(lightSphereGeom, redLightMat)
    l1.position.set(-1.6, 1.75, 10.14)
    vehicleGroup.add(l1)
    const l2 = new THREE.Mesh(lightSphereGeom, amberLightMat)
    l2.position.set(-1.3, 1.75, 10.14)
    vehicleGroup.add(l2)
    hazardLights.push(l2)
    
    // Luces derechas
    const r1 = new THREE.Mesh(lightSphereGeom, redLightMat)
    r1.position.set(1.6, 1.75, 10.14)
    vehicleGroup.add(r1)
    const r2 = new THREE.Mesh(lightSphereGeom, amberLightMat)
    r2.position.set(1.3, 1.75, 10.14)
    vehicleGroup.add(r2)
    hazardLights.push(r2)

    camera.position.set(21.7, 11, 20) // Alejar y desplazar cámara para ver todo el camión majestuoso centrado
  } else if (isDouble) {
    buildAxle(-1.35)
    buildAxle(1.35)
    const linkGeom = new THREE.BoxGeometry(0.15, 0.26, 3.0)
    const linkLeft = new THREE.Mesh(linkGeom, axleMat)
    linkLeft.position.set(-2.0, R_WHEEL, 0)
    linkLeft.castShadow = true
    vehicleGroup.add(linkLeft)
    const linkRight = new THREE.Mesh(linkGeom, axleMat)
    linkRight.position.set(2.0, R_WHEEL, 0)
    linkRight.castShadow = true
    vehicleGroup.add(linkRight)
    
    camera.position.set(9, 7, 10.5) // Restaurar cámara
  } else {
    buildAxle(0)
    camera.position.set(9, 7, 10.5) // Restaurar cámara
  }

  // Centrar el camión y el OrbitControls en el carril derecho si es C3S2 (en X = 5.7)
  if (isC3S2) {
    vehicleGroup.position.x = 5.7
    if (controls) {
      controls.target.set(5.7, 0, 0)
    }
  } else {
    vehicleGroup.position.x = 0
    if (controls) {
      controls.target.set(0, 0, 0)
    }
  }

  // --- Dibujar los Bulbos de Presiones ---
  if (showStressBulb.value && results.value && !isC3S2) {
    const capas = results.value.capas
    let yTotal = 0
    capas.forEach(c => { yTotal += c.cm * SCALE_Y })
    const subH = 1.5
    yTotal += subH

    const SN = results.value.SNT[2] || 3.0
    const stressCanvas = document.createElement('canvas')
    stressCanvas.width = 512
    stressCanvas.height = 256
    drawStressBulbSide(stressCanvas, 512, 256, capas, SN)
    const stressTex = new THREE.CanvasTexture(stressCanvas)
    const stressMat = new THREE.MeshBasicMaterial({
      map: stressTex, transparent: true, opacity: 0.95, side: THREE.DoubleSide, depthWrite: false
    })

    const planeGeom = new THREE.PlaneGeometry(currentDepth, yTotal)
    const rightPlane = new THREE.Mesh(planeGeom, stressMat)
    rightPlane.position.set(3.501, -yTotal / 2, 0)
    rightPlane.rotation.y = Math.PI / 2
    vehicleGroup.add(rightPlane)

    const leftPlane = new THREE.Mesh(planeGeom, stressMat)
    leftPlane.position.set(-3.501, -yTotal / 2, 0)
    leftPlane.rotation.y = -Math.PI / 2
    vehicleGroup.add(leftPlane)
  }
}

// Dibujar flecha indicadora de esfuerzo vertical en el canvas
function drawStressArrow(ctx, x, yStart, yEnd) {
  ctx.beginPath()
  ctx.moveTo(x, yStart)
  ctx.lineTo(x, yEnd)
  ctx.stroke()
  
  ctx.beginPath()
  ctx.moveTo(x - 3.5, yEnd - 5)
  ctx.lineTo(x, yEnd)
  ctx.lineTo(x + 3.5, yEnd - 5)
  ctx.stroke()
}

// Dibujar bulbo lateral tipo campana de esfuerzos con flechas descendentes
function drawStressBulbSide(canvas, width, height, capas, SN) {
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, width, height)
  
  // Dibujar líneas divisoras de capas en el lateral
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'
  ctx.lineWidth = 1.5
  
  const totalCm = capas.reduce((acc, c) => acc + c.cm, 0) + 120 // 120 cm de subrasante
  
  let accCm = 0
  capas.forEach(capa => {
    accCm += capa.cm
    const yPixel = (accCm / totalCm) * height
    ctx.beginPath()
    ctx.setLineDash([6, 4])
    ctx.moveTo(0, yPixel)
    ctx.lineTo(width, yPixel)
    ctx.stroke()
  })
  ctx.setLineDash([]) // Restaurar

  // Factores de deformación del bulbo por el SN (rigidez)
  const depthFactor = Math.max(0.4, 1.2 - SN * 0.12)
  const widthFactor = Math.min(1.8, 0.8 + SN * 0.15)
  
  // Centros de los bulbos según eje (Z = 0 para simple, Z = ±1.35 para doble)
  const isDouble = axleType.value === 'double'
  const centers = isDouble
    ? [
        256 - (1.35 / 2.5) * 256, // Eje trasero (-1.35) -> px 118
        256 + (1.35 / 2.5) * 256  // Eje delantero (1.35) -> px 394
      ]
    : [256] // Eje simple -> px 256
    
  centers.forEach(cz => {
    const rx = 80 * widthFactor
    const ry = 180 * depthFactor
    const w_load = 36
    
    // Relleno de campana degradada
    const grad = ctx.createLinearGradient(cz, 0, cz, ry)
    grad.addColorStop(0, 'rgba(239, 68, 68, 0.55)') // Rojo en la superficie
    grad.addColorStop(0.5, 'rgba(249, 115, 22, 0.35)') // Naranja medio
    grad.addColorStop(1, 'rgba(234, 179, 8, 0.05)') // Amarillo desvanecido abajo
    
    ctx.fillStyle = grad
    ctx.strokeStyle = '#ef4444' // Contorno rojo
    ctx.lineWidth = 2
    
    ctx.beginPath()
    ctx.moveTo(cz - w_load/2, 0)
    ctx.bezierCurveTo(cz - rx, ry * 0.35, cz - rx * 0.5, ry * 0.8, cz, ry)
    ctx.bezierCurveTo(cz + rx * 0.5, ry * 0.8, cz + rx, ry * 0.35, cz + w_load/2, 0)
    ctx.closePath()
    ctx.fill()
    ctx.stroke()
    
    // Flechas de esfuerzo verticales (estilo imagen de referencia)
    ctx.strokeStyle = '#0f172a' // Color de flechas oscuras
    ctx.lineWidth = 1.5
    
    // Flecha central (la más larga)
    drawStressArrow(ctx, cz, 8, ry - 16)
    
    // Flechas laterales intermedias
    const offset1 = rx * 0.35
    drawStressArrow(ctx, cz - offset1, 8, ry * 0.65 - 10)
    drawStressArrow(ctx, cz + offset1, 8, ry * 0.65 - 10)
    
    // Flechas laterales externas (las más cortas)
    const offset2 = rx * 0.65
    drawStressArrow(ctx, cz - offset2, 8, ry * 0.30 - 6)
    drawStressArrow(ctx, cz + offset2, 8, ry * 0.30 - 6)
  })
}

// Reactores
watch(() => results.value, () => {
  updatePavement()
  updateVehicle()
}, { deep: true })

watch(axleType, () => {
  updatePavement()
  updateVehicle()
})

watch(showStressBulb, () => {
  updatePavement()
  updateVehicle()
})

onMounted(() => {
  initThree()
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  cancelAnimationFrame(animId)
  if (renderer) {
    renderer.dispose()
  }
})

function disposeObject3D(obj) {
  if (obj.geometry) obj.geometry.dispose()
  if (obj.material) {
    if (Array.isArray(obj.material)) {
      obj.material.forEach(m => m.dispose())
    } else {
      obj.material.dispose()
    }
  }
  if (obj.children) {
    obj.children.forEach(child => disposeObject3D(child))
  }
}
</script>
