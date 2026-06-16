import { jsPDF } from 'jspdf'

export function generatePavimentoPDF(state, results) {
  const doc = new jsPDF('p', 'mm', 'letter')

  const brandColor = [79, 70, 229] // Indigo 600
  const gray       = [71, 85, 105]
  const light      = [248, 250, 252]
  const amber      = [245, 158, 11]

  // Header
  doc.setFillColor(...brandColor)
  doc.rect(0, 0, 216, 28, 'F')
  doc.setTextColor(255, 255, 255)
  doc.setFontSize(16)
  doc.setFont('helvetica', 'bold')
  doc.text('AASHTO 93 — Diseño de Pavimento Flexible', 15, 12)
  doc.setFontSize(9)
  doc.setFont('helvetica', 'normal')
  doc.text('AASHTO Guide for Design of Pavement Structures, 1993', 15, 20)

  // Fecha
  doc.setTextColor(200, 210, 255)
  doc.setFontSize(8)
  doc.text(new Date().toLocaleDateString('es-CO'), 180, 20)

  let y = 38

  // ---- Parámetros de diseño ----
  doc.setTextColor(...brandColor)
  doc.setFontSize(11)
  doc.setFont('helvetica', 'bold')
  doc.text('Parámetros de diseño', 15, y)
  y += 6

  const params = [
    ['Confiabilidad (R)',                 `${state.reliability}%`],
    ['Desv. estándar normal (Zr)',        state.Zr.toFixed(3)],
    ['Error estándar combinado (So)',     state.So.toFixed(3)],
    ['Pérdida de serviciabilidad (ΔPSI)', state.DPSI.toFixed(2)],
    ['Ejes equivalentes 18 kips (W₁₈)',  state.W18.toLocaleString('es-CO')],
    ['Número de capas',                   String(state.numCapas)],
  ]

  params.forEach(([label, value], i) => {
    const row = i % 2 === 0
    if (row) {
      doc.setFillColor(...light)
      doc.rect(15, y - 4, 186, 7, 'F')
    }
    doc.setTextColor(...gray)
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(9)
    doc.text(label, 18, y)
    doc.setFont('courier', 'bold')
    doc.setTextColor(...brandColor)
    doc.text(value, 150, y, { align: 'right' })
    y += 7
  })

  y += 5

  // ---- Propiedades materiales ----
  doc.setTextColor(...brandColor)
  doc.setFontSize(11)
  doc.setFont('helvetica', 'bold')
  doc.text('Propiedades de materiales', 15, y)
  y += 6

  const matRows = [['Coef. a₁ (CA)', state.a1.toFixed(3)]]
  if (state.numCapas >= 2) {
    matRows.push(
      ['Mr₁ Base granular (psi)', state.Mr1.toLocaleString('es-CO')],
      ['Coef. a₂', state.a2.toFixed(3)],
      ['m₂ drenaje', state.m2.toFixed(2)],
    )
  }
  if (state.numCapas === 3) {
    matRows.push(
      ['Mr₂ Sub-base (psi)', state.Mr2.toLocaleString('es-CO')],
      ['Coef. a₃', state.a3.toFixed(3)],
      ['m₃ drenaje', state.m3.toFixed(2)],
    )
  }
  matRows.push(['Mr₃ Subrasante (psi)', state.Mr3.toLocaleString('es-CO')])

  matRows.forEach(([label, value], i) => {
    if (i % 2 === 0) {
      doc.setFillColor(...light)
      doc.rect(15, y - 4, 186, 7, 'F')
    }
    doc.setTextColor(...gray)
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(9)
    doc.text(label, 18, y)
    doc.setFont('courier', 'bold')
    doc.setTextColor(...brandColor)
    doc.text(String(value), 150, y, { align: 'right' })
    y += 7
  })

  y += 5

  // ---- Resultados ----
  doc.setTextColor(...brandColor)
  doc.setFontSize(11)
  doc.setFont('helvetica', 'bold')
  doc.text('Resultados — Estructura de pavimento', 15, y)
  y += 8

  // Tabla de capas
  doc.setFillColor(...brandColor)
  doc.rect(15, y - 5, 186, 7, 'F')
  doc.setTextColor(255, 255, 255)
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(9)
  doc.text('Capa', 18, y)
  doc.text('SN requerido', 110, y, { align: 'center' })
  doc.text('Espesor (cm)', 185, y, { align: 'right' })
  y += 8

  const layerColors = [[45, 45, 45], [141, 128, 104], [107, 76, 59]]
  results.capas.forEach((capa, i) => {
    doc.setFillColor(...(i % 2 === 0 ? light : [255, 255, 255]))
    doc.rect(15, y - 5, 186, 8, 'F')
    doc.setFillColor(...layerColors[i] || layerColors[2])
    doc.rect(15, y - 4, 4, 6, 'F')
    doc.setTextColor(...gray)
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(9)
    doc.text(capa.nombre, 22, y)
    doc.setFont('courier', 'normal')
    doc.text(capa.SN.toFixed(3), 110, y, { align: 'center' })
    doc.setFont('courier', 'bold')
    doc.setTextColor(...brandColor)
    doc.text(`${capa.cm} cm`, 185, y, { align: 'right' })
    y += 8
  })

  // Total
  const total = results.capas.reduce((a, c) => a + c.cm, 0)
  doc.setFillColor(...amber)
  doc.rect(15, y - 4, 186, 8, 'F')
  doc.setTextColor(255, 255, 255)
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(10)
  doc.text('Espesor total de pavimento', 18, y + 1)
  doc.text(`${total} cm`, 185, y + 1, { align: 'right' })

  // Footer
  doc.setFontSize(8)
  doc.setTextColor(150, 150, 150)
  doc.text('Generado con AASHTO 93 Web — By Oscar Marquez', 108, 272, { align: 'center' })

  doc.save('diseno-pavimento-aashto93.pdf')
}
