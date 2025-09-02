import { RefreshCw } from 'lucide-react'
import KPICards from '../ui/KPICards'
import JobTable from '../ui/JobTable'
import { useRefreshKPIs } from '../hooks/useKPIs'
import { useRefreshJobs } from '../hooks/useJobs'

export default function Dashboard() {
  const refreshKPIs = useRefreshKPIs()
  const refreshJobs = useRefreshJobs()

  const handleRefresh = async () => {
    try {
      await Promise.all([
        refreshKPIs.mutateAsync(),
        refreshJobs.mutateAsync()
      ])
    } catch (error) {
      console.error('Failed to refresh data:', error)
    }
  }

  const isRefreshing = refreshKPIs.isPending || refreshJobs.isPending

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">Dashboard</h1>
            <p className="text-gray-600 dark:text-gray-400">Welcome to your Kyros Repurposer dashboard</p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed text-gray-900 dark:text-gray-100 px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
          </button>
        </div>
      </div>

      {/* KPI Cards - Full width at top */}
      <KPICards />

      {/* Recent Jobs - Full width */}
      <JobTable />
    </div>
  )
}
