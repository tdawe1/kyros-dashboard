import { useQuery } from "@tanstack/react-query";

const fetchReadyStatus = async () => {
  const response = await fetch("/ready");
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};

export default function ReadyBadge() {
  const { data, error, isLoading } = useQuery({
    queryKey: ["ready-status"],
    queryFn: fetchReadyStatus,
    refetchInterval: 30000, // Poll every 30 seconds
    refetchIntervalInBackground: true,
    retry: 1,
    retryDelay: 1000,
  });

  // Map states to display text and colors
  const getStatusInfo = () => {
    if (isLoading) {
      return { text: "LOADING", color: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300" };
    }
    if (error) {
      return { text: "DOWN", color: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300" };
    }
    if (data?.status === "ok") {
      return { text: "UP", color: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300" };
    }
    return { text: "DOWN", color: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300" };
  };

  const { text: statusText, color: statusColor } = getStatusInfo();

  return (
    <span 
      className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${statusColor}`}
      data-testid="ready-badge"
    >
      /ready:{statusText}
    </span>
  );
}
