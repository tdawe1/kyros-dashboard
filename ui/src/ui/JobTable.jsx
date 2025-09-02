import { useState } from 'react'
import { ChevronUp, ChevronDown, MoreHorizontal, Play, Pause, Trash2, FileText } from 'lucide-react'
import { useJobs } from '../hooks/useJobs'

const statusColors = {
  completed: 'bg-green-500',
  processing: 'bg-blue-500',
  pending: 'bg-yellow-500',
  failed: 'bg-red-500'
}

const statusLabels = {
  completed: 'Completed',
  processing: 'Processing',
  pending: 'Pending',
  failed: 'Failed'
}

export default function JobTable() {
  const { data: jobs, isLoading, error } = useJobs()
  const [sortField, setSortField] = useState('created_at')
  const [sortDirection, setSortDirection] = useState('desc')

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getSortIcon = (field) => {
    if (sortField !== field) return null
    return sortDirection === 'asc' ?
      <ChevronUp className="w-4 h-4" /> :
      <ChevronDown className="w-4 h-4" />
  }

  if (isLoading) {
    return (
      <div className="bg-navy-800 rounded-lg border border-navy-700">
        <div className="px-6 py-4 border-b border-navy-700">
          <h3 className="text-lg font-semibold text-white">Recent Jobs</h3>
        </div>
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex space-x-4">
                <div className="h-4 bg-navy-700 rounded w-1/4"></div>
                <div className="h-4 bg-navy-700 rounded w-1/6"></div>
                <div className="h-4 bg-navy-700 rounded w-1/6"></div>
                <div className="h-4 bg-navy-700 rounded w-1/6"></div>
                <div className="h-4 bg-navy-700 rounded w-1/6"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-navy-800 rounded-lg border border-navy-700">
        <div className="px-6 py-4 border-b border-navy-700">
          <h3 className="text-lg font-semibold text-white">Recent Jobs</h3>
        </div>
        <div className="p-6">
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 bg-navy-700 rounded-full flex items-center justify-center">
              <FileText className="w-8 h-8 text-navy-400" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">No jobs yet</h3>
            <p className="text-navy-300 mb-4">Start by creating your first content repurposing job</p>
            <button className="bg-accent hover:bg-accent/90 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
              Create Job
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-navy-800 rounded-lg border border-navy-700">
      <div className="px-6 py-4 border-b border-navy-700">
        <h3 className="text-lg font-semibold text-white">Recent Jobs</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-navy-700">
            <tr>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-navy-300 uppercase tracking-wider cursor-pointer hover:text-white"
                onClick={() => handleSort('client')}
              >
                <div className="flex items-center space-x-1">
                  <span>Client</span>
                  {getSortIcon('client')}
                </div>
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-navy-300 uppercase tracking-wider cursor-pointer hover:text-white"
                onClick={() => handleSort('words')}
              >
                <div className="flex items-center space-x-1">
                  <span>Words</span>
                  {getSortIcon('words')}
                </div>
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-navy-300 uppercase tracking-wider cursor-pointer hover:text-white"
                onClick={() => handleSort('status')}
              >
                <div className="flex items-center space-x-1">
                  <span>Status</span>
                  {getSortIcon('status')}
                </div>
              </th>
              <th
                className="px-6 py-3 text-left text-xs font-medium text-navy-300 uppercase tracking-wider cursor-pointer hover:text-white"
                onClick={() => handleSort('created_at')}
              >
                <div className="flex items-center space-x-1">
                  <span>Created</span>
                  {getSortIcon('created_at')}
                </div>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-navy-300 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-navy-700">
            {jobs?.map((job) => (
              <tr key={job.id} className="hover:bg-navy-750">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-white">{job.client}</div>
                  <div className="text-sm text-navy-300 truncate max-w-xs">
                    {job.source_url}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-navy-300">
                  {job.words.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white ${statusColors[job.status]}`}>
                    {statusLabels[job.status]}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-navy-300">
                  {formatDate(job.created_at)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex items-center space-x-2">
                    {job.status === 'pending' && (
                      <button className="text-accent hover:text-accent/80">
                        <Play className="w-4 h-4" />
                      </button>
                    )}
                    {job.status === 'processing' && (
                      <button className="text-yellow-400 hover:text-yellow-300">
                        <Pause className="w-4 h-4" />
                      </button>
                    )}
                    <button className="text-navy-300 hover:text-white">
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
