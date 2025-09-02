import { useMutation, useQueryClient } from '@tanstack/react-query'
import { generateContent, exportContent } from '../lib/api'

export const useGenerate = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: generateContent,
    onSuccess: () => {
      // Invalidate jobs query to refresh the list
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
  })
}

export const useExport = () => {
  return useMutation({
    mutationFn: exportContent,
  })
}
