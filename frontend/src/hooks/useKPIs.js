import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getKPIs } from '../lib/api'

export const useKPIs = () => {
  return useQuery({
    queryKey: ['kpis'],
    queryFn: getKPIs,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  })
}

export const useRefreshKPIs = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async () => {
      // Force refetch of KPIs
      await queryClient.invalidateQueries({ queryKey: ['kpis'] })
    },
  })
}
