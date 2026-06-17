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
  const ROAD_SPEED = 0.036
  const DEPTH_3D_VAL = 5.0

  // Bucle de animación (con rotación de ruedas en su plano y simulación de movimiento de carretera)
  function animate() {
    animId = requestAnimationFrame(animate)
    
    const isC3S2 = axleType.value === 'c3s2'
    const currentDepth = isC3S2 ? 35 : 5

    // 1. Rotar los neumáticos respecto a su centro en el eje X
    wheelsList.forEach(wheel => {
      wheel.rotation.x -= 0.04
    })

    // 2. Desplazar la textura del asfalto en V (eje Y del canvas) para simular movimiento
    if (textures.asphalt) {
      textures.asphalt.offset.y -= ROAD_SPEED / currentDepth
    }

    // 3. Desplazar los guiones amarillos centrales en el eje Z
    roadDashes.forEach(dash => {
      dash.position.z += ROAD_SPEED
      const limit = currentDepth / 2 + 0.25
      if (dash.position.z > limit) {
        // Enviar al principio (borde trasero)
        dash.position.z -= (currentDepth + 0.5)
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
    obj.geometry.dispose()
    if (obj.material) obj.material.dispose()
    layerGroup.remove(obj)
  }

  if (!results.value) return

  const isC3S2 = axleType.value === 'c3s2'
  const currentDepth = isC3S2 ? 35 : 5
  const currentWidth = isC3S2 ? 10 : 7

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

  // --- Líneas de Demarcación Vial ---
  const clipLimit = currentDepth / 2
  const clipPlanes = [
    new THREE.Plane(new THREE.Vector3(0, 0, -1), clipLimit),
    new THREE.Plane(new THREE.Vector3(0, 0, 1), clipLimit)
  ]

  const lineOffset = currentWidth / 2 - 0.4 // Líneas blancas en los bordes

  // 1. Línea Blanca Lateral Izquierda
  const lineLeftGeom = new THREE.BoxGeometry(0.12, 0.002, currentDepth)
  const lineLeftMat = new THREE.MeshBasicMaterial({ color: 0xf8fafc, clippingPlanes: clipPlanes })
  const lineLeftMesh = new THREE.Mesh(lineLeftGeom, lineLeftMat)
  lineLeftMesh.position.set(-lineOffset, 0.001, 0)
  lineLeftMesh.receiveShadow = true
  layerGroup.add(lineLeftMesh)

  // 2. Línea Blanca Lateral Derecha
  const lineRightGeom = new THREE.BoxGeometry(0.12, 0.002, currentDepth)
  const lineRightMat = new THREE.MeshBasicMaterial({ color: 0xf8fafc, clippingPlanes: clipPlanes })
  const lineRightMesh = new THREE.Mesh(lineRightGeom, lineRightMat)
  lineRightMesh.position.set(lineOffset, 0.001, 0)
  lineRightMesh.receiveShadow = true
  layerGroup.add(lineRightMesh)

  // 3. Líneas Centrales Amarillas (Múltiples si es más ancho)
  roadDashes = []
  const dashLength = 0.5
  const dashGeom = new THREE.BoxGeometry(0.10, 0.002, dashLength)
  const dashMat = new THREE.MeshBasicMaterial({ color: 0xeab308, clippingPlanes: clipPlanes })
  
  const numDashes = Math.ceil(currentDepth / 1.1) + 1
  const startOffset = -currentDepth / 2
  
  // Si es C3S2 (doble de ancho), añadimos dos carriles de guiones amarillos
  const centerOffsets = isC3S2 ? [-1.6, 1.6] : [0]
  
  centerOffsets.forEach(cx => {
    for (let i = 0; i < numDashes; i++) {
      const dashMesh = new THREE.Mesh(dashGeom, dashMat)
      const startZ = startOffset + i * 1.1
      dashMesh.position.set(cx, 0.001, startZ)
      dashMesh.receiveShadow = true
      layerGroup.add(dashMesh)
      roadDashes.push(dashMesh)
    }
  })
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
    
    // Tractor Tandem
    buildAxle(-3.0, false, true)
    buildAxle(-1.5, false, true)

    // Trailer Tandem
    buildAxle(4.5, false, true)
    buildAxle(6.0, false, true)

    // --- TRACTOCAMIÓN (CABEZOTE) ---
    // Chasis Tractor (Estructura base)
    const tBedGeom = new THREE.BoxGeometry(2.0, 0.4, 8.0)
    const tBedMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.6, metalness: 0.5 })
    const tBed = new THREE.Mesh(tBedGeom, tBedMat)
    tBed.position.set(0, R_WHEEL + 0.4, -4.0)
    tBed.castShadow = true
    vehicleGroup.add(tBed)

    // Materiales comunes de cabina
    const cabColor = 0xb91c1c // Rojo cereza oscuro brillante
    const cabMat = new THREE.MeshStandardMaterial({ color: cabColor, roughness: 0.2, metalness: 0.4 })
    const glassMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.1, metalness: 0.9 })
    const chromeMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.1, metalness: 1.0 })

    // Cabina Principal
    const cabGeom = new THREE.BoxGeometry(3.5, 3.5, 2.5)
    const cab = new THREE.Mesh(cabGeom, cabMat)
    cab.position.set(0, 1.3 + 1.75, -4.75)
    cab.castShadow = true
    vehicleGroup.add(cab)

    // Trompa (Capó)
    const hoodGeom = new THREE.BoxGeometry(3.0, 1.8, 1.8)
    const hood = new THREE.Mesh(hoodGeom, cabMat)
    hood.position.set(0, 1.3 + 0.9, -6.9)
    hood.castShadow = true
    vehicleGroup.add(hood)

    // Persiana (Grill) Cromada
    const grillGeom = new THREE.PlaneGeometry(2.6, 1.5)
    const grill = new THREE.Mesh(grillGeom, chromeMat)
    grill.position.set(0, 2.2, -7.81)
    grill.rotation.y = Math.PI
    vehicleGroup.add(grill)

    // Parabrisas
    const windGeom = new THREE.PlaneGeometry(3.1, 1.4)
    const wind = new THREE.Mesh(windGeom, glassMat)
    wind.position.set(0, 3.8, -6.01)
    wind.rotation.y = Math.PI
    vehicleGroup.add(wind)

    // Vidrios Laterales
    const sideWinGeom = new THREE.PlaneGeometry(1.4, 1.4)
    const winLeft = new THREE.Mesh(sideWinGeom, glassMat)
    winLeft.position.set(-1.76, 3.8, -4.75)
    winLeft.rotation.y = -Math.PI / 2
    vehicleGroup.add(winLeft)
    const winRight = new THREE.Mesh(sideWinGeom, glassMat)
    winRight.position.set(1.76, 3.8, -4.75)
    winRight.rotation.y = Math.PI / 2
    vehicleGroup.add(winRight)

    // Chimeneas (Escapes Verticales)
    const exhaustGeom = new THREE.CylinderGeometry(0.12, 0.12, 4.5, 12)
    const exLeft = new THREE.Mesh(exhaustGeom, chromeMat)
    exLeft.position.set(-2.0, 3.5, -3.4)
    exLeft.castShadow = true
    vehicleGroup.add(exLeft)
    const exRight = new THREE.Mesh(exhaustGeom, chromeMat)
    exRight.position.set(2.0, 3.5, -3.4)
    exRight.castShadow = true
    vehicleGroup.add(exRight)

    // Tanques de Combustible (Laterales cilíndricos)
    const tankGeom = new THREE.CylinderGeometry(0.45, 0.45, 1.6, 16)
    tankGeom.rotateZ(Math.PI / 2)
    const tankLeft = new THREE.Mesh(tankGeom, chromeMat)
    tankLeft.position.set(-1.4, 1.0, -4.7)
    tankLeft.castShadow = true
    vehicleGroup.add(tankLeft)
    const tankRight = new THREE.Mesh(tankGeom, chromeMat)
    tankRight.position.set(1.4, 1.0, -4.7)
    tankRight.castShadow = true
    vehicleGroup.add(tankRight)

    // Quinta Rueda (Acople del remolque)
    const fwGeom = new THREE.CylinderGeometry(0.8, 0.8, 0.1, 16)
    const fw = new THREE.Mesh(fwGeom, new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.8 }))
    fw.position.set(0, 1.55, -2.25)
    vehicleGroup.add(fw)

    // Guardabarros Traseros (Tractocamión)
    const mudMat = new THREE.MeshStandardMaterial({ color: 0x0a0a0a, roughness: 0.9 })
    const mudTractorGeom = new THREE.BoxGeometry(4.0, 1.0, 0.05)
    const mudTractor = new THREE.Mesh(mudTractorGeom, mudMat)
    mudTractor.position.set(0, 0.8, -0.6)
    vehicleGroup.add(mudTractor)

    // --- SEMIRREMOLQUE (FURGÓN) ---
    // Plataforma del Remolque
    const pBedGeom = new THREE.BoxGeometry(4.0, 0.3, 9.5)
    const pBedMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.7, metalness: 0.2 })
    const pBed = new THREE.Mesh(pBedGeom, pBedMat)
    pBed.position.set(0, 1.75, 2.375)
    pBed.castShadow = true
    vehicleGroup.add(pBed)

    // Caja / Contenedor de Carga
    const boxGeom = new THREE.BoxGeometry(4.0, 4.5, 9.5)
    // Usamos textura blanca corrugada simple (solo color y sombreado para que se vea limpio)
    const boxMat = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.5, metalness: 0.1 })
    const cargoBox = new THREE.Mesh(boxGeom, boxMat)
    cargoBox.position.set(0, 1.75 + 2.25, 2.375)
    cargoBox.castShadow = true
    vehicleGroup.add(cargoBox)

    // Guardabarros Traseros (Remolque)
    const mudTrailer = new THREE.Mesh(mudTractorGeom, mudMat)
    mudTrailer.position.set(0, 0.8, 6.9)
    vehicleGroup.add(mudTrailer)

    camera.position.set(16, 11, 20) // Alejar cámara para ver todo el camión majestuoso
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
</script>
