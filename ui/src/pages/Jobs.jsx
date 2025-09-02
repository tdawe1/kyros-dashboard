import { useState } from 'react'
import { Search, Filter, Download, RefreshCw } from 'lucide-react'
import JobTable from '../ui/JobTable'
import { useRefreshJobs } from '../hooks/useJobs'

export default function Jobs() {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const refreshJobs = useRefreshJobs()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">Job Monitor</h1>
          <p className="text-gray-600 dark:text-gray-400">Monitor and manage your content repurposing jobs</p>
        </div>
        <button
          onClick={() => refreshJobs.mutate()}
          disabled={refreshJobs.isPending}
          className="bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed text-gray-900 dark:text-gray-100 px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
        >
          <RefreshCw className={`w-4 h-4 ${refreshJobs.isPending ? 'animate-spin' : ''}`} />
          <span>{refreshJobs.isPending ? 'Refreshing...' : 'Refresh'}</span>
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search jobs by client or URL..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div className="sm:w-48">
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
              >
                <option value="all">All Status</option>
                <option value="completed">Completed</option>
                <option value="processing">Processing</option>
                <option value="pending">Pending</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>

          {/* Export Button */}
          <button className="bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-gray-100 px-4 py-2 rounded-lg font-medium transition-colors border border-gray-300 dark:border-gray-600">
            <Download className="w-4 h-4 inline mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Job Table */}
      <JobTable />
    </div>
  )
}
