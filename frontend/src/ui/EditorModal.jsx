import { useState, useEffect } from "react";
import { X, Save, RotateCcw } from "lucide-react";

export default function EditorModal({ isOpen, onClose, variant, onSave }) {
  const [editedText, setEditedText] = useState("");
  const [originalText, setOriginalText] = useState("");

  useEffect(() => {
    if (variant?.text) {
      setEditedText(variant.text);
      setOriginalText(variant.text);
    }
  }, [variant]);

  const handleSave = () => {
    if (onSave && variant) {
      onSave({
        ...variant,
        text: editedText,
      });
    }
    onClose();
  };

  const handleReset = () => {
    setEditedText(originalText);
  };

  const handleKeyDown = e => {
    if (e.key === "Escape") {
      onClose();
    } else if (e.key === "s" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSave();
    }
  };

  if (!isOpen || !variant) return null;

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      aria-describedby="modal-description"
    >
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />

        {/* Modal */}
        <div className="relative bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 w-full max-w-4xl max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div>
              <h3
                id="modal-title"
                className="text-xl font-semibold text-gray-900 dark:text-white"
              >
                Edit Variant
              </h3>
              <p
                id="modal-description"
                className="text-gray-600 dark:text-gray-300 text-sm mt-1"
              >
                {variant?.text?.length || 0} characters •{" "}
                {variant?.readability || "N/A"} readability
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
              aria-label="Close modal"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            <div className="space-y-4">
              {/* Text Editor */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Content
                </label>
                <textarea
                  data-testid="edit-modal"
                  value={editedText}
                  onChange={e => setEditedText(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="w-full h-96 p-4 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent resize-none font-mono text-sm leading-relaxed"
                  placeholder="Enter your content here..."
                  autoFocus
                  aria-describedby="character-count unsaved-indicator"
                />
                <div className="flex justify-between items-center mt-2">
                  <span
                    id="character-count"
                    className="text-xs text-gray-500 dark:text-gray-400"
                  >
                    {editedText.length} characters
                  </span>
                  {editedText !== originalText && (
                    <span
                      id="unsaved-indicator"
                      className="text-xs text-yellow-400"
                      role="status"
                      aria-live="polite"
                    >
                      Unsaved changes
                    </span>
                  )}
                </div>
              </div>

              {/* Preview */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Preview
                </label>
                <div className="p-4 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg min-h-32">
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                    {editedText || "Enter content to see preview..."}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-2">
              <button
                onClick={handleReset}
                disabled={editedText === originalText}
                className="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:bg-gray-200 dark:disabled:bg-gray-800 disabled:cursor-not-allowed text-gray-900 dark:text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2 border border-gray-300 dark:border-gray-600"
                aria-label="Reset changes to original text"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Reset</span>
              </button>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={onClose}
                className="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-900 dark:text-white px-4 py-2 rounded-lg font-medium transition-colors border border-gray-300 dark:border-gray-600"
                aria-label="Cancel editing and close modal"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={editedText === originalText}
                className="bg-accent hover:bg-accent/90 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
                aria-label="Save changes and close modal"
              >
                <Save className="w-4 h-4" />
                <span>Save Changes</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
