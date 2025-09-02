import { TrendingUp, Clock, FileText, Download } from 'lucide-react'
import { useKPIs } from '../hooks/useKPIs'

const kpiConfig = [
  {
    title: 'Jobs Processed',
    key: 'jobs_processed',
    change: '+2.5%',
    changeType: 'positive',
    icon: FileText,
    color: 'bg-accent'
  },
  {
    title: 'Hours Saved',
    key: 'hours_saved',
    change: '+18.2%',
    changeType: 'positive',
    icon: Clock,
    color: 'bg-blue-500'
  },
  {
    title: 'Avg Edit Time',
    key: 'avg_edit_min',
    change: '-12.1%',
    changeType: 'positive',
    icon: TrendingUp,
    color: 'bg-green-500',
    suffix: ' min'
  },
  {
    title: 'Export Bundles',
    key: 'export_bundles',
    change: '+33.3%',
    changeType: 'positive',
    icon: Download,
    color: 'bg-purple-500'
  }
]

export default function KPICards() {
  const { data: kpis, isLoading, error } = useKPIs()

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {kpiConfig.map((kpi) => (
          <div key={kpi.title} className="bg-navy-800 rounded-lg p-6 border border-navy-700 animate-pulse">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <div className="h-4 bg-navy-700 rounded w-24"></div>
                <div className="h-8 bg-navy-700 rounded w-16"></div>
                <div className="h-3 bg-navy-700 rounded w-20"></div>
              </div>
              <div className="w-12 h-12 bg-navy-700 rounded-lg"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {kpiConfig.map((kpi) => {
          const Icon = kpi.icon
          return (
            <div key={kpi.title} className="bg-navy-800 rounded-lg p-6 border border-navy-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-navy-300 text-sm font-medium">{kpi.title}</p>
                  <p className="text-2xl font-bold text-white mt-1">--</p>
                  <p className="text-sm mt-1 text-navy-400">No data available</p>
                </div>
                <div className={`${kpi.color} p-3 rounded-lg opacity-50`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {kpiConfig.map((kpi) => {
        const Icon = kpi.icon
        const value = kpis?.[kpi.key] || 0
        const displayValue = kpi.suffix ? `${value}${kpi.suffix}` : value.toString()

        return (
          <div key={kpi.title} className="bg-navy-800 rounded-lg p-6 border border-navy-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-navy-300 text-sm font-medium">{kpi.title}</p>
                <p className="text-2xl font-bold text-white mt-1">{displayValue}</p>
                <p className={`text-sm mt-1 ${
                  kpi.changeType === 'positive' ? 'text-green-400' : 'text-red-400'
                }`}>
                  {kpi.change} from last month
                </p>
              </div>
              <div className={`${kpi.color} p-3 rounded-lg`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
