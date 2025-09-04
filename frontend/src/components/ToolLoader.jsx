import React from "react";
import { useParams } from "react-router-dom";
import { getTool, listTools } from "../toolRegistry";

/**
 * ToolLoader Component
 *
 * Dynamically loads and renders tool panels based on the tool name.
 * This component provides a consistent interface for loading different tools.
 */
export default function ToolLoader({ ...props }) {
  const { toolName } = useParams();
  const tool = getTool(toolName);

  if (!tool) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="text-6xl mb-4">🔧</div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Tool Not Found
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            The tool "{toolName}" could not be found or is not available.
          </p>
          <div className="text-sm text-gray-500 dark:text-gray-500">
            Available tools:{" "}
            {listTools()
              .filter((tool) => tool.enabled)
              .map((tool) => tool.title)
              .join(", ") || "none"}
          </div>
        </div>
      </div>
    );
  }

  if (tool.enabled === false) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="text-6xl mb-4">🚫</div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Tool Disabled
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            The tool "{tool.title}" is currently disabled.
          </p>
        </div>
      </div>
    );
  }

  // Render the tool component
  const ToolComponent = tool.component;

  if (!ToolComponent) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Component Error
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            The tool "{tool.title}" component could not be loaded.
          </p>
        </div>
      </div>
    );
  }

  return <ToolComponent {...props} />;
}
