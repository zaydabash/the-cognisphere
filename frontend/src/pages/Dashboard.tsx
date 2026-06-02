import React from 'react'
import { motion } from 'framer-motion'
import {
  Users,
  Activity,
  Globe,
  Network,
  Clock,
  Link,
  Landmark,
  Database,
  ArrowLeftRight,
  Scale,
} from 'lucide-react'
import { useSimulation } from '../state/SimulationContext'

const Dashboard: React.FC = () => {
  const { state } = useSimulation()

  const realtime = state.status?.realtime
  const isRunning = state.status?.state === 'running'
  const currentTick = realtime?.current_tick ?? 0

  // Headline metrics: the four numbers you watch.
  const headline = [
    { name: 'Agents', value: realtime?.agent_count ?? state.agents.length, icon: Users },
    { name: 'Trades', value: realtime?.trade_count ?? 0, icon: ArrowLeftRight },
    { name: 'Myths', value: realtime?.myth_count ?? 0, icon: Globe },
    { name: 'Gini', value: (realtime?.gini_coefficient ?? 0).toFixed(3), icon: Scale },
  ]

  // Emergent social / memory dynamics, secondary strip.
  const emergent = [
    { name: 'Alliances', value: realtime?.alliance_count ?? 0, icon: Link },
    { name: 'Betrayals', value: realtime?.betrayal_count ?? 0, icon: Activity },
    { name: 'Institutions', value: realtime?.institution_count ?? 0, icon: Landmark },
    { name: 'Factions', value: realtime?.faction_count ?? 0, icon: Network },
    { name: 'Memories', value: realtime?.world_memories ?? 0, icon: Database },
  ]

  const myths = state.culturalData?.myths ?? []
  const norms = state.culturalData?.norms ?? []
  const networkData = state.networkData
  const economicData = state.economicData
  const prices = economicData?.market_summary?.current_prices

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-end justify-between border-b border-secondary-800 pb-5">
        <div>
          <p className="text-[0.7rem] font-medium uppercase tracking-[0.18em] text-primary-400">
            Observatory
          </p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-secondary-50">
            Civilization Overview
          </h1>
        </div>
        <div className="flex items-center gap-5 text-sm">
          <span className="flex items-center gap-2 text-secondary-400">
            <span
              className={`inline-block h-1.5 w-1.5 rounded-full ${
                isRunning ? 'bg-accent-400' : state.connected ? 'bg-primary-400' : 'bg-secondary-600'
              }`}
            />
            {isRunning ? 'Running' : state.connected ? (state.status?.state ?? 'Ready') : 'Offline'}
          </span>
          <span className="flex items-center gap-1.5 font-mono tabular text-secondary-300">
            <Clock className="h-3.5 w-3.5 text-secondary-500" />
            {String(currentTick).padStart(4, '0')}
          </span>
        </div>
      </div>

      {/* Headline metrics */}
      <div className="grid grid-cols-2 gap-px overflow-hidden rounded-lg border border-secondary-800 bg-secondary-800 lg:grid-cols-4">
        {headline.map((m, i) => (
          <motion.div
            key={m.name}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: i * 0.05 }}
            className="bg-secondary-900 px-6 py-7"
          >
            <div className="flex items-center justify-between">
              <span className="metric-label">{m.name}</span>
              <m.icon className="h-4 w-4 text-secondary-600" strokeWidth={1.75} />
            </div>
            <p className="metric-value text-4xl">{m.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Emergent dynamics strip */}
      <div>
        <h2 className="mb-3 text-xs font-medium uppercase tracking-[0.14em] text-secondary-500">
          Emergent dynamics
        </h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {emergent.map((m) => (
            <div key={m.name} className="card flex items-center gap-3 px-4 py-3">
              <m.icon className="h-4 w-4 shrink-0 text-secondary-500" strokeWidth={1.75} />
              <div className="min-w-0">
                <p className="font-mono tabular text-lg font-semibold leading-none text-secondary-50">
                  {m.value}
                </p>
                <p className="mt-1 truncate text-[0.7rem] uppercase tracking-wide text-secondary-400">
                  {m.name}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cultural + economic */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Cultural developments */}
        <div className="card p-6">
          <div className="mb-5 flex items-center gap-2.5">
            <Globe className="h-4 w-4 text-primary-400" strokeWidth={1.75} />
            <h2 className="text-sm font-semibold uppercase tracking-wide text-secondary-200">
              Cultural developments
            </h2>
          </div>

          <p className="metric-label mb-2">Recent myths</p>
          <div className="space-y-px overflow-hidden rounded-md border border-secondary-800">
            {myths.length > 0 ? (
              myths.slice(0, 4).map((myth) => (
                <div key={myth.id} className="flex items-center justify-between gap-3 bg-secondary-900/60 px-3 py-2.5">
                  <div className="min-w-0">
                    <p className="truncate text-sm text-secondary-100">{myth.title}</p>
                    <p className="text-xs text-secondary-500">{myth.theme}</p>
                  </div>
                  <span className="shrink-0 font-mono tabular text-xs text-primary-400">
                    {(myth.popularity * 100).toFixed(0)}%
                  </span>
                </div>
              ))
            ) : (
              <p className="bg-secondary-900/60 px-3 py-4 text-sm text-secondary-500">
                No myths yet. Start a simulation.
              </p>
            )}
          </div>

          <p className="metric-label mb-2 mt-5">Active norms</p>
          {norms.length > 0 ? (
            <div className="space-y-px overflow-hidden rounded-md border border-secondary-800">
              {norms.slice(0, 3).map((norm) => (
                <div key={norm.id} className="flex items-center justify-between gap-3 bg-secondary-900/60 px-3 py-2.5">
                  <p className="truncate text-sm text-secondary-100">{norm.title}</p>
                  <span className="shrink-0 font-mono tabular text-xs text-secondary-400">
                    {norm.votes_for}/{norm.votes_for + norm.votes_against}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="rounded-md border border-secondary-800 bg-secondary-900/60 px-3 py-4 text-sm text-secondary-500">
              No active norms yet.
            </p>
          )}
        </div>

        {/* Economic overview */}
        <div className="card p-6">
          <div className="mb-5 flex items-center gap-2.5">
            <ArrowLeftRight className="h-4 w-4 text-primary-400" strokeWidth={1.75} />
            <h2 className="text-sm font-semibold uppercase tracking-wide text-secondary-200">
              Economy
            </h2>
          </div>

          <div className="grid grid-cols-3 gap-px overflow-hidden rounded-md border border-secondary-800">
            {[
              { label: 'Trades', value: realtime?.trade_count ?? 0 },
              { label: 'Clearings', value: realtime?.market_clearings ?? 0 },
              { label: 'Gini', value: (economicData?.gini_coefficient ?? realtime?.gini_coefficient ?? 0).toFixed(3) },
            ].map((s) => (
              <div key={s.label} className="bg-secondary-900/60 px-4 py-4 text-center">
                <p className="font-mono tabular text-xl font-semibold text-secondary-50">{s.value}</p>
                <p className="metric-label mt-1">{s.label}</p>
              </div>
            ))}
          </div>

          {prices && (
            <>
              <p className="metric-label mb-3 mt-5">Resource prices</p>
              <div className="space-y-3">
                {Object.entries(prices).map(([res, price]) => {
                  const pct = Math.min(100, (Number(price) / 30) * 100)
                  return (
                    <div key={res}>
                      <div className="mb-1 flex items-center justify-between text-xs">
                        <span className="capitalize text-secondary-300">{res}</span>
                        <span className="font-mono tabular text-secondary-400">{Number(price).toFixed(2)}</span>
                      </div>
                      <div className="h-1 overflow-hidden rounded-full bg-secondary-800">
                        <div className="h-full rounded-full bg-primary-500/70" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  )
                })}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Network overview */}
      <div className="card p-6">
        <div className="mb-5 flex items-center gap-2.5">
          <Network className="h-4 w-4 text-primary-400" strokeWidth={1.75} />
          <h2 className="text-sm font-semibold uppercase tracking-wide text-secondary-200">
            Network
          </h2>
        </div>
        <div className="grid grid-cols-2 gap-px overflow-hidden rounded-md border border-secondary-800 md:grid-cols-4">
          {[
            { label: 'Agents', value: networkData?.nodes.length ?? realtime?.agent_count ?? 0 },
            { label: 'Connections', value: networkData?.edges.length ?? 0 },
            {
              label: 'Avg degree',
              value: networkData?.nodes.length
                ? (networkData.edges.length / networkData.nodes.length).toFixed(1)
                : '0.0',
            },
            { label: 'Alliances', value: realtime?.alliance_count ?? 0 },
          ].map((s) => (
            <div key={s.label} className="bg-secondary-900/60 px-4 py-5 text-center">
              <p className="font-mono tabular text-2xl font-semibold text-secondary-50">{s.value}</p>
              <p className="metric-label mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
