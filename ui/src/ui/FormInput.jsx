import { forwardRef } from 'react'
import { AlertCircle } from 'lucide-react'

const FormInput = forwardRef(({
  label,
  error,
  required,
  className = '',
  ...props
}, ref) => {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
          {required && <span className="text-red-400 ml-1">*</span>}
        </label>
      )}
      <div className="relative">
        <input
          ref={ref}
          className={`w-full px-3 py-2 bg-white dark:bg-gray-700 border rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-colors ${
            error
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300 dark:border-gray-600'
          } ${className}`}
          {...props}
        />
        {error && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <AlertCircle className="w-4 h-4 text-red-400" />
          </div>
        )}
      </div>
      {error && (
        <p className="text-sm text-red-400 flex items-center space-x-1">
          <AlertCircle className="w-3 h-3" />
          <span>{error}</span>
        </p>
      )}
    </div>
  )
})

FormInput.displayName = 'FormInput'

export default FormInput
