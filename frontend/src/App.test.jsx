import { render, screen } from '@testing-library/react'
import KPICards from './ui/KPICards'

// Mock the useKPIs hook
vi.mock('./hooks/useKPIs', () => ({
  useKPIs: () => ({
    data: {
      jobs_processed: 12,
      hours_saved: 24.5,
      avg_edit_min: 18,
      export_bundles: 9
    },
    isLoading: false,
    error: null
  })
}))

test('renders KPI cards with data', () => {
  render(<KPICards />)

  // Check if KPI cards are rendered with correct data
  expect(screen.getByText('Jobs Processed')).toBeInTheDocument()
  expect(screen.getByText('12')).toBeInTheDocument()
  expect(screen.getByText('Hours Saved')).toBeInTheDocument()
  expect(screen.getByText('24.5')).toBeInTheDocument()
  expect(screen.getByText('Avg Edit Time')).toBeInTheDocument()
  expect(screen.getByText('18 min')).toBeInTheDocument()
  expect(screen.getByText('Export Bundles')).toBeInTheDocument()
  expect(screen.getByText('9')).toBeInTheDocument()
})
