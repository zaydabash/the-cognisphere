import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Simulation from './pages/Simulation'
import Culture from './pages/Culture'
import Economy from './pages/Economy'
import Network from './pages/Network'
import Settings from './pages/Settings'
import About from './pages/About'
import EnvironmentalStimuli from './pages/EnvironmentalStimuli'
import { SimulationProvider } from './state/SimulationContext'

function App() {
  return (
    <SimulationProvider>
      <div className="min-h-screen bg-secondary-950 text-secondary-100">
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="simulation" element={<Simulation />} />
            <Route path="culture" element={<Culture />} />
            <Route path="economy" element={<Economy />} />
            <Route path="network" element={<Network />} />
            <Route path="environmental-stimuli" element={<EnvironmentalStimuli />} />
            <Route path="settings" element={<Settings />} />
            <Route path="about" element={<About />} />
          </Route>
        </Routes>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1e293b',
              color: '#f8fafc',
              border: '1px solid #334155',
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#f8fafc',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#f8fafc',
              },
            },
          }}
        />
      </div>
    </SimulationProvider>
  )
}

export default App
