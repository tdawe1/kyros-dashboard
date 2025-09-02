import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";

// Query keys
const SCHEDULER_KEYS = {
  schedules: ["scheduler", "schedules"],
  schedule: (id) => ["scheduler", "schedule", id],
  runs: (id) => ["scheduler", "runs", id],
  run: (jobId, runId) => ["scheduler", "run", jobId, runId],
};

// API functions
const schedulerApi = {
  // Get all schedules
  getSchedules: async (params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.append("page", params.page);
    if (params.page_size) searchParams.append("page_size", params.page_size);
    if (params.status) searchParams.append("status", params.status);

    const response = await api.get(`/scheduler/?${searchParams.toString()}`);
    return response.data;
  },

  // Get schedule details
  getSchedule: async (id) => {
    const response = await api.get(`/scheduler/${id}`);
    return response.data;
  },

  // Create schedule
  createSchedule: async (data) => {
    const response = await api.post("/scheduler/", data);
    return response.data;
  },

  // Update schedule
  updateSchedule: async ({ id, ...data }) => {
    const response = await api.patch(`/scheduler/${id}`, data);
    return response.data;
  },

  // Delete schedule
  deleteSchedule: async (id) => {
    const response = await api.delete(`/scheduler/${id}`);
    return response.data;
  },

  // Run job now
  runNow: async ({ id, idempotency_key }) => {
    const response = await api.post(`/scheduler/${id}/run-now`, {
      idempotency_key,
    });
    return response.data;
  },

  // Get job runs
  getJobRuns: async (jobId, params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.append("page", params.page);
    if (params.page_size) searchParams.append("page_size", params.page_size);

    const response = await api.get(
      `/scheduler/${jobId}/runs?${searchParams.toString()}`,
    );
    return response.data;
  },

  // Get specific run
  getRun: async (jobId, runId) => {
    const response = await api.get(`/scheduler/${jobId}/runs/${runId}`);
    return response.data;
  },
};

// Hooks
export function useSchedules(params = {}) {
  return useQuery({
    queryKey: [...SCHEDULER_KEYS.schedules, params],
    queryFn: () => schedulerApi.getSchedules(params),
    staleTime: 30 * 1000, // 30 seconds
  });
}

export function useSchedule(id) {
  return useQuery({
    queryKey: SCHEDULER_KEYS.schedule(id),
    queryFn: () => schedulerApi.getSchedule(id),
    enabled: !!id,
  });
}

export function useCreateSchedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: schedulerApi.createSchedule,
    onSuccess: () => {
      // Invalidate and refetch schedules
      queryClient.invalidateQueries({ queryKey: SCHEDULER_KEYS.schedules });
    },
  });
}

export function useUpdateSchedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: schedulerApi.updateSchedule,
    onSuccess: (data, variables) => {
      // Invalidate schedules list
      queryClient.invalidateQueries({ queryKey: SCHEDULER_KEYS.schedules });
      // Update specific schedule cache
      queryClient.setQueryData(SCHEDULER_KEYS.schedule(variables.id), data);
    },
  });
}

export function useDeleteSchedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: schedulerApi.deleteSchedule,
    onSuccess: (data, variables) => {
      // Invalidate schedules list
      queryClient.invalidateQueries({ queryKey: SCHEDULER_KEYS.schedules });
      // Remove specific schedule from cache
      queryClient.removeQueries({
        queryKey: SCHEDULER_KEYS.schedule(variables),
      });
    },
  });
}

export function useRunNow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: schedulerApi.runNow,
    onSuccess: (data, variables) => {
      // Invalidate schedules to refresh next run time
      queryClient.invalidateQueries({ queryKey: SCHEDULER_KEYS.schedules });
      // Invalidate specific schedule
      queryClient.invalidateQueries({
        queryKey: SCHEDULER_KEYS.schedule(variables.id),
      });
      // Invalidate runs for this job
      queryClient.invalidateQueries({
        queryKey: SCHEDULER_KEYS.runs(variables.id),
      });
    },
  });
}

export function useJobRuns(jobId, params = {}) {
  return useQuery({
    queryKey: [...SCHEDULER_KEYS.runs(jobId), params],
    queryFn: () => schedulerApi.getJobRuns(jobId, params),
    enabled: !!jobId,
  });
}

export function useRun(jobId, runId) {
  return useQuery({
    queryKey: SCHEDULER_KEYS.run(jobId, runId),
    queryFn: () => schedulerApi.getRun(jobId, runId),
    enabled: !!jobId && !!runId,
  });
}

// Utility hooks
export function useSchedulerStats() {
  const { data: schedules } = useSchedules();

  if (!schedules) {
    return {
      total: 0,
      active: 0,
      paused: 0,
      completed: 0,
      failed: 0,
    };
  }

  const stats = schedules.jobs?.reduce(
    (acc, schedule) => {
      acc.total++;
      acc[schedule.status] = (acc[schedule.status] || 0) + 1;
      return acc;
    },
    { total: 0, active: 0, paused: 0, completed: 0, failed: 0 },
  ) || {
    total: 0,
    active: 0,
    paused: 0,
    completed: 0,
    failed: 0,
  };

  return stats;
}
