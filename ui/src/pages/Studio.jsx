import { useState } from 'react'
import { FileText, Settings, Download, Sparkles } from 'lucide-react'
import { useGenerate } from '../hooks/useGenerate'
import VariantsGallery from '../ui/VariantsGallery'

export default function Studio() {
  const [inputText, setInputText] = useState('')
  const [selectedChannels, setSelectedChannels] = useState(['linkedin', 'twitter'])
  const [selectedTone, setSelectedTone] = useState('professional')
  const [selectedPreset, setSelectedPreset] = useState('default')
  const [generatedVariants, setGeneratedVariants] = useState(null)
  const generateMutation = useGenerate()

  const channels = [
    { id: 'linkedin', name: 'LinkedIn', icon: '💼' },
    { id: 'twitter', name: 'Twitter', icon: '🐦' },
    { id: 'newsletter', name: 'Newsletter', icon: '📧' },
    { id: 'blog', name: 'Blog', icon: '📝' }
  ]

  const tones = [
    { id: 'professional', name: 'Professional' },
    { id: 'casual', name: 'Casual' },
    { id: 'technical', name: 'Technical' },
    { id: 'creative', name: 'Creative' }
  ]

  const presets = [
    { id: 'default', name: 'Default' },
    { id: 'marketing', name: 'Marketing' },
    { id: 'technical', name: 'Technical' },
    { id: 'newsletter', name: 'Newsletter' }
  ]

  const handleChannelToggle = (channelId) => {
    setSelectedChannels(prev => 
      prev.includes(channelId) 
        ? prev.filter(id => id !== channelId)
        : [...prev, channelId]
    )
  }

  const handleGenerate = async () => {
    if (inputText.length < 100) {
      alert('Please enter at least 100 characters for better results.')
      return
    }
    
    try {
      const result = await generateMutation.mutateAsync({
        input_text: inputText,
        channels: selectedChannels,
        tone: selectedTone,
        preset: selectedPreset
      })
      
      // Store the generated variants
      setGeneratedVariants([{
        job_id: result.job_id,
        variants: result.variants
      }])
    } catch (error) {
      console.error('Generation failed:', error)
      alert('Failed to generate content. Please try again.')
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Repurposer Studio</h1>
        <p className="text-navy-300">Transform your content into multiple channel formats</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Input Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Text Input */}
          <div className="bg-navy-800 rounded-lg p-6 border border-navy-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Source Content</h3>
              <span className="text-sm text-navy-300">{inputText.length} characters</span>
            </div>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Paste your source content here... (minimum 100 characters for best results)"
              className="w-full h-64 p-4 bg-navy-700 border border-navy-600 rounded-lg text-white placeholder-navy-400 focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent resize-none"
            />
          </div>

          {/* Channel Selection */}
          <div className="bg-navy-800 rounded-lg p-6 border border-navy-700">
            <h3 className="text-lg font-semibold text-white mb-4">Target Channels</h3>
            <div className="grid grid-cols-2 gap-3">
              {channels.map((channel) => (
                <button
                  key={channel.id}
                  onClick={() => handleChannelToggle(channel.id)}
                  className={`p-3 rounded-lg border transition-colors ${
                    selectedChannels.includes(channel.id)
                      ? 'bg-accent border-accent text-white'
                      : 'bg-navy-700 border-navy-600 text-navy-300 hover:bg-navy-600'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">{channel.icon}</span>
                    <span className="font-medium">{channel.name}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Settings Panel */}
        <div className="space-y-6">
          {/* Tone Selection */}
          <div className="bg-navy-800 rounded-lg p-6 border border-navy-700">
            <h3 className="text-lg font-semibold text-white mb-4">Tone & Style</h3>
            <div className="space-y-2">
              {tones.map((tone) => (
                <button
                  key={tone.id}
                  onClick={() => setSelectedTone(tone.id)}
                  className={`w-full p-3 rounded-lg border transition-colors ${
                    selectedTone === tone.id
                      ? 'bg-accent border-accent text-white'
                      : 'bg-navy-700 border-navy-600 text-navy-300 hover:bg-navy-600'
                  }`}
                >
                  {tone.name}
                </button>
              ))}
            </div>
          </div>

          {/* Preset Selection */}
          <div className="bg-navy-800 rounded-lg p-6 border border-navy-700">
            <h3 className="text-lg font-semibold text-white mb-4">Preset</h3>
            <div className="space-y-2">
              {presets.map((preset) => (
                <button
                  key={preset.id}
                  onClick={() => setSelectedPreset(preset.id)}
                  className={`w-full p-3 rounded-lg border transition-colors ${
                    selectedPreset === preset.id
                      ? 'bg-accent border-accent text-white'
                      : 'bg-navy-700 border-navy-600 text-navy-300 hover:bg-navy-600'
                  }`}
                >
                  {preset.name}
                </button>
              ))}
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={generateMutation.isPending || inputText.length < 100}
            className="w-full bg-accent hover:bg-accent/90 disabled:bg-navy-600 disabled:cursor-not-allowed text-white px-6 py-4 rounded-lg font-semibold transition-colors flex items-center justify-center space-x-2"
          >
            {generateMutation.isPending ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Generate Variants</span>
              </>
            )}
          </button>

          {/* Quick Actions */}
          <div className="bg-navy-800 rounded-lg p-6 border border-navy-700">
            <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button className="w-full bg-navy-700 hover:bg-navy-600 text-white px-4 py-2 rounded-lg font-medium transition-colors border border-navy-600">
                <Settings className="w-4 h-4 inline mr-2" />
                Manage Presets
              </button>
              <button className="w-full bg-navy-700 hover:bg-navy-600 text-white px-4 py-2 rounded-lg font-medium transition-colors border border-navy-600">
                <Download className="w-4 h-4 inline mr-2" />
                Export Templates
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Generated Variants */}
      {generatedVariants && (
        <div className="mt-8">
          <VariantsGallery 
            variants={generatedVariants}
            onVariantUpdate={(updatedVariant) => {
              // Update the variant in the state
              setGeneratedVariants(prev => 
                prev.map(job => ({
                  ...job,
                  variants: Object.fromEntries(
                    Object.entries(job.variants).map(([channel, variants]) => [
                      channel,
                      variants.map(variant => 
                        variant.id === updatedVariant.id ? updatedVariant : variant
                      )
                    ])
                  )
                }))
              )
            }}
          />
        </div>
      )}
    </div>
  )
}
