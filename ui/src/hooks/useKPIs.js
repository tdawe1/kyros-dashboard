import { useQuery } from '@tanstack/react-query'
import { getKPIs } from '../lib/api'

export const useKPIs = () => {
  return useQuery({
    queryKey: ['kpis'],
    queryFn: getKPIs,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
  })
}
