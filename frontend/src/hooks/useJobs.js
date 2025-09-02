import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getJobs, getJob } from '../lib/api'

export const useJobs = () => {
  return useQuery({
    queryKey: ['jobs'],
    queryFn: getJobs,
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchOnWindowFocus: false,
  })
}

export const useJob = (jobId) => {
  return useQuery({
    queryKey: ['job', jobId],
    queryFn: () => getJob(jobId),
    enabled: !!jobId,
  })
}

export const useRefreshJobs = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async () => {
      // Force refetch of jobs
      await queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
  })
}
