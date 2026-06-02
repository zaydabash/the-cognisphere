import React from 'react'
import { motion } from 'framer-motion'
import { Play, Pause, Square, RotateCcw, Activity, Clock, Users, Zap } from 'lucide-react'
import { useSimulation } from '../state/SimulationContext'
import { MetricStrip } from '../components/MetricStrip'

const Simulation: React.FC = () => {
  const { state, controlSimulation, startRealTimeUpdates, stopRealTimeUpdates } = useSimulation()

  const handleControl = async (action: string) => {
    await controlSimulation(action)
  }

  const isRunning = state.status?.state === 'running'
  const isPaused = state.status?.state === 'paused'
  const isStopped = state.status?.state === 'stopped' || state.status?.state === 'ready'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Simulation Control</h1>
          <p className="text-secondary-400 mt-2">
            Monitor and control your emergent civilization simulation
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={() => {
              if (state.status?.state === 'running') {
                stopRealTimeUpdates()
              } else {
                startRealTimeUpdates()
              }
            }}
            className={`btn ${state.status?.state === 'running' ? 'btn-secondary' : 'btn-primary'}`}
          >
            {state.status?.state === 'running' ? 'Stop Updates' : 'Start Updates'}
          </button>
        </div>
      </div>

      {/* Status */}
      <div>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-secondary-200">
            Simulation Status
          </h2>
          <span
            className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${
              isRunning
                ? 'bg-accent-500/15 text-accent-300'
                : isPaused
                ? 'bg-primary-500/15 text-primary-300'
                : 'bg-secondary-700/50 text-secondary-400'
            }`}
          >
            {isRunning && <Activity className="h-3 w-3" />}
            {state.status?.state || 'Stopped'}
          </span>
        </div>

        <MetricStrip
          metrics={[
            { label: 'Current Tick', value: state.status?.current_tick ?? 0, icon: Clock },
            {
              label: 'Active Agents',
              value: state.status?.realtime?.agent_count ?? state.agents.length,
              icon: Users,
            },
            { label: 'Active Events', value: state.status?.realtime?.active_events ?? 0, icon: Zap },
            {
              label: 'Duration',
              value: state.status?.duration ? `${state.status.duration.toFixed(1)}s` : 'n/a',
              icon: Activity,
            },
          ]}
        />
      </div>

      {/* Control Panel */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card p-6"
      >
        <h2 className="text-lg font-semibold text-white mb-4">Simulation Controls</h2>
        
        <div className="flex flex-wrap items-center gap-4">
          {isStopped && (
            <button
              onClick={() => handleControl('start')}
              disabled={state.loading}
              className="btn-primary flex items-center space-x-2"
            >
              <Play className="w-4 h-4" />
              <span>Start Simulation</span>
            </button>
          )}

          {isRunning && (
            <button
              onClick={() => handleControl('pause')}
              disabled={state.loading}
              className="btn-secondary flex items-center space-x-2"
            >
              <Pause className="w-4 h-4" />
              <span>Pause</span>
            </button>
          )}

          {isPaused && (
            <>
              <button
                onClick={() => handleControl('resume')}
                disabled={state.loading}
                className="btn-primary flex items-center space-x-2"
              >
                <Play className="w-4 h-4" />
                <span>Resume</span>
              </button>
              
              <button
                onClick={() => handleControl('step')}
                disabled={state.loading}
                className="btn-accent flex items-center space-x-2"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Step Forward</span>
              </button>
            </>
          )}

          {(isRunning || isPaused) && (
            <button
              onClick={() => handleControl('stop')}
              disabled={state.loading}
              className="btn-ghost flex items-center space-x-2 text-red-400 hover:text-red-300 hover:bg-red-900/20"
            >
              <Square className="w-4 h-4" />
              <span>Stop</span>
            </button>
          )}

          {state.loading && (
            <div className="flex items-center space-x-2 text-secondary-400">
              <div className="spinner" />
              <span>Processing...</span>
            </div>
          )}
        </div>
      </motion.div>

      {/* Performance Metrics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card p-6"
      >
        <h2 className="text-lg font-semibold text-white mb-4">Performance Metrics</h2>
        
        {state.status?.scheduler_stats ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="text-sm font-medium text-secondary-300 mb-2">Tick Performance</h3>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-400">Total Ticks</span>
                  <span className="text-white">{state.status.scheduler_stats.total_ticks || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-400">Avg Duration</span>
                  <span className="text-white">
                    {state.status.scheduler_stats.avg_tick_duration?.toFixed(2) || '0.00'}ms
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-400">Total Duration</span>
                  <span className="text-white">
                    {state.status.scheduler_stats.total_duration?.toFixed(2) || '0.00'}s
                  </span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-secondary-300 mb-2">Processing Stats</h3>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-400">Agents Processed</span>
                  <span className="text-white">{state.status.scheduler_stats.agents_processed || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-400">Interactions</span>
                  <span className="text-white">{state.status.scheduler_stats.interactions_processed || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-400">State</span>
                  <span className="text-white">{state.status.scheduler_stats.state || 'Unknown'}</span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-secondary-300 mb-2">System Health</h3>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-400">Connection</span>
                  <span className={`${state.connected ? 'text-green-400' : 'text-red-400'}`}>
                    {state.connected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-400">Loading</span>
                  <span className={`${state.loading ? 'text-yellow-400' : 'text-green-400'}`}>
                    {state.loading ? 'Loading' : 'Ready'}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-400">Errors</span>
                  <span className={`${state.error ? 'text-red-400' : 'text-green-400'}`}>
                    {state.error ? 'Error' : 'None'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <Activity className="w-12 h-12 text-secondary-600 mx-auto mb-4" />
            <p className="text-secondary-400">No performance data available</p>
            <p className="text-sm text-secondary-500 mt-1">Start a simulation to see metrics</p>
          </div>
        )}
      </motion.div>

      {/* Error Display */}
      {state.error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-6 border-red-500/50 bg-red-500/5"
        >
          <div className="flex items-center space-x-2 text-red-400">
            <Activity className="w-5 h-5" />
            <h2 className="text-lg font-semibold">Error</h2>
          </div>
          <p className="text-red-300 mt-2">{state.error}</p>
        </motion.div>
      )}
    </div>
  )
}

export default Simulation
