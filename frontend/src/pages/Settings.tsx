import React from 'react'
import { motion } from 'framer-motion'
import { Settings as SettingsIcon, Save, RotateCcw, Download, Upload } from 'lucide-react'
import toast from 'react-hot-toast'
import { useSimulation } from '../state/SimulationContext'

const Settings: React.FC = () => {
  const { state } = useSimulation()

  const handleSaveSettings = () => {
    toast('Settings are applied per-run via the simulation config (not yet persisted).')
  }

  const handleResetSettings = () => {
    toast('Settings reset is not yet implemented.')
  }

  const handleExportData = () => {
    toast('Data export is not yet implemented.')
  }

  const handleImportData = () => {
    toast('Data import is not yet implemented.')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Settings</h1>
          <p className="text-secondary-400 mt-2">
            Configure simulation parameters and system preferences
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={handleSaveSettings}
            className="btn-primary flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Save Settings</span>
          </button>
        </div>
      </div>

      {/* General Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card p-6"
      >
        <div className="flex items-center space-x-2 mb-6">
          <SettingsIcon className="w-5 h-5 text-primary-400" />
          <h2 className="text-lg font-semibold text-white">General Settings</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-secondary-200 mb-2">
              Update Frequency (seconds)
            </label>
            <input
              type="number"
              defaultValue="2"
              className="input"
              min="1"
              max="60"
            />
            <p className="text-xs text-secondary-400 mt-1">
              How often to refresh simulation data
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-200 mb-2">
              Max History Items
            </label>
            <input
              type="number"
              defaultValue="1000"
              className="input"
              min="100"
              max="10000"
            />
            <p className="text-xs text-secondary-400 mt-1">
              Maximum number of historical data points to keep
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-200 mb-2">
              Theme
            </label>
            <select className="select">
              <option value="dark">Dark</option>
              <option value="light">Light</option>
              <option value="auto">Auto</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-200 mb-2">
              Language
            </label>
            <select className="select">
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
            </select>
          </div>
        </div>
      </motion.div>

      {/* Visualization Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card p-6"
      >
        <h2 className="text-lg font-semibold text-white mb-6">Visualization Settings</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-secondary-200 mb-2">
              Network Layout
            </label>
            <select className="select">
              <option value="force">Force Directed</option>
              <option value="circle">Circle</option>
              <option value="grid">Grid</option>
              <option value="hierarchical">Hierarchical</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-200 mb-2">
              Node Size Scale
            </label>
            <input
              type="range"
              defaultValue="1"
              className="w-full"
              min="0.5"
              max="2"
              step="0.1"
            />
            <p className="text-xs text-secondary-400 mt-1">
              Scale factor for node sizes in network visualization
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-200 mb-2">
              Edge Opacity
            </label>
            <input
              type="range"
              defaultValue="0.6"
              className="w-full"
              min="0.1"
              max="1"
              step="0.1"
            />
            <p className="text-xs text-secondary-400 mt-1">
              Transparency level for network edges
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-200 mb-2">
              Animation Speed
            </label>
            <select className="select">
              <option value="slow">Slow</option>
              <option value="normal">Normal</option>
              <option value="fast">Fast</option>
              <option value="instant">Instant</option>
            </select>
          </div>
        </div>
      </motion.div>

      {/* Data Management */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card p-6"
      >
        <h2 className="text-lg font-semibold text-white mb-6">Data Management</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-secondary-300">Export Data</h3>
            <div className="space-y-2">
              <button
                onClick={handleExportData}
                className="btn-secondary w-full flex items-center justify-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Export Simulation Data</span>
              </button>
              <button
                onClick={handleExportData}
                className="btn-secondary w-full flex items-center justify-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Export Agent Network</span>
              </button>
              <button
                onClick={handleExportData}
                className="btn-secondary w-full flex items-center justify-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Export Cultural Data</span>
              </button>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-sm font-medium text-secondary-300">Import Data</h3>
            <div className="space-y-2">
              <button
                onClick={handleImportData}
                className="btn-secondary w-full flex items-center justify-center space-x-2"
              >
                <Upload className="w-4 h-4" />
                <span>Import Simulation Data</span>
              </button>
              <button
                onClick={handleImportData}
                className="btn-secondary w-full flex items-center justify-center space-x-2"
              >
                <Upload className="w-4 h-4" />
                <span>Import Agent Network</span>
              </button>
              <button
                onClick={handleImportData}
                className="btn-secondary w-full flex items-center justify-center space-x-2"
              >
                <Upload className="w-4 h-4" />
                <span>Import Cultural Data</span>
              </button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* System Information */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card p-6"
      >
        <h2 className="text-lg font-semibold text-white mb-6">System Information</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-medium text-secondary-300 mb-4">Connection Status</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-secondary-400">Backend Status</span>
                <span className={`${state.connected ? 'text-green-400' : 'text-red-400'}`}>
                  {state.connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-secondary-400">Last Update</span>
                <span className="text-white">{new Date().toLocaleTimeString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-secondary-400">Simulation State</span>
                <span className="text-white">{state.status?.state || 'Unknown'}</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-secondary-300 mb-4">Performance</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-secondary-400">Active Agents</span>
                <span className="text-white">{state.agents.length}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-secondary-400">Current Tick</span>
                <span className="text-white">{state.status?.current_tick || 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-secondary-400">Uptime</span>
                <span className="text-white">
                  {state.status?.duration ? `${state.status.duration.toFixed(1)}s` : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Danger Zone */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card p-6 border-red-500/50 bg-red-500/5"
      >
        <h2 className="text-lg font-semibold text-white mb-6">Danger Zone</h2>

        <div className="space-y-4">
          <div className="p-4 bg-red-500/10 rounded-lg border border-red-500/20">
            <h3 className="text-sm font-medium text-red-400 mb-2">Reset All Settings</h3>
            <p className="text-sm text-secondary-400 mb-3">
              This will reset all settings to their default values. This action cannot be undone.
            </p>
            <button
              onClick={handleResetSettings}
              className="btn-ghost text-red-400 hover:text-red-300 hover:bg-red-900/20 flex items-center space-x-2"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Reset Settings</span>
            </button>
          </div>

          <div className="p-4 bg-red-500/10 rounded-lg border border-red-500/20">
            <h3 className="text-sm font-medium text-red-400 mb-2">Clear All Data</h3>
            <p className="text-sm text-secondary-400 mb-3">
              This will clear all simulation data and reset the system to its initial state.
            </p>
            <button
              onClick={() => {
                if (confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
                  toast('Clear-all-data is not yet implemented.')
                }
              }}
              className="btn-ghost text-red-400 hover:text-red-300 hover:bg-red-900/20 flex items-center space-x-2"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Clear All Data</span>
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default Settings
