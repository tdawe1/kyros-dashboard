import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";

const fetchReadyStatus = async () => {
  const response = await fetch("/ready");
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};

export default function ReadyBadge() {
  const [isVisible, setIsVisible] = useState(true);

  const { data, error, isLoading } = useQuery({
    queryKey: ["ready-status"],
    queryFn: fetchReadyStatus,
    refetchInterval: 30000, // Poll every 30 seconds
    refetchIntervalInBackground: true,
    retry: 1,
    retryDelay: 1000,
  });

  // Hide badge if there's an error and it's not loading
  useEffect(() => {
    if (error && !isLoading) {
      setIsVisible(false);
    } else {
      setIsVisible(true);
    }
  }, [error, isLoading]);

  if (!isVisible) {
    return null;
  }

  const isUp = data?.status === "ok" && !error;
  const statusText = isUp ? "UP" : "DOWN";
  const statusColor = isUp 
    ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
    : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300";

  return (
    <span 
      className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${statusColor}`}
      data-testid="ready-badge"
    >
      /ready:{statusText}
    </span>
  );
}
