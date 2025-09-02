import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react'

const toastIcons = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info
}

const toastColors = {
  success: 'bg-green-900/20 border-green-500/20 text-green-400',
  error: 'bg-red-900/20 border-red-500/20 text-red-400',
  warning: 'bg-yellow-900/20 border-yellow-500/20 text-yellow-400',
  info: 'bg-blue-900/20 border-blue-500/20 text-blue-400'
}

export default function ToastContainer({ toasts, onRemove }) {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {toasts.map((toast) => {
        const Icon = toastIcons[toast.type]
        const colorClass = toastColors[toast.type]

        return (
          <div
            key={toast.id}
            className={`${colorClass} border rounded-lg p-4 min-w-80 max-w-96 shadow-lg backdrop-blur-sm transition-all duration-300 transform`}
          >
            <div className="flex items-start space-x-3">
              <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium">{toast.message}</p>
                {toast.description && (
                  <p className="text-xs opacity-80 mt-1">{toast.description}</p>
                )}
              </div>
              <button
                onClick={() => onRemove(toast.id)}
                className="text-current opacity-60 hover:opacity-100 transition-opacity"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )
      })}
    </div>
  )
}
