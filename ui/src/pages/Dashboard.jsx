import KPICards from '../ui/KPICards'
import JobTable from '../ui/JobTable'
import StudioPanel from '../ui/StudioPanel'

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-navy-300">Welcome to your kyros Repurposer dashboard</p>
      </div>
      
      {/* KPI Cards */}
      <KPICards />
      
      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Job Table - takes 2/3 of the width */}
        <div className="lg:col-span-2">
          <JobTable />
        </div>
        
        {/* Studio Panel - takes 1/3 of the width */}
        <div className="lg:col-span-1">
          <StudioPanel />
        </div>
      </div>
    </div>
  )
}
