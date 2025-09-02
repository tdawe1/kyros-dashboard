import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Monitor,
  Settings,
  X,
  FileText,
  BarChart3
} from 'lucide-react'
import clsx from 'clsx'
import ThemeToggle from './ThemeToggle'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Job Monitor', href: '/jobs', icon: Monitor },
  { name: 'Repurposer Studio', href: '/studio', icon: FileText },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function Sidebar({ isOpen, onClose }) {
  const location = useLocation()

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={clsx(
        'fixed inset-y-0 left-0 z-50 w-64 bg-navy-800 border-r border-navy-700 transform transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0 lg:inset-auto flex flex-col',
        isOpen ? 'translate-x-0' : '-translate-x-full'
      )}>
        {/* Header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-navy-700">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">K</span>
            </div>
            <span className="ml-3 text-white font-semibold">Kyros</span>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden text-navy-300 hover:text-white"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 mt-6 px-3">
          <div className="space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={clsx(
                    'group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                    isActive
                      ? 'bg-accent text-white'
                      : 'text-navy-300 hover:bg-navy-700 hover:text-white'
                  )}
                >
                  <item.icon
                    className={clsx(
                      'mr-3 h-5 w-5 flex-shrink-0',
                      isActive
                        ? 'text-white'
                        : 'text-navy-400 group-hover:text-white'
                    )}
                  />
                  {item.name}
                </Link>
              )
            })}
          </div>
        </nav>

        {/* Theme Toggle at Bottom */}
        <div className="p-4 border-t border-navy-700">
          <div className="flex items-center justify-between">
            <span className="text-sm text-navy-300">Theme</span>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </>
  )
}
