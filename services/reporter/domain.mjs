export async function operation({ site, rateCents, readings }, meter) {
  if (!Number.isFinite(rateCents) || rateCents < 0 || rateCents > 10000) throw new TypeError('Invalid rateCents')
  const series = await meter({ site, readings })
  const totalWh = series.readings.reduce((sum, { wh }) => sum + wh, 0)
  const peakWh = series.readings.reduce((max, { wh }) => Math.max(max, wh), 0)
  return { site, intervals: series.readings.length, totalKwh: totalWh / 1000, peakKw: peakWh / 500,
    costCents: Math.round(totalWh / 1000 * rateCents) }
}
