import React from 'react'

export default function KyrosLogo({ className = "w-8 h-8", showText = true }) {
  return (
    <div className={`flex items-center ${className}`}>
      {/* Logo SVG */}
      <svg
        viewBox="0 0 120 32"
        className="h-8 w-auto"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Letter k */}
        <path
          d="M8 4h4v8l6-8h6l-8 8 8 8h-6l-6-8v8H8V4z"
          fill="currentColor"
          className="text-blue-600 dark:text-blue-400"
        />

        {/* Letter y */}
        <path
          d="M26 4h4v6l4-6h6l-6 8 6 8h-6l-4-6v6h-4V4z"
          fill="currentColor"
          className="text-blue-600 dark:text-blue-400"
        />

        {/* Letter r */}
        <path
          d="M44 4h6c2 0 3.5 1.5 3.5 3.5S52 11 50 11h-2v9h-4V4zm4 4v3h2c.5 0 1-.5 1-1.5S50.5 8 50 8h-2z"
          fill="currentColor"
          className="text-blue-600 dark:text-blue-400"
        />

        {/* Letter o */}
        <path
          d="M58 4h6c2 0 4 2 4 4v8c0 2-2 4-4 4h-6c-2 0-4-2-4-4V8c0-2 2-4 4-4zm0 4v8h6V8h-6z"
          fill="currentColor"
          className="text-blue-600 dark:text-blue-400"
        />

        {/* Teal circle overlapping the s */}
        <circle
          cx="78"
          cy="20"
          r="6"
          fill="#14B8A6"
          className="text-teal-500"
        />

        {/* Letter s (partially covered by circle) */}
        <path
          d="M72 4h6c2 0 3.5 1.5 3.5 3.5S80 11 78 11h-4c-1 0-2 1-2 2s1 2 2 2h4c2 0 3.5 1.5 3.5 3.5S80 22 78 22h-6c-2 0-3.5-1.5-3.5-3.5S70 15 72 15h4c1 0 2-1 2-2s-1-2-2-2h-4c-2 0-3.5-1.5-3.5-3.5S70 4 72 4z"
          fill="currentColor"
          className="text-blue-600 dark:text-blue-400"
        />
      </svg>

      {/* Text label */}
      {showText && (
        <span className="ml-3 text-gray-900 dark:text-gray-100 font-semibold text-lg">
          Kyros
        </span>
      )}
    </div>
  )
}

// Compact version for smaller spaces
export function KyrosLogoCompact({ className = "w-6 h-6" }) {
  return (
    <div className={`flex items-center ${className}`}>
      <svg
        viewBox="0 0 24 24"
        className="h-6 w-6"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Simplified logo - just the "k" with teal accent */}
        <path
          d="M4 4h3v6l4-6h3l-5 6 5 6h-3l-4-6v6H4V4z"
          fill="currentColor"
          className="text-blue-600 dark:text-blue-400"
        />
        <circle
          cx="18"
          cy="18"
          r="3"
          fill="#14B8A6"
          className="text-teal-500"
        />
      </svg>
    </div>
  )
}
