import { useState } from 'react'
import { FileText, Sparkles, ArrowRight } from 'lucide-react'
import { useGenerate } from '../hooks/useGenerate'

export default function StudioPanel() {
  const [inputText, setInputText] = useState('')
  const generateMutation = useGenerate()

  const handleGenerate = async () => {
    if (inputText.length < 50) {
      alert('Please enter at least 50 characters for better results.')
      return
    }

    try {
      await generateMutation.mutateAsync({
        input_text: inputText,
        channels: ['linkedin', 'twitter'],
        tone: 'professional',
        preset: 'default'
      })
      // TODO: Show success message or redirect to results
    } catch (error) {
      console.error('Generation failed:', error)
      alert('Failed to generate content. Please try again.')
    }
  }

  return (
    <div className="bg-white dark:bg-dark-800 rounded-lg border border-gray-200 dark:border-dark-700">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-dark-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
          <FileText className="w-5 h-5 mr-2" />
          Quick Studio
        </h3>
      </div>

      <div className="p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Source Content
          </label>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Paste your content here for quick repurposing..."
            className="w-full h-32 p-3 bg-gray-50 dark:bg-dark-700 border border-gray-300 dark:border-dark-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none text-sm"
          />
          <div className="flex justify-between items-center mt-2">
            <span className="text-xs text-gray-500 dark:text-gray-400">{inputText.length} characters</span>
            {inputText.length < 50 && (
              <span className="text-xs text-yellow-600 dark:text-yellow-400">Minimum 50 characters</span>
            )}
          </div>
        </div>

        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Target Channels
            </label>
            <div className="grid grid-cols-2 gap-2">
              {['LinkedIn', 'Twitter', 'Newsletter', 'Blog'].map((channel) => (
                <button
                  key={channel}
                  className="p-2 bg-gray-100 dark:bg-dark-700 border border-gray-300 dark:border-dark-600 rounded text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-dark-600 hover:text-gray-900 dark:hover:text-white transition-colors text-sm"
                >
                  {channel}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Tone
            </label>
            <select className="w-full p-2 bg-gray-50 dark:bg-dark-700 border border-gray-300 dark:border-dark-600 rounded text-gray-900 dark:text-white text-sm">
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="technical">Technical</option>
              <option value="creative">Creative</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={generateMutation.isPending || inputText.length < 50}
          className="w-full bg-primary-600 hover:bg-primary-700 dark:bg-primary-500 dark:hover:bg-primary-600 disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
        >
          {generateMutation.isPending ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Generating...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Generate Variants</span>
            </>
          )}
        </button>

        <div className="pt-4 border-t border-gray-200 dark:border-dark-700">
          <button className="w-full text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white text-sm font-medium flex items-center justify-center space-x-2">
            <span>Open Full Studio</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
