import { useState, useEffect } from 'react'
import { X, Save, RotateCcw } from 'lucide-react'

export default function EditorModal({ isOpen, onClose, variant, onSave }) {
  const [editedText, setEditedText] = useState('')
  const [originalText, setOriginalText] = useState('')

  useEffect(() => {
    if (variant) {
      setEditedText(variant.text)
      setOriginalText(variant.text)
    }
  }, [variant])

  const handleSave = () => {
    if (onSave) {
      onSave({
        ...variant,
        text: editedText
      })
    }
    onClose()
  }

  const handleReset = () => {
    setEditedText(originalText)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      onClose()
    } else if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      handleSave()
    }
  }

  if (!isOpen || !variant) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
        />
        
        {/* Modal */}
        <div className="relative bg-navy-800 rounded-lg border border-navy-700 w-full max-w-4xl max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-navy-700">
            <div>
              <h3 className="text-xl font-semibold text-white">Edit Variant</h3>
              <p className="text-navy-300 text-sm mt-1">
                {variant.length} characters • {variant.readability} readability
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-navy-300 hover:text-white transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            <div className="space-y-4">
              {/* Text Editor */}
              <div>
                <label className="block text-sm font-medium text-navy-300 mb-2">
                  Content
                </label>
                <textarea
                  value={editedText}
                  onChange={(e) => setEditedText(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="w-full h-96 p-4 bg-navy-700 border border-navy-600 rounded-lg text-white placeholder-navy-400 focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent resize-none font-mono text-sm leading-relaxed"
                  placeholder="Enter your content here..."
                  autoFocus
                />
                <div className="flex justify-between items-center mt-2">
                  <span className="text-xs text-navy-400">
                    {editedText.length} characters
                  </span>
                  {editedText !== originalText && (
                    <span className="text-xs text-yellow-400">
                      Unsaved changes
                    </span>
                  )}
                </div>
              </div>

              {/* Preview */}
              <div>
                <label className="block text-sm font-medium text-navy-300 mb-2">
                  Preview
                </label>
                <div className="p-4 bg-navy-700 border border-navy-600 rounded-lg min-h-32">
                  <p className="text-navy-200 leading-relaxed whitespace-pre-wrap">
                    {editedText || 'Enter content to see preview...'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-6 border-t border-navy-700">
            <div className="flex items-center space-x-2">
              <button
                onClick={handleReset}
                disabled={editedText === originalText}
                className="bg-navy-700 hover:bg-navy-600 disabled:bg-navy-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2 border border-navy-600"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Reset</span>
              </button>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={onClose}
                className="bg-navy-700 hover:bg-navy-600 text-white px-4 py-2 rounded-lg font-medium transition-colors border border-navy-600"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={editedText === originalText}
                className="bg-accent hover:bg-accent/90 disabled:bg-navy-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
              >
                <Save className="w-4 h-4" />
                <span>Save Changes</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
