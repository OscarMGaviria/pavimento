import { reactive, computed } from 'vue'
import { useAASHTODesign } from './useAASHTODesign.js'

const costs = reactive({
  c1: 45,   // $/m²·cm carpeta asfáltica
  c2: 18,   // $/m²·cm base granular
  c3: 10,   // $/m²·cm sub-base
})

export function useOptimization() {
  const { state, results } = useAASHTODesign()

  const optimizationResults = computed(() => {
    if (!results.value || state.numCapas !== 3) return null

    const { SNT } = results.value
    const { a1, a2, a3, m2, m3, W18 } = state

    function minEspesor(W18) {
      if (W18 < 150000)                    return [2,   4, 4]
      if (W18 < 500000)                    return [2.5, 4, 4]
      if (W18 < 2000000)                   return [3,   6, 6]
      if (W18 < 7000000)                   return [3.5, 6, 6]
      return [4, 6, 6]
    }

    function redondea(D) {
      return Math.ceil(D * 2.54) / 2.54
    }

    const dmin = minEspesor(W18)
    const SN1req = SNT[0], SN2req = SNT[1], SN3req = SNT[2]

    let best = null
    let candidates = []

    // D1 desde mínimo hasta SN3req/a1 con paso 0.5"
    const D1max = Math.ceil((SN3req / a1) * 2) / 2 + 2
    for (let D1 = dmin[0]; D1 <= D1max; D1 += 0.5) {
      const SN1_aportado = D1 * a1
      if (SN1_aportado < SN1req) continue

      const SN2_needed = SN2req - SN1_aportado
      let D2 = SN2_needed > 0 ? redondea(SN2_needed / (a2 * m2)) : dmin[1]
      D2 = Math.max(D2, dmin[1])
      const SN2_aportado = SN1_aportado + D2 * a2 * m2

      const SN3_needed = SN3req - SN2_aportado
      let D3 = SN3_needed > 0 ? redondea(SN3_needed / (a3 * m3)) : dmin[2]
      D3 = Math.max(D3, dmin[2])

      const costo = D1 * costs.c1 + D2 * costs.c2 + D3 * costs.c3
      const entry = {
        D1: Math.round(D1 * 2.54),
        D2: Math.round(D2 * 2.54),
        D3: Math.round(D3 * 2.54),
        costo: Math.round(costo * 100) / 100,
      }
      candidates.push(entry)
      if (!best || costo < best.costo) best = entry
    }

    // Tomar los 5 de menor costo para la tabla
    candidates.sort((a, b) => a.costo - b.costo)
    return { best, candidates: candidates.slice(0, 8) }
  })

  return { costs, optimizationResults }
}
