import React from 'react'
import { motion } from 'framer-motion'
import { BarChart3, TrendingUp, DollarSign, Activity, Zap, Users } from 'lucide-react'
import { useSimulation } from '../state/SimulationContext'
import { MetricStrip } from '../components/MetricStrip'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'

const Economy: React.FC = () => {
  const { state } = useSimulation()

  const economicData = state.economicData
  const realtime = state.status?.realtime
  const marketData = economicData?.market_summary
  const prices = marketData?.current_prices || {}
  const resources = marketData?.resources || {}

  // Mock historical data for charts
  const priceHistory = [
    { tick: 0, food: 1.0, energy: 1.2, artifacts: 2.0, influence: 3.0 },
    { tick: 10, food: 1.1, energy: 1.3, artifacts: 2.1, influence: 2.9 },
    { tick: 20, food: 1.2, energy: 1.1, artifacts: 2.3, influence: 3.1 },
    { tick: 30, food: 0.9, energy: 1.4, artifacts: 2.0, influence: 3.2 },
    { tick: 40, food: 1.3, energy: 1.2, artifacts: 2.5, influence: 2.8 },
  ]

  const tradeData = [
    { tick: 0, trades: 0 },
    { tick: 10, trades: 12 },
    { tick: 20, trades: 28 },
    { tick: 30, trades: 45 },
    { tick: 40, trades: 67 },
  ]

  const giniData = [
    { name: 'Low Inequality', value: 0.3, color: '#10b981' },
    { name: 'Medium Inequality', value: 0.5, color: '#f59e0b' },
    { name: 'High Inequality', value: 0.2, color: '#ef4444' },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Economic Overview</h1>
          <p className="text-secondary-400 mt-2">
            Market dynamics, trade patterns, and economic indicators
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-sm text-secondary-400">Gini Coefficient</div>
            <div className="text-2xl font-bold text-white">
              {economicData?.gini_coefficient?.toFixed(3) || '0.000'}
            </div>
          </div>
        </div>
      </div>

      {/* Economic Stats */}
      <MetricStrip
        metrics={[
          { label: 'Total Trades', value: economicData?.total_trades ?? realtime?.trade_count ?? 0, icon: DollarSign },
          { label: 'Market Clearings', value: realtime?.market_clearings ?? 0, icon: TrendingUp },
          { label: 'Active Events', value: economicData?.active_events || 0, icon: Zap },
          { label: 'Gini Coefficient', value: economicData?.gini_coefficient?.toFixed(3) || '0.000', icon: BarChart3 },
        ]}
      />

      {/* Price Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card p-6"
        >
          <h2 className="text-lg font-semibold text-white mb-4">Resource Price Trends</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={priceHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="tick" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1e293b', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }} 
              />
              <Line type="monotone" dataKey="food" stroke="#10b981" strokeWidth={2} />
              <Line type="monotone" dataKey="energy" stroke="#3b82f6" strokeWidth={2} />
              <Line type="monotone" dataKey="artifacts" stroke="#8b5cf6" strokeWidth={2} />
              <Line type="monotone" dataKey="influence" stroke="#f59e0b" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card p-6"
        >
          <h2 className="text-lg font-semibold text-white mb-4">Trade Volume</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={tradeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="tick" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1e293b', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }} 
              />
              <Bar dataKey="trades" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Market Prices */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="card p-6"
      >
        <h2 className="text-lg font-semibold text-white mb-4">Current Market Prices</h2>
        
        {Object.keys(prices).length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(prices).map(([resource, price]) => (
              <div key={resource} className="p-4 bg-secondary-800 rounded-lg border border-secondary-700">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-white capitalize">{resource}</h3>
                  <div className="text-sm text-secondary-400">
                    {resources[resource]?.current_value?.toFixed(2) || price.toFixed(2)}
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs text-secondary-400">
                    <span>Base Value</span>
                    <span>{resources[resource]?.base_value?.toFixed(2) || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between text-xs text-secondary-400">
                    <span>Scarcity</span>
                    <span>{resources[resource]?.scarcity_modifier?.toFixed(2) || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between text-xs text-secondary-400">
                    <span>Production</span>
                    <span>{resources[resource]?.production_rate?.toFixed(2) || 'N/A'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <BarChart3 className="w-12 h-12 text-secondary-600 mx-auto mb-4" />
            <p className="text-secondary-400">No market data available</p>
            <p className="text-sm text-secondary-500 mt-1">Start a simulation to see market dynamics</p>
          </div>
        )}
      </motion.div>

      {/* Economic Indicators */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="card p-6"
        >
          <h2 className="text-lg font-semibold text-white mb-4">Inequality Distribution</h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={giniData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {giniData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1e293b', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }} 
              />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="card p-6"
        >
          <h2 className="text-lg font-semibold text-white mb-4">Economic Health</h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-secondary-800 rounded-lg">
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4 text-green-400" />
                <span className="text-sm text-secondary-300">Trade Activity</span>
              </div>
              <span className="text-sm font-medium text-white">
                {((marketData?.active_trades || 0) + (marketData?.completed_trades || 0)) > 0 ? 'Healthy' : 'Low'}
              </span>
            </div>

            <div className="flex items-center justify-between p-3 bg-secondary-800 rounded-lg">
              <div className="flex items-center space-x-2">
                <Users className="w-4 h-4 text-blue-400" />
                <span className="text-sm text-secondary-300">Market Participation</span>
              </div>
              <span className="text-sm font-medium text-white">
                {state.agents.length > 0 ? 'Active' : 'Inactive'}
              </span>
            </div>

            <div className="flex items-center justify-between p-3 bg-secondary-800 rounded-lg">
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4 text-purple-400" />
                <span className="text-sm text-secondary-300">Economic Events</span>
              </div>
              <span className="text-sm font-medium text-white">
                {economicData?.active_events || 0} Active
              </span>
            </div>

            <div className="flex items-center justify-between p-3 bg-secondary-800 rounded-lg">
              <div className="flex items-center space-x-2">
                <BarChart3 className="w-4 h-4 text-red-400" />
                <span className="text-sm text-secondary-300">Inequality Level</span>
              </div>
              <span className="text-sm font-medium text-white">
                {economicData?.gini_coefficient ? 
                  (economicData.gini_coefficient > 0.7 ? 'High' : 
                   economicData.gini_coefficient > 0.4 ? 'Medium' : 'Low') : 'Unknown'}
              </span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Resource Production */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9 }}
        className="card p-6"
      >
        <h2 className="text-lg font-semibold text-white mb-4">Resource Production</h2>
        
        {economicData?.resource_production ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(economicData.resource_production).map(([resource, production]) => (
              <div key={resource} className="p-4 bg-secondary-800 rounded-lg border border-secondary-700">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-white capitalize">{resource}</h3>
                  <div className="text-sm text-secondary-400">
                    {production.toFixed(0)}
                  </div>
                </div>
                <div className="w-full bg-secondary-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-primary-500 to-accent-500 h-2 rounded-full"
                    style={{ width: `${Math.min(100, (production / 1000) * 100)}%` }}
                  />
                </div>
                <div className="text-xs text-secondary-400 mt-1">
                  Production Rate
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <TrendingUp className="w-12 h-12 text-secondary-600 mx-auto mb-4" />
            <p className="text-secondary-400">No production data available</p>
            <p className="text-sm text-secondary-500 mt-1">Resource production will be tracked here</p>
          </div>
        )}
      </motion.div>
    </div>
  )
}

export default Economy
