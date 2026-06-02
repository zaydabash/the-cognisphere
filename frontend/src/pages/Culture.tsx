import React from 'react'
import { motion } from 'framer-motion'
import { Globe, BookOpen, Users, TrendingUp, Clock, Star } from 'lucide-react'
import { useSimulation } from '../state/SimulationContext'
import { MetricStrip } from '../components/MetricStrip'

const Culture: React.FC = () => {
  const { state } = useSimulation()

  const myths = state.culturalData?.myths || []
  const norms = state.culturalData?.norms || []
  const slang = state.culturalData?.slang || []
  const timeline = state.culturalData?.timeline || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Cultural Evolution</h1>
          <p className="text-secondary-400 mt-2">
            Myths, norms, and language evolution in your civilization
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-sm text-secondary-400">Cultural Diversity</div>
            <div className="text-2xl font-bold text-white">{myths.length + norms.length + slang.length}</div>
          </div>
        </div>
      </div>

      {/* Cultural Stats */}
      <MetricStrip
        metrics={[
          { label: 'Total Myths', value: myths.length, icon: BookOpen },
          { label: 'Active Norms', value: norms.length, icon: Users },
          { label: 'Slang Terms', value: slang.length, icon: Globe },
        ]}
      />

      {/* Myths Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card p-6"
      >
        <div className="flex items-center space-x-2 mb-6">
          <BookOpen className="w-5 h-5 text-green-400" />
          <h2 className="text-lg font-semibold text-white">Myths & Legends</h2>
        </div>

        {myths.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {myths.slice(0, 6).map((myth) => (
              <div key={myth.id} className="p-4 bg-secondary-800 rounded-lg border border-secondary-700">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-medium text-white">{myth.title}</h3>
                  <div className="flex items-center space-x-1 text-xs text-secondary-400">
                    <Star className="w-3 h-3" />
                    <span>{myth.popularity.toFixed(2)}</span>
                  </div>
                </div>
                <p className="text-sm text-secondary-300 mb-3 line-clamp-2">{myth.content}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                      {myth.theme}
                    </span>
                  </div>
                  <div className="text-xs text-secondary-500">
                    Tick {myth.tick_created}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <BookOpen className="w-12 h-12 text-secondary-600 mx-auto mb-4" />
            <p className="text-secondary-400">No myths have been created yet</p>
            <p className="text-sm text-secondary-500 mt-1">Start a simulation to see emergent myths</p>
          </div>
        )}
      </motion.div>

      {/* Norms Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card p-6"
      >
        <div className="flex items-center space-x-2 mb-6">
          <Users className="w-5 h-5 text-blue-400" />
          <h2 className="text-lg font-semibold text-white">Social Norms</h2>
        </div>

        {norms.length > 0 ? (
          <div className="space-y-4">
            {norms.map((norm) => (
              <div key={norm.id} className="p-4 bg-secondary-800 rounded-lg border border-secondary-700">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-medium text-white">{norm.title}</h3>
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">
                      {norm.norm_type}
                    </span>
                    <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                      {norm.status}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-secondary-300 mb-3">{norm.description}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="text-xs text-secondary-400">
                      Votes: {norm.votes_for}/{norm.votes_for + norm.votes_against}
                    </div>
                    <div className="text-xs text-secondary-400">
                      Compliance: {(norm.compliance_rate * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div className="text-xs text-secondary-500">
                    Tick {norm.tick_proposed}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Users className="w-12 h-12 text-secondary-600 mx-auto mb-4" />
            <p className="text-secondary-400">No social norms have been established</p>
            <p className="text-sm text-secondary-500 mt-1">Norms will emerge as agents interact</p>
          </div>
        )}
      </motion.div>

      {/* Slang Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="card p-6"
      >
        <div className="flex items-center space-x-2 mb-6">
          <Globe className="w-5 h-5 text-purple-400" />
          <h2 className="text-lg font-semibold text-white">Language Evolution</h2>
        </div>

        {slang.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {slang.slice(0, 12).map((term) => (
              <div key={term.id} className="p-4 bg-secondary-800 rounded-lg border border-secondary-700">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-medium text-white font-mono">{term.word}</h3>
                  <div className="flex items-center space-x-1 text-xs text-secondary-400">
                    <TrendingUp className="w-3 h-3" />
                    <span>{(term.adoption_rate * 100).toFixed(0)}%</span>
                  </div>
                </div>
                <p className="text-sm text-secondary-300 mb-3">{term.meaning}</p>
                <div className="flex items-center justify-between">
                  <div className="text-xs text-secondary-400">
                    {term.usage_context}
                  </div>
                  <div className="text-xs text-secondary-500">
                    Tick {term.tick_created}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Globe className="w-12 h-12 text-secondary-600 mx-auto mb-4" />
            <p className="text-secondary-400">No slang terms have emerged</p>
            <p className="text-sm text-secondary-500 mt-1">Language will evolve as agents communicate</p>
          </div>
        )}
      </motion.div>

      {/* Cultural Timeline */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="card p-6"
      >
        <div className="flex items-center space-x-2 mb-6">
          <Clock className="w-5 h-5 text-yellow-400" />
          <h2 className="text-lg font-semibold text-white">Cultural Timeline</h2>
        </div>

        {timeline.length > 0 ? (
          <div className="space-y-4 max-h-96 overflow-y-auto custom-scrollbar">
            {timeline.slice(-20).map((event, index) => (
              <div key={index} className="flex items-start space-x-4 p-3 bg-secondary-800 rounded-lg">
                <div className={`w-2 h-2 rounded-full mt-2 ${
                  event.type === 'myth' ? 'bg-green-400' :
                  event.type === 'norm' ? 'bg-blue-400' :
                  'bg-purple-400'
                }`} />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-white">{event.title}</h4>
                    <span className="text-xs text-secondary-500">Tick {event.tick}</span>
                  </div>
                  <p className="text-sm text-secondary-400 mt-1">
                    {event.type === 'myth' ? `Myth: ${event.theme}` :
                     event.type === 'norm' ? `Norm: ${event.norm_type}` :
                     'Cultural Event'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Clock className="w-12 h-12 text-secondary-600 mx-auto mb-4" />
            <p className="text-secondary-400">No cultural events yet</p>
            <p className="text-sm text-secondary-500 mt-1">Cultural evolution will be tracked here</p>
          </div>
        )}
      </motion.div>
    </div>
  )
}

export default Culture
