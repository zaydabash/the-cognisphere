import React, { useState } from 'react'
import { X, Brain, Settings, Play } from 'lucide-react'

interface SimulationConfigProps {
  onSubmit: (config: any) => void
  onCancel: () => void
  loading: boolean
}

const SimulationConfig: React.FC<SimulationConfigProps> = ({ onSubmit, onCancel, loading }) => {
  const [config, setConfig] = useState({
    num_agents: 300,
    seed: 42,
    max_ticks: 10000,
    llm_mode: 'mock',
    llm_model: 'gpt-3.5-turbo',
    llm_temperature: 0.3,
    tick_duration_ms: 100,
    agents_per_tick: 50,
    interactions_per_tick: 100,
    memory_backend: 'networkx',
    vector_backend: 'faiss',
    snapshot_frequency: 20,
    snapshot_directory: 'snapshots',
    stimuli_file: '',
    enable_environmental_stimuli: false,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(config)
  }

  const handleChange = (field: string, value: any) => {
    setConfig(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-primary">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Simulation Configuration</h2>
            <p className="text-sm text-secondary-400">Configure your emergent civilization</p>
          </div>
        </div>
        <button
          onClick={onCancel}
          className="p-2 rounded-lg text-secondary-400 hover:text-secondary-200 hover:bg-secondary-800"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* World Settings */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <Settings className="w-5 h-5 text-primary-400" />
            <h3 className="text-lg font-semibold text-white">World Settings</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Number of Agents
              </label>
              <input
                type="number"
                value={config.num_agents}
                onChange={(e) => handleChange('num_agents', parseInt(e.target.value))}
                className="input"
                min="10"
                max="1000"
                step="10"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Random Seed
              </label>
              <input
                type="number"
                value={config.seed}
                onChange={(e) => handleChange('seed', parseInt(e.target.value))}
                className="input"
                min="0"
                max="999999"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Max Ticks
              </label>
              <input
                type="number"
                value={config.max_ticks}
                onChange={(e) => handleChange('max_ticks', parseInt(e.target.value))}
                className="input"
                min="100"
                max="100000"
                step="100"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Tick Duration (ms)
              </label>
              <input
                type="number"
                value={config.tick_duration_ms}
                onChange={(e) => handleChange('tick_duration_ms', parseInt(e.target.value))}
                className="input"
                min="10"
                max="1000"
                step="10"
              />
            </div>
          </div>
        </div>

        {/* LLM Settings */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <Brain className="w-5 h-5 text-accent-400" />
            <h3 className="text-lg font-semibold text-white">LLM Settings</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                LLM Mode
              </label>
              <select
                value={config.llm_mode}
                onChange={(e) => handleChange('llm_mode', e.target.value)}
                className="select"
              >
                <option value="mock">Mock (Fast, Deterministic)</option>
                <option value="openai">OpenAI (Real LLM)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Model
              </label>
              <select
                value={config.llm_model}
                onChange={(e) => handleChange('llm_model', e.target.value)}
                className="select"
              >
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Temperature
              </label>
              <input
                type="range"
                value={config.llm_temperature}
                onChange={(e) => handleChange('llm_temperature', parseFloat(e.target.value))}
                className="w-full"
                min="0"
                max="2"
                step="0.1"
              />
              <div className="text-xs text-secondary-400 mt-1">
                {config.llm_temperature}
              </div>
            </div>
          </div>
        </div>

        {/* Performance Settings */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <Settings className="w-5 h-5 text-green-400" />
            <h3 className="text-lg font-semibold text-white">Performance Settings</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Agents per Tick
              </label>
              <input
                type="number"
                value={config.agents_per_tick}
                onChange={(e) => handleChange('agents_per_tick', parseInt(e.target.value))}
                className="input"
                min="10"
                max="200"
                step="10"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Interactions per Tick
              </label>
              <input
                type="number"
                value={config.interactions_per_tick}
                onChange={(e) => handleChange('interactions_per_tick', parseInt(e.target.value))}
                className="input"
                min="10"
                max="500"
                step="10"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Memory Backend
              </label>
              <select
                value={config.memory_backend}
                onChange={(e) => handleChange('memory_backend', e.target.value)}
                className="select"
              >
                <option value="networkx">NetworkX (Fast)</option>
                <option value="neo4j">Neo4j (Scalable)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Vector Backend
              </label>
              <select
                value={config.vector_backend}
                onChange={(e) => handleChange('vector_backend', e.target.value)}
                className="select"
              >
                <option value="faiss">FAISS (Fast)</option>
                <option value="chroma">Chroma (Features)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Advanced Settings */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white">Advanced Settings</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Snapshot Frequency
              </label>
              <input
                type="number"
                value={config.snapshot_frequency}
                onChange={(e) => handleChange('snapshot_frequency', parseInt(e.target.value))}
                className="input"
                min="0"
                max="1000"
                step="10"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Snapshot Directory
              </label>
              <input
                type="text"
                value={config.snapshot_directory}
                onChange={(e) => handleChange('snapshot_directory', e.target.value)}
                className="input"
                placeholder="snapshots"
              />
            </div>
          </div>

          <div className="flex items-start justify-between rounded-lg border border-secondary-800 p-4">
            <div className="pr-4">
              <label htmlFor="enable-stimuli" className="block text-sm font-medium text-secondary-200">
                Environmental Stimuli
              </label>
              <p className="text-xs text-secondary-400 mt-1">
                Pull live real-world RSS data into the simulation. Non-deterministic —
                leave off for reproducible seeded runs.
              </p>
            </div>
            <input
              id="enable-stimuli"
              type="checkbox"
              checked={config.enable_environmental_stimuli}
              onChange={(e) => handleChange('enable_environmental_stimuli', e.target.checked)}
              className="mt-1 h-5 w-5 rounded border-secondary-700 bg-secondary-800 text-primary-600"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end space-x-3 pt-6 border-t border-secondary-800">
          <button
            type="button"
            onClick={onCancel}
            className="btn-secondary"
            disabled={loading}
          >
            Cancel
          </button>
          
          <button
            type="submit"
            className="btn-primary flex items-center space-x-2"
            disabled={loading}
          >
            {loading ? (
              <div className="spinner" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            <span>{loading ? 'Initializing...' : 'Initialize Simulation'}</span>
          </button>
        </div>
      </form>
    </div>
  )
}

export default SimulationConfig
