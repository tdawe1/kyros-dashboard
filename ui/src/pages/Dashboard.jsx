import KPICards from '../ui/KPICards'
import JobTable from '../ui/JobTable'
import StudioPanel from '../ui/StudioPanel'

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-navy-300">Welcome to your Kyros Repurposer dashboard</p>
      </div>

      {/* KPI Cards - Full width at top */}
      <KPICards />

      {/* Main content grid - Better proportions */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* Recent Jobs - Takes 3/4 width on large screens */}
        <div className="xl:col-span-3">
          <JobTable />
        </div>

        {/* Quick Studio - Takes 1/4 width on large screens */}
        <div className="xl:col-span-1">
          <StudioPanel />
        </div>
      </div>
    </div>
  )
}
