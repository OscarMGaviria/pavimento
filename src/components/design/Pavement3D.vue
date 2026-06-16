<template>
  <div class="bg-white rounded-2xl border border-slate-100 shadow-sm shadow-slate-100/40 p-6 flex flex-col relative min-h-0">
    <div class="flex items-center justify-between mb-4 shrink-0 flex-wrap gap-2">
      <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400">Modelo tridimensional (3D)</h2>
      
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
          >Eje Doble (Tándem)</button>
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
    <div ref="container" class="w-full h-80 md:h-[400px] bg-slate-50/50 border border-slate-100 rounded-xl overflow-hidden relative shrink-0 shadow-inner">
      <!-- Instrucciones de Cámara -->
      <span class="absolute bottom-3 left-3 text-[9px] font-bold text-slate-500 uppercase tracking-widest pointer-events-none select-none bg-white/80 border border-slate-200/50 shadow-sm px-2.5 py-1 rounded-lg backdrop-blur-sm">
        Arrastra para rotar • Click Der para desplazar • Scroll para zoom
      </span>
      
      <div v-if="!results" class="absolute inset-0 flex items-center justify-center text-slate-400 text-xs font-semibold bg-slate-50/50">
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

  // Textos grabados Bridgestone
  sideCtx.fillStyle = '#a1a1aa'
  sideCtx.font = 'bold 24px Arial, sans-serif'
  sideCtx.textAlign = 'center'
  sideCtx.textBaseline = 'middle'
  
  sideCtx.save()
  sideCtx.translate(cx, cy)
  sideCtx.fillText('BRIDGESTONE', 0, -188)
  sideCtx.restore()

  sideCtx.save()
  sideCtx.translate(cx, cy)
  sideCtx.rotate(Math.PI)
  sideCtx.fillText('M-DRIVE 002', 0, -188)
  sideCtx.restore()

  sideCtx.font = 'bold 12px Arial, sans-serif'
  sideCtx.fillStyle = '#71717a'
  
  sideCtx.save()
  sideCtx.translate(cx, cy)
  sideCtx.rotate(-Math.PI / 2)
  sideCtx.fillText('315 / 80 R 22.5', 0, -188)
  sideCtx.restore()

  sideCtx.save()
  sideCtx.translate(cx, cy)
  sideCtx.rotate(Math.PI / 2)
  sideCtx.fillText('REGIONAL / LONG HAUL', 0, -188)
  sideCtx.restore()

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
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
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
    
    // 1. Rotar los neumáticos respecto a su centro en el eje X
    wheelsList.forEach(wheel => {
      wheel.rotation.x += 0.04
    })

    // 2. Desplazar la textura del asfalto en V (eje Y del canvas) para simular movimiento
    if (textures.asphalt) {
      textures.asphalt.offset.y -= ROAD_SPEED / DEPTH_3D_VAL
    }

    // 3. Desplazar los guiones amarillos centrales en el eje Z
    roadDashes.forEach(dash => {
      dash.position.z += ROAD_SPEED
      // Si el guión sale completamente del borde frontal (+2.75 con el clipping de GPU), lo devolvemos al borde trasero (-2.75)
      if (dash.position.z > 2.75) {
        dash.position.z -= 5.5
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

  const capas = results.value.capas
  let yOffset = 0

  capas.forEach((capa) => {
    const h = capa.cm * SCALE_Y
    const geom = new THREE.BoxGeometry(WIDTH_3D, h, DEPTH_3D)

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
  const subGeom = new THREE.BoxGeometry(WIDTH_3D, subH, DEPTH_3D)
  const subMat = new THREE.MeshStandardMaterial({
    color: 0x15803d, // Verde oscuro
    roughness: 0.98,
    metalness: 0.05
  })
  const subMesh = new THREE.Mesh(subGeom, subMat)
  subMesh.position.y = -yOffset - subH / 2
  subMesh.receiveShadow = true
  layerGroup.add(subMesh)

  // --- Líneas de Demarcación Vial (Dos Carriles con Movimiento y Recorte por GPU) ---
  // Definir planos de recorte en los extremos Z del pavimento (Z = ±2.5)
  const clipPlanes = [
    new THREE.Plane(new THREE.Vector3(0, 0, -1), 2.5), // Corta todo Z > 2.5
    new THREE.Plane(new THREE.Vector3(0, 0, 1), 2.5)   // Corta todo Z < -2.5
  ]

  // 1. Línea Blanca Lateral Izquierda (x = -3.2)
  const lineLeftGeom = new THREE.BoxGeometry(0.12, 0.002, DEPTH_3D)
  const lineLeftMat = new THREE.MeshBasicMaterial({ color: 0xf8fafc, clippingPlanes: clipPlanes }) // Blanco sólido con recorte
  const lineLeftMesh = new THREE.Mesh(lineLeftGeom, lineLeftMat)
  lineLeftMesh.position.set(-3.2, 0.001, 0)
  lineLeftMesh.receiveShadow = true
  layerGroup.add(lineLeftMesh)

  // 2. Línea Blanca Lateral Derecha (x = 3.2)
  const lineRightGeom = new THREE.BoxGeometry(0.12, 0.002, DEPTH_3D)
  const lineRightMat = new THREE.MeshBasicMaterial({ color: 0xf8fafc, clippingPlanes: clipPlanes })
  const lineRightMesh = new THREE.Mesh(lineRightGeom, lineRightMat)
  lineRightMesh.position.set(3.2, 0.001, 0)
  lineRightMesh.receiveShadow = true
  layerGroup.add(lineRightMesh)

  // 3. Línea Central Amarilla Intermitente (x = 0)
  roadDashes = []
  const dashLength = 0.5
  const dashGeom = new THREE.BoxGeometry(0.10, 0.002, dashLength)
  const dashMat = new THREE.MeshBasicMaterial({ color: 0xeab308, clippingPlanes: clipPlanes }) // Amarillo tráfico con recorte
  
  for (let i = 0; i < 5; i++) {
    const dashMesh = new THREE.Mesh(dashGeom, dashMat)
    // Distribuir de z = -2.2 a z = 2.2 para espaciamiento uniforme inicial (intervalos de 1.1)
    const startZ = -2.2 + i * 1.1
    dashMesh.position.set(0, 0.001, startZ)
    dashMesh.receiveShadow = true
    layerGroup.add(dashMesh)
    roadDashes.push(dashMesh)
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
  const isDouble = axleType.value === 'double'

  // Materiales para neumáticos Bridgestone
  const tireTreadMat = new THREE.MeshStandardMaterial({ 
    map: textures.tireTread, 
    roughness: 0.8,
    metalness: 0.1 
  })
  const tireSidewallMat = new THREE.MeshStandardMaterial({ 
    map: textures.tireSidewall, 
    roughness: 0.8,
    metalness: 0.1 
  })
  const tireMaterials = [
    tireTreadMat,    // Lado / Banda de rodadura
    tireSidewallMat, // Tapa superior (exterior)
    tireSidewallMat  // Tapa inferior (interior)
  ]

  // Materiales para rines galvanizados (satinados)
  const rimFaceMat = new THREE.MeshStandardMaterial({
    map: textures.rim,
    roughness: 0.38, // Mayor rugosidad para aspecto satinado/galvanizado
    metalness: 0.85  // Metalicidad de chapa de acero
  })
  const rimSideMat = new THREE.MeshStandardMaterial({
    color: 0x94a3b8,
    roughness: 0.4,
    metalness: 0.8
  })
  const rimMaterials = [
    rimSideMat, // Lado del cilindro del rin
    rimFaceMat, // Tapa superior
    rimFaceMat  // Tapa inferior
  ]

  const hubMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.2, metalness: 0.9 })
  const axleMat = new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.3, metalness: 0.8 })

  // Dimensiones del Neumático (Cilindro con radio 0.90 y espesor 0.40)
  const R_WHEEL = 0.90
  const TIRE_GEOM = new THREE.CylinderGeometry(R_WHEEL, R_WHEEL, 0.40, 32)
  TIRE_GEOM.rotateZ(Math.PI / 2) // Orientar el eje del cilindro hacia X para que ruede sobre Z

  // Llanta / Rin central (Cilindro más angosto para que quede rebajado dentro del neumático)
  const RIM_GEOM = new THREE.CylinderGeometry(0.48, 0.48, 0.36, 24)
  RIM_GEOM.rotateZ(Math.PI / 2) // Orientar hacia X

  // Generador de etiqueta Sprite "8.2 Ton" con sombra de texto de alta definición
  const labelCanvas = document.createElement('canvas')
  labelCanvas.width = 256
  labelCanvas.height = 128
  const labelCtx = labelCanvas.getContext('2d')
  
  // Dibujar tarjeta roja con bordes redondeados y contorno blanco
  labelCtx.fillStyle = '#ef4444' // Rojo brillante
  labelCtx.beginPath()
  labelCtx.roundRect(8, 8, 240, 112, 16)
  labelCtx.fill()
  labelCtx.lineWidth = 6
  labelCtx.strokeStyle = '#ffffff'
  labelCtx.stroke()

  // Texto blanco con sombra
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

  function buildAxle(zPos) {
    // Eje central extendido a 6.0 unidades para acomodar la nueva separación
    const axleGeom = new THREE.CylinderGeometry(0.12, 0.12, 6.0, 12)
    axleGeom.rotateZ(Math.PI / 2)
    const axleMesh = new THREE.Mesh(axleGeom, axleMat)
    axleMesh.position.set(0, R_WHEEL, zPos)
    axleMesh.castShadow = true
    vehicleGroup.add(axleMesh)

    // Ruedas duales (Izquierda y Derecha) con separación de 10 cm (0.10 unidades libres)
    const xOffsets = [-2.85, -2.35, 2.35, 2.85]
    xOffsets.forEach((x, i) => {
      // Crear neumático (Cylinder)
      const tireMesh = new THREE.Mesh(TIRE_GEOM, tireMaterials)
      tireMesh.position.set(x, R_WHEEL, zPos)
      tireMesh.castShadow = true

      // Crear Rin central (Cylinder)
      const rimMesh = new THREE.Mesh(RIM_GEOM, rimMaterials)
      rimMesh.castShadow = true
      tireMesh.add(rimMesh)

      // Tapón plateado central (Taza de rueda)
      if (i === 0 || i === 3) {
        const hubGeom = new THREE.CylinderGeometry(0.18, 0.18, 0.05, 12)
        hubGeom.rotateZ(Math.PI / 2)
        const hubMesh = new THREE.Mesh(hubGeom, hubMat)
        // Posicionar relativo al neumático (en la cara externa)
        hubMesh.position.set(i === 0 ? -0.19 : 0.19, 0, 0)
        tireMesh.add(hubMesh)
      }

      vehicleGroup.add(tireMesh)
      wheelsList.push(tireMesh)
    })

    // Flecha indicadora de carga 3D sólida y emisiva (Cilindro + Cono)
    const arrowGroup = new THREE.Group()
    const arrowMat = new THREE.MeshStandardMaterial({
      color: 0xef4444,     // Rojo vibrante
      emissive: 0x991b1b,  // Resplandor rojo oscuro
      roughness: 0.15,
      metalness: 0.8
    })

    // Punta (cono)
    const coneGeom = new THREE.ConeGeometry(0.22, 0.4, 16)
    const coneMesh = new THREE.Mesh(coneGeom, arrowMat)
    coneMesh.rotation.z = Math.PI // Apuntar hacia abajo
    coneMesh.position.y = 0.2     // Colocar para que la punta esté en y=0
    coneMesh.castShadow = true
    arrowGroup.add(coneMesh)

    // Cuerpo (cilindro)
    const shaftGeom = new THREE.CylinderGeometry(0.08, 0.08, 0.8, 16)
    const shaftMesh = new THREE.Mesh(shaftGeom, arrowMat)
    shaftMesh.position.y = 0.8     // Colocar para que empiece en y=0.4 y suba a y=1.2
    shaftMesh.castShadow = true
    arrowGroup.add(shaftMesh)

    // Posicionar flecha justo encima del eje
    arrowGroup.position.set(0, R_WHEEL + 0.15, zPos)
    vehicleGroup.add(arrowGroup)

    // Etiqueta flotante Sprite de alta visibilidad
    const labelSprite = new THREE.Sprite(labelMat)
    labelSprite.scale.set(2.8, 1.4, 1) // Escala aumentada
    labelSprite.position.set(0, R_WHEEL + 1.6, zPos)
    vehicleGroup.add(labelSprite)
  }

  if (isDouble) {
    buildAxle(-1.35)
    buildAxle(1.35)

    // Barras de suspensión lateral
    const linkGeom = new THREE.BoxGeometry(0.15, 0.26, 3.0)
    const linkLeft = new THREE.Mesh(linkGeom, axleMat)
    linkLeft.position.set(-2.0, R_WHEEL, 0)
    linkLeft.castShadow = true
    vehicleGroup.add(linkLeft)

    const linkRight = new THREE.Mesh(linkGeom, axleMat)
    linkRight.position.set(2.0, R_WHEEL, 0)
    linkRight.castShadow = true
    vehicleGroup.add(linkRight)
  } else {
    buildAxle(0)
  }

  if (isDouble) {
    buildAxle(-1.35)
    buildAxle(1.35)

    // Barras de suspensión lateral
    const linkGeom = new THREE.BoxGeometry(0.15, 0.26, 3.0)
    const linkLeft = new THREE.Mesh(linkGeom, axleMat)
    linkLeft.position.set(-2.0, R_WHEEL, 0)
    linkLeft.castShadow = true
    vehicleGroup.add(linkLeft)

    const linkRight = new THREE.Mesh(linkGeom, axleMat)
    linkRight.position.set(2.0, R_WHEEL, 0)
    linkRight.castShadow = true
    vehicleGroup.add(linkRight)
  } else {
    buildAxle(0)
  }

  // --- Dibujar los Bulbos de Presiones en las Caras Laterales (Paralelas a las Llantas) ---
  if (showStressBulb.value && results.value) {
    const capas = results.value.capas
    let yTotal = 0
    capas.forEach(c => {
      yTotal += c.cm * SCALE_Y
    })
    const subH = 1.5
    yTotal += subH

    // Obtener el SN acumulado total
    const SN = results.value.SNT[2] || 3.0

    // Canvas de renderizado para textura del bulbo lateral (YZ)
    const stressCanvas = document.createElement('canvas')
    stressCanvas.width = 512
    stressCanvas.height = 256
    
    drawStressBulbSide(stressCanvas, 512, 256, capas, SN)
    
    const stressTex = new THREE.CanvasTexture(stressCanvas)
    const stressMat = new THREE.MeshBasicMaterial({
      map: stressTex,
      transparent: true,
      opacity: 0.95,
      side: THREE.DoubleSide,
      depthWrite: false
    })

    // La anchura de la geometría es DEPTH_3D (5) a lo largo de Z, altura es yTotal
    const planeGeom = new THREE.PlaneGeometry(DEPTH_3D, yTotal)

    // Plano lateral derecho (+X, un poco desplazado hacia afuera para evitar Z-fighting)
    const rightPlane = new THREE.Mesh(planeGeom, stressMat)
    rightPlane.position.set(3.501, -yTotal / 2, 0)
    rightPlane.rotation.y = Math.PI / 2
    vehicleGroup.add(rightPlane)

    // Plano lateral izquierdo (-X)
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
