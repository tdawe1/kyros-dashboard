import { useMutation, useQueryClient } from '@tanstack/react-query'
import { generateContent, exportContent } from '../lib/api'

export const useGenerate = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: generateContent,
    onSuccess: () => {
      // Invalidate jobs and KPIs queries to refresh the data
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['kpis'] })
    },
  })
}

export const useExport = () => {
  return useMutation({
    mutationFn: exportContent,
  })
}
