/**
 * Frontend Tool Registry
 *
 * This module manages the registration and discovery of frontend tools.
 * Each tool is self-contained with its own UI components and metadata.
 */

import repurposer from './tools/repurposer'

// Static registry of available tools
export const tools = [
  repurposer,
  // Future tools will be added here
  // hello,
  // summarizer,
  // etc.
]

/**
 * Get all enabled tools
 */
export const getEnabledTools = () => {
  return tools.filter(tool => tool.enabled !== false)
}

/**
 * Get a specific tool by name
 */
export const getTool = (toolName) => {
  return tools.find(tool => tool.name === toolName)
}

/**
 * Get tools by category
 */
export const getToolsByCategory = (category) => {
  return tools.filter(tool => tool.category === category)
}

/**
 * Get all available categories
 */
export const getCategories = () => {
  const categories = new Set(tools.map(tool => tool.category).filter(Boolean))
  return Array.from(categories)
}

/**
 * Check if a tool exists and is enabled
 */
export const isToolEnabled = (toolName) => {
  const tool = getTool(toolName)
  return tool && tool.enabled !== false
}

/**
 * Get tool metadata for display
 */
export const getToolMetadata = (toolName) => {
  const tool = getTool(toolName)
  if (!tool) return null

  return {
    name: tool.name,
    title: tool.title,
    description: tool.description,
    icon: tool.icon,
    category: tool.category,
    version: tool.version,
    enabled: tool.enabled !== false,
  }
}

/**
 * Get all tools metadata
 */
export const getAllToolsMetadata = () => {
  return tools.map(tool => getToolMetadata(tool.name)).filter(Boolean)
}
