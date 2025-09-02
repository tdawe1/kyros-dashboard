import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Monitor,
  Settings,
  X,
  FileText,
  BarChart3,
  MessageCircle,
  Calendar
} from 'lucide-react'
import clsx from 'clsx'
import ThemeToggle from './ThemeToggle'
import { getEnabledTools } from '../toolRegistry'
import KyrosLogo from '../components/KyrosLogo'

// Icon mapping for tools
const iconMap = {
  FileText: FileText,
  MessageCircle: MessageCircle,
  // Add more icon mappings as needed
}

// Static navigation items
const staticNavigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Studio', href: '/studio', icon: FileText },
  { name: 'Job Monitor', href: '/jobs', icon: Monitor },
  { name: 'Scheduler', href: '/scheduler', icon: Calendar },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
]

// Generate dynamic navigation from tools
const getToolNavigation = () => {
  return getEnabledTools().map(tool => ({
    name: tool.title,
    href: `/tools/${tool.name}`,
    icon: iconMap[tool.icon] || FileText, // Default to FileText if icon not found
    tool: true,
  }))
}

export default function Sidebar({ isOpen, onClose }) {
  const location = useLocation()

  // Combine static and dynamic navigation
  const navigation = [
    ...staticNavigation,
    ...getToolNavigation(),
  ]

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
        'fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transform transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0 lg:inset-auto flex flex-col',
        isOpen ? 'translate-x-0' : '-translate-x-full'
      )}>
        {/* Header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <KyrosLogo showText={false} className="w-32 h-32" />
          </div>
          <button
            onClick={onClose}
            className="lg:hidden text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 mt-6 px-3">
          <div className="space-y-1">
            {navigation.map((item) => {
              // Handle tool routes - check if current path starts with tool path
              const isActive = item.tool
                ? location.pathname.startsWith(item.href)
                : location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={clsx(
                    'group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                    isActive
                      ? 'bg-accent text-white'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'
                  )}
                >
                  <item.icon
                    className={clsx(
                      'mr-3 h-5 w-5 flex-shrink-0',
                      isActive
                        ? 'text-white'
                        : 'text-gray-500 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-100'
                    )}
                  />
                  {item.name}
                </Link>
              )
            })}
          </div>
        </nav>

        {/* Theme Toggle at Bottom */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Theme</span>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </>
  )
}
