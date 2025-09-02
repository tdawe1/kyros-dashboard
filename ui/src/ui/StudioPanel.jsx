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
    <div className="bg-navy-800 rounded-lg border border-navy-700">
      <div className="px-6 py-4 border-b border-navy-700">
        <h3 className="text-lg font-semibold text-white flex items-center">
          <FileText className="w-5 h-5 mr-2" />
          Quick Studio
        </h3>
      </div>
      
      <div className="p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-navy-300 mb-2">
            Source Content
          </label>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Paste your content here for quick repurposing..."
            className="w-full h-32 p-3 bg-navy-700 border border-navy-600 rounded-lg text-white placeholder-navy-400 focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent resize-none text-sm"
          />
          <div className="flex justify-between items-center mt-2">
            <span className="text-xs text-navy-400">{inputText.length} characters</span>
            {inputText.length < 50 && (
              <span className="text-xs text-yellow-400">Minimum 50 characters</span>
            )}
          </div>
        </div>

        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-navy-300 mb-2">
              Target Channels
            </label>
            <div className="grid grid-cols-2 gap-2">
              {['LinkedIn', 'Twitter', 'Newsletter', 'Blog'].map((channel) => (
                <button
                  key={channel}
                  className="p-2 bg-navy-700 border border-navy-600 rounded text-navy-300 hover:bg-navy-600 hover:text-white transition-colors text-sm"
                >
                  {channel}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-navy-300 mb-2">
              Tone
            </label>
            <select className="w-full p-2 bg-navy-700 border border-navy-600 rounded text-white text-sm">
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
          className="w-full bg-accent hover:bg-accent/90 disabled:bg-navy-600 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
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

        <div className="pt-4 border-t border-navy-700">
          <button className="w-full text-navy-300 hover:text-white text-sm font-medium flex items-center justify-center space-x-2">
            <span>Open Full Studio</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
