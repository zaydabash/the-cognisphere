import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Globe, 
  TrendingUp, 
  TrendingDown, 
  Zap, 
  Brain, 
  Activity,
  RefreshCw,
  BarChart3,
  Clock,
  Tag,
  Users,
  DollarSign,
  Heart
} from 'lucide-react';
import { apiClient } from '../api/client';
import { MetricStrip } from '../components/MetricStrip';

interface EnvironmentalStimulus {
  id: string;
  type: string;
  title: string;
  content: string;
  source: string;
  timestamp: string;
  intensity: number;
  sentiment: number;
  keywords: string[];
  cultural_impact: number;
  economic_impact: number;
  social_impact: number;
}

interface StimuliStatus {
  enabled: boolean;
  active_stimuli_count: number;
  cultural_divergence: {
    mirroring_factor: number;
    divergence_rate: number;
    reality_baseline: any;
    active_stimuli_count: number;
    historical_stimuli_count: number;
  };
}

const EnvironmentalStimuliDashboard: React.FC = () => {
  const [stimuli, setStimuli] = useState<EnvironmentalStimulus[]>([]);
  const [status, setStatus] = useState<StimuliStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>('all');
  const [refreshing, setRefreshing] = useState(false);

  const stimulusTypes = [
    { value: 'all', label: 'All Types', icon: Globe, color: 'text-gray-500' },
    { value: 'news', label: 'News', icon: Activity, color: 'text-blue-500' },
    { value: 'technological', label: 'Technology', icon: Zap, color: 'text-purple-500' },
    { value: 'scientific', label: 'Science', icon: Brain, color: 'text-green-500' },
    { value: 'economic', label: 'Economy', icon: DollarSign, color: 'text-yellow-500' },
    { value: 'cultural', label: 'Culture', icon: Heart, color: 'text-pink-500' },
    { value: 'social_media', label: 'Social', icon: Users, color: 'text-indigo-500' },
    { value: 'weather', label: 'Weather', icon: Globe, color: 'text-cyan-500' }
  ];

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [stimuliResponse, statusResponse] = await Promise.all([
        apiClient.get('/stimuli/active'),
        apiClient.get('/stimuli/status')
      ]);
      
      setStimuli(stimuliResponse.data.stimuli || []);
      setStatus(statusResponse.data);
    } catch (error) {
      console.error('Error fetching stimuli data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await apiClient.post('/stimuli/fetch');
      await fetchData();
    } catch (error) {
      console.error('Error refreshing stimuli:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const filteredStimuli = filterType === 'all' 
    ? stimuli 
    : stimuli.filter(s => s.type === filterType);

  const getIntensityColor = (intensity: number) => {
    if (intensity >= 0.8) return 'text-red-500 bg-red-100';
    if (intensity >= 0.6) return 'text-orange-500 bg-orange-100';
    if (intensity >= 0.3) return 'text-yellow-500 bg-yellow-100';
    return 'text-green-500 bg-green-100';
  };

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.3) return 'text-green-600';
    if (sentiment < -0.3) return 'text-red-600';
    return 'text-gray-600';
  };

  const getSentimentIcon = (sentiment: number) => {
    if (sentiment > 0.3) return <TrendingUp className="w-4 h-4" />;
    if (sentiment < -0.3) return <TrendingDown className="w-4 h-4" />;
    return <Activity className="w-4 h-4" />;
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Environmental Stimuli</h1>
          <p className="text-secondary-300 mt-2">
            Real-world data shaping the digital civilization
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Status Overview */}
      {status && (
        <MetricStrip
          metrics={[
            { label: 'Active Stimuli', value: status.active_stimuli_count, icon: Activity },
            { label: 'Mirroring', value: `${(status.cultural_divergence.mirroring_factor * 100).toFixed(1)}%`, icon: Brain },
            { label: 'Divergence Rate', value: `${(status.cultural_divergence.divergence_rate * 100).toFixed(2)}%`, icon: Zap },
            { label: 'Historical', value: status.cultural_divergence.historical_stimuli_count, icon: BarChart3 },
          ]}
        />
      )}

      {/* Cultural Divergence Analysis */}
      {status && (
        <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 p-6 rounded-lg border border-purple-500/20">
          <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
            <Brain className="w-5 h-5 text-purple-400" />
            <span>Cultural Evolution Analysis</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-secondary-300 text-sm mb-2">
                <strong>Mirroring Factor:</strong> {(status.cultural_divergence.mirroring_factor * 100).toFixed(1)}%
              </p>
              <p className="text-secondary-400 text-xs">
                The civilization mirrors {(status.cultural_divergence.mirroring_factor * 100).toFixed(1)}% of real-world patterns
              </p>
            </div>
            <div>
              <p className="text-secondary-300 text-sm mb-2">
                <strong>Divergence Rate:</strong> {(status.cultural_divergence.divergence_rate * 100).toFixed(2)}%
              </p>
              <p className="text-secondary-400 text-xs">
                Culture diverges at {(status.cultural_divergence.divergence_rate * 100).toFixed(2)}% per stimulus, creating a "future version"
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2">
        {stimulusTypes.map((type) => {
          const Icon = type.icon;
          const isActive = filterType === type.value;
          const count = type.value === 'all' 
            ? stimuli.length 
            : stimuli.filter(s => s.type === type.value).length;
          
          return (
            <button
              key={type.value}
              onClick={() => setFilterType(type.value)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                isActive 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-secondary-800 text-secondary-300 hover:bg-secondary-700'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : type.color}`} />
              <span>{type.label}</span>
              <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                isActive ? 'bg-primary-500' : 'bg-secondary-600'
              }`}>
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Stimuli List */}
      <div className="space-y-4">
        <AnimatePresence>
          {filteredStimuli.map((stimulus, index) => (
            <motion.div
              key={stimulus.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ delay: index * 0.1 }}
              className="bg-secondary-800 p-6 rounded-lg border border-secondary-700 hover:border-primary-500/50 transition-colors"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-white mb-2">
                    {stimulus.title}
                  </h3>
                  <p className="text-secondary-300 text-sm mb-3">
                    {stimulus.content}
                  </p>
                </div>
                <div className="flex items-center space-x-2 ml-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getIntensityColor(stimulus.intensity)}`}>
                    {stimulus.intensity >= 0.8 ? 'Critical' : 
                     stimulus.intensity >= 0.6 ? 'High' : 
                     stimulus.intensity >= 0.3 ? 'Medium' : 'Low'}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="flex items-center space-x-2">
                  <div className={`${getSentimentColor(stimulus.sentiment)}`}>
                    {getSentimentIcon(stimulus.sentiment)}
                  </div>
                  <span className="text-sm text-secondary-300">
                    Sentiment: {(stimulus.sentiment * 100).toFixed(0)}%
                  </span>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Heart className="w-4 h-4 text-pink-500" />
                  <span className="text-sm text-secondary-300">
                    Cultural: {(stimulus.cultural_impact * 100).toFixed(0)}%
                  </span>
                </div>
                
                <div className="flex items-center space-x-2">
                  <DollarSign className="w-4 h-4 text-yellow-500" />
                  <span className="text-sm text-secondary-300">
                    Economic: {(stimulus.economic_impact * 100).toFixed(0)}%
                  </span>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Users className="w-4 h-4 text-indigo-500" />
                  <span className="text-sm text-secondary-300">
                    Social: {(stimulus.social_impact * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 text-sm text-secondary-400">
                  <div className="flex items-center space-x-1">
                    <Clock className="w-4 h-4" />
                    <span>{formatTimestamp(stimulus.timestamp)}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Activity className="w-4 h-4" />
                    <span>{stimulus.source}</span>
                  </div>
                </div>
                
                <div className="flex flex-wrap gap-1">
                  {stimulus.keywords.slice(0, 5).map((keyword, idx) => (
                    <span
                      key={idx}
                      className="flex items-center space-x-1 px-2 py-1 bg-secondary-700 text-secondary-300 text-xs rounded-full"
                    >
                      <Tag className="w-3 h-3" />
                      <span>{keyword}</span>
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {filteredStimuli.length === 0 && (
        <div className="text-center py-12">
          <Globe className="w-12 h-12 text-secondary-600 mx-auto mb-4" />
          <p className="text-secondary-400">No environmental stimuli found</p>
          <p className="text-secondary-500 text-sm mt-2">
            Try refreshing or check if the stimuli system is enabled
          </p>
        </div>
      )}
    </div>
  );
};

export default EnvironmentalStimuliDashboard;
