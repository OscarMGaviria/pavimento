import { reactive, computed } from 'vue'

const ZR_TABLE = {
  50: 0, 60: -0.253, 70: -0.524, 75: -0.674,
  80: -0.841, 85: -1.037, 90: -1.282, 91: -1.340,
  92: -1.405, 93: -1.476, 94: -1.555, 95: -1.645,
  96: -1.751, 97: -1.881, 98: -2.054, 99: -2.327
}

const RELIABILITY_OPTIONS = [50, 60, 70, 75, 80, 85, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]

const state = reactive({
  // Parámetros de diseño
  reliability: 90,
  Zr: -1.282,
  So: 0.45,
  pi: 4.2,
  pt: 2.5,
  get DPSI() {
    return Math.max(0.1, parseFloat((this.pi - this.pt).toFixed(2)))
  },
  W18: 8000000,
  // Número de capas: 3, 2, 1
  numCapas: 3,
  // Capa 1 — Carpeta asfáltica
  a1: 0.488,
  // Capa 2 — Base granular
  Mr1: 30000,
  a2: 0.138,
  m2: 0.80,
  // Capa 3 — Sub-base
  Mr2: 17000,
  a3: 0.120,
  m3: 0.80,
  // Subrasante
  Mr3: 10500,
})

function setReliability(r) {
  state.reliability = r
  state.Zr = ZR_TABLE[r]
}

// Bisección para resolver la ecuación AASHTO 93
function solveSN(Mr) {
  const { Zr, So, DPSI, W18 } = state
  function eq(SN) {
    return (
      Zr * So +
      9.36 * Math.log10(SN + 1) -
      0.2 +
      Math.log10(DPSI / (4.2 - 1.5)) / (0.40 + 1094 / Math.pow(SN + 1, 5.19)) +
      2.32 * Math.log10(Mr) -
      8.07 -
      Math.log10(W18)
    )
  }
  let s1 = 0, s2 = 50
  for (let i = 0; i < 1000; i++) {
    const mid = s1 + 0.5 * (s2 - s1)
    if (eq(s1) * eq(mid) < 0) s2 = mid
    else s1 = mid
  }
  return s1
}

function redondea(D) {
  return Math.ceil(D * 2.54) / 2.54
}

function minEspesor(W18) {
  if (W18 < 150000)                        return [2,   4, 4]
  if (W18 >= 150000 && W18 < 500000)       return [2.5, 4, 4]
  if (W18 >= 500000 && W18 < 2000000)      return [3,   6, 6]
  if (W18 >= 2000000 && W18 < 7000000)     return [3.5, 6, 6]
  return [4, 6, 6]
}

function disCA(SN, a1) {
  const dmin = minEspesor(state.W18)
  let D1 = redondea(SN / a1)
  D1 = Math.max(D1, dmin[0])
  return { D: D1, SNaportado: D1 * a1, cm: Math.round(D1 * 2.54) }
}

function disCapa(SNreq, SNant, a, m, idx) {
  const dmin = minEspesor(state.W18)
  let D = redondea((SNreq - SNant) / (a * m))
  D = Math.max(D, dmin[idx])
  return { D, SNaportado: D * a * m + SNant, cm: Math.round(D * 2.54) }
}

const results = computed(() => {
  const { numCapas, a1, a2, a3, m2, m3, Mr1, Mr2, Mr3, W18 } = state
  if (!W18 || W18 <= 0) return null

  const MR = [Mr1, Mr2, Mr3]
  const SNT = MR.map(mr => solveSN(mr))

  if (numCapas === 1) {
    const CA = disCA(SNT[2], a1)
    return {
      SNT,
      capas: [
        { nombre: 'Carpeta asfáltica', cm: CA.cm, SN: SNT[2], color: '#3B3B3B' },
      ],
    }
  }

  if (numCapas === 2) {
    const CA = disCA(SNT[0], a1)
    const BG = disCapa(SNT[2], CA.SNaportado, a2, m2, 1)
    return {
      SNT,
      capas: [
        { nombre: 'Carpeta asfáltica', cm: CA.cm, SN: SNT[0], color: '#3B3B3B' },
        { nombre: 'Base granular',     cm: BG.cm, SN: SNT[2], color: '#8D8068' },
      ],
    }
  }

  // 3 capas
  const CA  = disCA(SNT[0], a1)
  const BG  = disCapa(SNT[1], CA.SNaportado, a2, m2, 1)
  const SBG = disCapa(SNT[2], BG.SNaportado, a3, m3, 2)
  return {
    SNT,
    capas: [
      { nombre: 'Carpeta asfáltica', cm: CA.cm,  SN: SNT[0], color: '#2D2D2D' },
      { nombre: 'Base granular',     cm: BG.cm,  SN: SNT[1], color: '#8D8068' },
      { nombre: 'Sub-base granular', cm: SBG.cm, SN: SNT[2], color: '#6B4C3B' },
    ],
  }
})

export function useAASHTODesign() {
  return { state, results, setReliability, RELIABILITY_OPTIONS }
}
