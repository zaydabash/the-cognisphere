import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Play, 
  Pause, 
  Square, 
  RotateCcw, 
  Settings, 
  ChevronDown,
  ChevronUp,
  Brain,
  Users,
  Activity
} from 'lucide-react'
import { useSimulation } from '../state/SimulationContext'
import SimulationConfig from './SimulationConfig'

const ControlPanel: React.FC = () => {
  const { state, controlSimulation, initializeSimulation, startRealTimeUpdates } = useSimulation()
  const [expanded, setExpanded] = useState(false)
  const [showConfig, setShowConfig] = useState(false)

  const handleControl = async (action: string) => {
    await controlSimulation(action)
  }

  const handleInitialize = async (config: any) => {
    const success = await initializeSimulation(config)
    if (success) {
      startRealTimeUpdates()
      setShowConfig(false)
    }
  }

  const isRunning = state.status?.state === 'running'
  const isPaused = state.status?.state === 'paused'
  const isStopped = state.status?.state === 'stopped' || state.status?.state === 'ready'

  return (
    <>
      <motion.div
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="bg-secondary-900 border-b border-secondary-800"
      >
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            {/* Status info */}
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <Brain className="w-5 h-5 text-primary-400" />
                <span className="text-sm font-medium text-secondary-200">
                  {state.agents.length} Agents
                </span>
              </div>
              
              {state.status?.realtime && (
                <>
                  <div className="flex items-center space-x-2">
                    <Users className="w-4 h-4 text-accent-400" />
                    <span className="text-sm text-secondary-300">
                      {state.status.realtime.faction_count} Factions
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Activity className="w-4 h-4 text-green-400" />
                    <span className="text-sm text-secondary-300">
                      {state.status.realtime.active_events} Events
                    </span>
                  </div>
                </>
              )}
            </div>

            {/* Controls */}
            <div className="flex items-center space-x-2">
              {/* Main control buttons */}
              <div className="flex items-center space-x-2">
                {isStopped && (
                  <button
                    onClick={() => handleControl('start')}
                    disabled={state.loading}
                    className="btn-primary flex items-center space-x-2"
                  >
                    <Play className="w-4 h-4" />
                    <span>Start</span>
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
                      <span>Step</span>
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
              </div>

              {/* Config button */}
              <button
                onClick={() => setShowConfig(!showConfig)}
                className="btn-ghost flex items-center space-x-2"
              >
                <Settings className="w-4 h-4" />
                <span>Config</span>
              </button>

              {/* Expand/collapse */}
              <button
                onClick={() => setExpanded(!expanded)}
                className="btn-ghost p-2"
              >
                {expanded ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          {/* Expanded panel */}
          <AnimatePresence>
            {expanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="border-t border-secondary-800 pt-4 pb-4"
              >
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  {/* Simulation stats */}
                  <div className="space-y-2">
                    <h3 className="text-sm font-medium text-secondary-200">Simulation</h3>
                    <div className="text-xs text-secondary-400 space-y-1">
                      <div>State: {state.status?.state || 'Unknown'}</div>
                      <div>Tick: {state.status?.current_tick || 0}</div>
                      <div>Duration: {state.status?.duration ? `${state.status.duration.toFixed(1)}s` : 'N/A'}</div>
                    </div>
                  </div>

                  {/* Cultural stats */}
                  <div className="space-y-2">
                    <h3 className="text-sm font-medium text-secondary-200">Culture</h3>
                    <div className="text-xs text-secondary-400 space-y-1">
                      <div>Myths: {state.status?.realtime?.myth_count || 0}</div>
                      <div>Norms: {state.status?.realtime?.norm_count || 0}</div>
                      <div>Slang: {state.culturalData?.slang.length || 0}</div>
                    </div>
                  </div>

                  {/* Economic stats */}
                  <div className="space-y-2">
                    <h3 className="text-sm font-medium text-secondary-200">Economy</h3>
                    <div className="text-xs text-secondary-400 space-y-1">
                      <div>Trades: {state.status?.realtime?.trade_count || 0}</div>
                      <div>Gini: {state.economicData?.gini_coefficient?.toFixed(3) || 'N/A'}</div>
                      <div>Events: {state.status?.realtime?.active_events || 0}</div>
                    </div>
                  </div>

                  {/* Network stats */}
                  <div className="space-y-2">
                    <h3 className="text-sm font-medium text-secondary-200">Network</h3>
                    <div className="text-xs text-secondary-400 space-y-1">
                      <div>Agents: {state.agents.length}</div>
                      <div>Factions: {state.status?.realtime?.faction_count || 0}</div>
                      <div>Connections: {state.networkData?.edges.length || 0}</div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Configuration modal */}
      <AnimatePresence>
        {showConfig && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4"
            onClick={() => setShowConfig(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-secondary-900 rounded-xl border border-secondary-800 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <SimulationConfig
                onSubmit={handleInitialize}
                onCancel={() => setShowConfig(false)}
                loading={state.loading}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

export default ControlPanel
