import React from 'react'
import { LucideIcon } from 'lucide-react'

export interface Metric {
  label: string
  value: React.ReactNode
  icon?: LucideIcon
}

// Literal class strings so Tailwind's JIT scanner keeps them.
const colsClass: Record<number, string> = {
  2: 'lg:grid-cols-2',
  3: 'lg:grid-cols-3',
  4: 'lg:grid-cols-4',
  5: 'lg:grid-cols-5',
}

interface MetricStripProps {
  metrics: Metric[]
}

/**
 * A hairline-divided strip of metric tiles: uppercase micro-label, large
 * monospace tabular value, small monochrome icon. Shared across pages so the
 * whole app reads with one consistent "instrument readout" language.
 */
export function MetricStrip({ metrics }: MetricStripProps) {
  const lg = colsClass[metrics.length] ?? 'lg:grid-cols-4'
  return (
    <div
      className={`grid grid-cols-2 gap-px overflow-hidden rounded-lg border border-secondary-800 bg-secondary-800 ${lg}`}
    >
      {metrics.map((m) => (
        <div key={m.label} className="bg-secondary-900 px-6 py-6">
          <div className="flex items-center justify-between">
            <span className="metric-label">{m.label}</span>
            {m.icon && <m.icon className="h-4 w-4 text-secondary-600" strokeWidth={1.75} />}
          </div>
          <p className="metric-value">{m.value}</p>
        </div>
      ))}
    </div>
  )
}

export default MetricStrip
