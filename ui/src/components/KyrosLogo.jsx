import React from 'react'

export default function KyrosLogo({ className = "w-8 h-8", showText = true }) {
  return (
    <div className={`flex items-center ${className}`}>
      {/* Logo Image - different logos for light/dark mode */}
      <img
        src="/kyros-logo.svg"
        alt="Kyros Logo"
        className="h-24 w-auto dark:hidden"
      />
      <img
        src="/kyros-logo-white.svg"
        alt="Kyros Logo"
        className="h-24 w-auto hidden dark:block"
      />

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
          fill="#3B82F6"
        />
        <circle
          cx="18"
          cy="18"
          r="3"
          fill="#14B8A6"
        />
      </svg>
    </div>
  )
}
