import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react'
import { apiClient } from '../api/client'
import toast from 'react-hot-toast'

// Types
export interface Agent {
  id: string
  name: string
  generation: number
  personality: {
    openness: number
    conscientiousness: number
    extraversion: number
    agreeableness: number
    neuroticism: number
  }
  resources: Record<string, number>
  influence: number
  faction_id?: string
  state: string
  satisfaction: number
  trust_relationships: Record<string, any>
}

export interface Myth {
  id: string
  creator_id: string
  title: string
  content: string
  theme: string
  characters: string[]
  motifs: string[]
  tick_created: number
  popularity: number
  influence: number
  version: number
  parent_id?: string
}

export interface Norm {
  id: string
  proposer_id: string
  title: string
  description: string
  norm_type: string
  tick_proposed: number
  votes_for: number
  votes_against: number
  status: string
  enforcement_strength: number
  compliance_rate: number
  violations: number
}

export interface Slang {
  id: string
  creator_id: string
  word: string
  meaning: string
  usage_context: string
  tick_created: number
  popularity: number
  adoption_rate: number
  parent_word?: string
}

export interface SimulationStatus {
  state: string
  current_tick: number
  start_time?: number
  end_time?: number
  duration?: number
  world_summary?: any
  scheduler_stats?: any
  realtime?: {
    current_tick: number
    agent_count: number
    faction_count: number
    active_events: number
    myth_count: number
    norm_count: number
    trade_count: number
    gini_coefficient: number
    alliance_count: number
    betrayal_count: number
    institution_count: number
    avg_reputation: number
    negotiations_successful: number
    market_clearings: number
    world_memories: number
  }
}

export interface NetworkData {
  nodes: Array<{
    id: string
    name: string
    faction_id?: string
    influence: number
    satisfaction: number
    personality: any
  }>
  edges: Array<{
    source: string
    target: string
    trust_level: number
    interaction_count: number
  }>
}

export interface EconomicData {
  market_summary: {
    name: string
    current_prices: Record<string, number>
    active_trades: number
    completed_trades: number
    resources: Record<string, any>
  }
  gini_coefficient: number
  active_events: number
  total_trades: number
  resource_production: Record<string, number>
}

export interface CulturalData {
  myths: Myth[]
  norms: Norm[]
  slang: Slang[]
  timeline: Array<{
    tick: number
    type: string
    title: string
    theme?: string
    norm_type?: string
    creator_id?: string
    proposer_id?: string
    popularity?: number
    compliance_rate?: number
  }>
}

// State interface
interface SimulationState {
  status: SimulationStatus | null
  agents: Agent[]
  networkData: NetworkData | null
  economicData: EconomicData | null
  culturalData: CulturalData | null
  loading: boolean
  error: string | null
  connected: boolean
}

// Action types
type SimulationAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_CONNECTED'; payload: boolean }
  | { type: 'SET_STATUS'; payload: SimulationStatus }
  | { type: 'SET_AGENTS'; payload: Agent[] }
  | { type: 'SET_NETWORK_DATA'; payload: NetworkData }
  | { type: 'SET_ECONOMIC_DATA'; payload: EconomicData }
  | { type: 'SET_CULTURAL_DATA'; payload: CulturalData }
  | { type: 'UPDATE_REALTIME_DATA' }

// Initial state
const initialState: SimulationState = {
  status: null,
  agents: [],
  networkData: null,
  economicData: null,
  culturalData: null,
  loading: false,
  error: null,
  connected: false,
}

// Reducer
function simulationReducer(state: SimulationState, action: SimulationAction): SimulationState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload }
    case 'SET_ERROR':
      return { ...state, error: action.payload }
    case 'SET_CONNECTED':
      return { ...state, connected: action.payload }
    case 'SET_STATUS':
      return { ...state, status: action.payload }
    case 'SET_AGENTS':
      return { ...state, agents: action.payload }
    case 'SET_NETWORK_DATA':
      return { ...state, networkData: action.payload }
    case 'SET_ECONOMIC_DATA':
      return { ...state, economicData: action.payload }
    case 'SET_CULTURAL_DATA':
      return { ...state, culturalData: action.payload }
    case 'UPDATE_REALTIME_DATA':
      return { ...state }
    default:
      return state
  }
}

// Context
const SimulationContext = createContext<{
  state: SimulationState
  dispatch: React.Dispatch<SimulationAction>
  initializeSimulation: (config: any) => Promise<boolean>
  controlSimulation: (action: string) => Promise<boolean>
  refreshData: () => Promise<void>
  startRealTimeUpdates: () => void
  stopRealTimeUpdates: () => void
} | null>(null)

// Provider component
export function SimulationProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(simulationReducer, initialState)
  const [updateInterval, setUpdateInterval] = React.useState<NodeJS.Timeout | null>(null)

  // Initialize simulation
  const initializeSimulation = async (config: any): Promise<boolean> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      dispatch({ type: 'SET_ERROR', payload: null })

      const response = await apiClient.post('/simulation/initialize', config)
      
      if (response.data.status === 'initialized') {
        toast.success('Simulation initialized successfully')
        await refreshData()
        return true
      } else {
        throw new Error('Failed to initialize simulation')
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to initialize simulation'
      dispatch({ type: 'SET_ERROR', payload: errorMessage })
      toast.error(errorMessage)
      return false
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  // Control simulation
  const controlSimulation = async (action: string): Promise<boolean> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      dispatch({ type: 'SET_ERROR', payload: null })

      const response = await apiClient.post('/simulation/control', { action })
      
      if (response.data.status) {
        toast.success(`Simulation ${action} successful`)
        await refreshData()
        return true
      } else {
        throw new Error(`Failed to ${action} simulation`)
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || `Failed to ${action} simulation`
      dispatch({ type: 'SET_ERROR', payload: errorMessage })
      toast.error(errorMessage)
      return false
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  // Refresh all data
  const refreshData = async (): Promise<void> => {
    try {
      dispatch({ type: 'SET_ERROR', payload: null })

      // Fetch all data in parallel
      const [statusResponse, agentsResponse, networkResponse, economicResponse, culturalResponse] = await Promise.allSettled([
        apiClient.get('/realtime/status'),
        apiClient.get('/agents'),
        apiClient.get('/realtime/network'),
        apiClient.get('/realtime/economy'),
        apiClient.get('/realtime/culture')
      ])

      // Update status
      if (statusResponse.status === 'fulfilled') {
        dispatch({ type: 'SET_STATUS', payload: statusResponse.value.data })
        dispatch({ type: 'SET_CONNECTED', payload: true })
      }

      // Update agents
      if (agentsResponse.status === 'fulfilled') {
        dispatch({ type: 'SET_AGENTS', payload: agentsResponse.value.data.agents || [] })
      }

      // Update network data
      if (networkResponse.status === 'fulfilled') {
        dispatch({ type: 'SET_NETWORK_DATA', payload: networkResponse.value.data })
      }

      // Update economic data
      if (economicResponse.status === 'fulfilled') {
        dispatch({ type: 'SET_ECONOMIC_DATA', payload: economicResponse.value.data })
      }

      // Update cultural data
      if (culturalResponse.status === 'fulfilled') {
        dispatch({ type: 'SET_CULTURAL_DATA', payload: culturalResponse.value.data })
      }

    } catch (error: any) {
      dispatch({ type: 'SET_ERROR', payload: error.message })
      dispatch({ type: 'SET_CONNECTED', payload: false })
    }
  }

  // Start real-time updates
  const startRealTimeUpdates = () => {
    if (updateInterval) return

    const interval = setInterval(async () => {
      await refreshData()
    }, 2000) // Update every 2 seconds

    setUpdateInterval(interval)
  }

  // Stop real-time updates
  const stopRealTimeUpdates = () => {
    if (updateInterval) {
      clearInterval(updateInterval)
      setUpdateInterval(null)
    }
  }

  // Cleanup on unmount (run once)
  useEffect(() => {
    return () => {
      stopRealTimeUpdates()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Initial data fetch
  useEffect(() => {
    refreshData()
  }, [])

  const contextValue = {
    state,
    dispatch,
    initializeSimulation,
    controlSimulation,
    refreshData,
    startRealTimeUpdates,
    stopRealTimeUpdates,
  }

  return (
    <SimulationContext.Provider value={contextValue}>
      {children}
    </SimulationContext.Provider>
  )
}

// Hook to use simulation context
// eslint-disable-next-line react-refresh/only-export-components
export function useSimulation() {
  const context = useContext(SimulationContext)
  if (!context) {
    throw new Error('useSimulation must be used within a SimulationProvider')
  }
  return context
}
