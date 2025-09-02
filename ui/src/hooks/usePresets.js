import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getPresets, createPreset, updatePreset, deletePreset } from '../lib/api'

export const usePresets = () => {
  return useQuery({
    queryKey: ['presets'],
    queryFn: getPresets,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

export const useCreatePreset = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createPreset,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['presets'] })
    },
  })
}

export const useUpdatePreset = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ presetId, data }) => updatePreset(presetId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['presets'] })
    },
  })
}

export const useDeletePreset = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: deletePreset,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['presets'] })
    },
  })
}
