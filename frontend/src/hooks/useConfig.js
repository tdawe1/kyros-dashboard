import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

const VALID_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-mini"];

export function useConfig() {
  const { data: config, isLoading } = useQuery({
    queryKey: ["config"],
    queryFn: async () => {
      const response = await api.get("/api/config");
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  return {
    config,
    isLoading,
    validModels: VALID_MODELS,
    isDemoMode: config?.api_mode === "demo",
    defaultModel: config?.default_model || "gpt-4o-mini",
  };
}

export function useModelSelection() {
  const { defaultModel } = useConfig();
  const [selectedModel, setSelectedModel] = useState(() => {
    // Initialize from localStorage or use default
    const saved = localStorage.getItem("selectedModel");
    return saved || defaultModel || "gpt-4o-mini";
  });

  useEffect(() => {
    // Update selected model when default changes
    if (defaultModel && !localStorage.getItem("selectedModel")) {
      setSelectedModel(defaultModel);
    }
  }, [defaultModel]);

  const updateModel = model => {
    if (VALID_MODELS.includes(model)) {
      setSelectedModel(model);
      try {
        localStorage.setItem("selectedModel", model);
      } catch (error) {
        console.warn("Failed to save model selection to localStorage:", error);
      }
    }
  };

  return {
    selectedModel,
    updateModel,
    validModels: VALID_MODELS,
  };
}
