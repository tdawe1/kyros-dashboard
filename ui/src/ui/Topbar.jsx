import { Menu, Bell, User } from 'lucide-react'
import { useLocation } from 'react-router-dom'

const pageTitles = {
  '/': 'Dashboard',
  '/jobs': 'Job Monitor',
  '/studio': 'Repurposer Studio',
  '/settings': 'Settings'
}

export default function Topbar({ onMenuClick }) {
  const location = useLocation()
  const pageTitle = pageTitles[location.pathname] || 'Dashboard'

  return (
    <div className="sticky top-0 z-30 bg-gradient-kyros border-b border-navy-800">
      <div className="flex items-center justify-between h-16 px-6">
        {/* Mobile menu button */}
        <button
          onClick={onMenuClick}
          className="lg:hidden text-navy-300 hover:text-white"
        >
          <Menu className="w-6 h-6" />
        </button>
        
        {/* Page title - dynamic based on route */}
        <div className="flex-1 lg:flex-none">
          <h1 className="text-xl font-semibold text-white">{pageTitle}</h1>
        </div>
        
        {/* Right side actions */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="text-navy-300 hover:text-white relative">
            <Bell className="w-6 h-6" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-accent rounded-full"></span>
          </button>
          
          {/* User menu */}
          <button className="flex items-center space-x-2 text-navy-300 hover:text-white">
            <div className="w-8 h-8 bg-navy-700 rounded-full flex items-center justify-center">
              <User className="w-4 h-4" />
            </div>
            <span className="hidden md:block text-sm">Admin</span>
          </button>
        </div>
      </div>
    </div>
  )
}
