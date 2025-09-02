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
          <h1 className="text-3xl font-bold text-white mb-2">Job Monitor</h1>
          <p className="text-navy-300">Monitor and manage your content repurposing jobs</p>
        </div>
        <button 
          onClick={() => refreshJobs.mutate()}
          disabled={refreshJobs.isPending}
          className="bg-accent hover:bg-accent/90 disabled:bg-navy-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-colors"
        >
          <RefreshCw className={`w-4 h-4 inline mr-2 ${refreshJobs.isPending ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="bg-navy-800 rounded-lg p-6 border border-navy-700">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-navy-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search jobs by client or URL..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-navy-700 border border-navy-600 rounded-lg text-white placeholder-navy-400 focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
              />
            </div>
          </div>
          
          {/* Status Filter */}
          <div className="sm:w-48">
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-navy-400 w-4 h-4" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-navy-700 border border-navy-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent appearance-none"
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
          <button className="bg-navy-700 hover:bg-navy-600 text-white px-4 py-2 rounded-lg font-medium transition-colors border border-navy-600">
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
