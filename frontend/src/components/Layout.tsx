import React, { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Play,
  Settings,
  BarChart3,
  Network,
  Globe,
  Info,
  Zap
} from 'lucide-react'
import { useSimulation } from '../state/SimulationContext'
import Sidebar from './Sidebar'
import Header from './Header'
import ControlPanel from './ControlPanel'

const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { state } = useSimulation()
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: BarChart3 },
    { name: 'Simulation', href: '/simulation', icon: Play },
    { name: 'Culture', href: '/culture', icon: Globe },
    { name: 'Economy', href: '/economy', icon: BarChart3 },
    { name: 'Network', href: '/network', icon: Network },
    { name: 'Environmental Stimuli', href: '/environmental-stimuli', icon: Zap },
    { name: 'About', href: '/about', icon: Info },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  const pageVariants = {
    initial: { opacity: 0, x: 20 },
    in: { opacity: 1, x: 0 },
    out: { opacity: 0, x: -20 }
  }

  const pageTransition = {
    type: 'tween',
    ease: 'anticipate',
    duration: 0.3
  }

  return (
    <div className="min-h-screen bg-secondary-950">
      {/* Mobile sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
              onClick={() => setSidebarOpen(false)}
            />
            <motion.div
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              className="fixed inset-y-0 left-0 z-50 w-64 lg:hidden"
            >
              <Sidebar navigation={navigation} onClose={() => setSidebarOpen(false)} />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <Sidebar navigation={navigation} />
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Header */}
        <Header onMenuClick={() => setSidebarOpen(true)} />

        {/* Control panel */}
        <ControlPanel />

        {/* Page content */}
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                initial="initial"
                animate="in"
                exit="out"
                variants={pageVariants}
                transition={pageTransition}
              >
                <Outlet />
              </motion.div>
            </AnimatePresence>
          </div>
        </main>
      </div>

      {/* Status indicator */}
      {state.status && (
        <div className="fixed bottom-4 right-4 z-30">
          <div className="flex items-center space-x-2 rounded-lg bg-secondary-800 px-3 py-2 text-sm">
            <div className={`h-2 w-2 rounded-full ${
              state.connected ? 'bg-green-400 animate-pulse' : 'bg-red-400'
            }`} />
            <span className="text-secondary-300">
              {state.status.state} • Tick {state.status.current_tick || 0}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

export default Layout
