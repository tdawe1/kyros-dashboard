import { useState } from 'react'
import { FileText, Settings, Download, Sparkles } from 'lucide-react'
import { useGenerate } from '../hooks/useGenerate'
import { useToast } from '../hooks/useToast'
import VariantsGallery from '../ui/VariantsGallery'
import { CHANNELS, TONES, PRESETS, VALIDATION_RULES } from '../constants'

export default function Studio() {
  const [inputText, setInputText] = useState('')
  const [selectedChannels, setSelectedChannels] = useState(['linkedin', 'twitter'])
  const [selectedTone, setSelectedTone] = useState('professional')
  const [selectedPreset, setSelectedPreset] = useState('default')
  const [generatedVariants, setGeneratedVariants] = useState(null)
  const [errors, setErrors] = useState({})

  const generateMutation = useGenerate()
  const toast = useToast()

  const handleChannelToggle = (channelId) => {
    setSelectedChannels(prev =>
      prev.includes(channelId)
        ? prev.filter(id => id !== channelId)
        : [...prev, channelId]
    )
  }

  const validateForm = () => {
    const newErrors = {}

    if (inputText.length < VALIDATION_RULES.MIN_INPUT_LENGTH) {
      newErrors.inputText = `Please enter at least ${VALIDATION_RULES.MIN_INPUT_LENGTH} characters for better results.`
    }

    if (inputText.length > VALIDATION_RULES.MAX_INPUT_LENGTH) {
      newErrors.inputText = `Input text cannot exceed ${VALIDATION_RULES.MAX_INPUT_LENGTH} characters.`
    }

    if (selectedChannels.length === 0) {
      newErrors.channels = 'Please select at least one channel.'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleGenerate = async () => {
    if (!validateForm()) {
      toast.error('Please fix the errors before generating content.')
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

      toast.success('Content generated successfully!', {
        description: `Created variants for ${selectedChannels.length} channel(s)`
      })
    } catch (error) {
      console.error('Generation failed:', error)
      toast.error('Failed to generate content. Please try again.', {
        description: error.message
      })
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">Repurposer Studio</h1>
        <p className="text-gray-600 dark:text-gray-400">Transform your content into multiple channel formats</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Input Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Text Input */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Source Content</h3>
              <span className="text-sm text-gray-600 dark:text-gray-400">{inputText.length} characters</span>
            </div>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Paste your source content here... (minimum 100 characters for best results)"
              className="w-full h-64 p-4 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Channel Selection */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Target Channels</h3>
            <div className="grid grid-cols-2 gap-3">
              {CHANNELS.map((channel) => (
                <button
                  key={channel.id}
                  onClick={() => handleChannelToggle(channel.id)}
                  className={`p-3 rounded-lg border transition-colors ${
                    selectedChannels.includes(channel.id)
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
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
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Tone & Style</h3>
            <div className="space-y-2">
              {TONES.map((tone) => (
                <button
                  key={tone.id}
                  onClick={() => setSelectedTone(tone.id)}
                  className={`w-full p-3 rounded-lg border transition-colors ${
                    selectedTone === tone.id
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
                  }`}
                >
                  {tone.name}
                </button>
              ))}
            </div>
          </div>

          {/* Preset Selection */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Preset</h3>
            <div className="space-y-2">
              {PRESETS.map((preset) => (
                <button
                  key={preset.id}
                  onClick={() => setSelectedPreset(preset.id)}
                  className={`w-full p-3 rounded-lg border transition-colors ${
                    selectedPreset === preset.id
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
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
            className="w-full bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-4 rounded-lg font-semibold transition-colors flex items-center justify-center space-x-2"
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
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button className="w-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-gray-100 px-4 py-2 rounded-lg font-medium transition-colors border border-gray-300 dark:border-gray-600">
                <Settings className="w-4 h-4 inline mr-2" />
                Manage Presets
              </button>
              <button className="w-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-gray-100 px-4 py-2 rounded-lg font-medium transition-colors border border-gray-300 dark:border-gray-600">
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
