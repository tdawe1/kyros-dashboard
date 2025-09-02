import { useState } from 'react'
import { Download, CheckCircle, Filter, Grid, List } from 'lucide-react'
import VariantCard from './VariantCard'
import EditorModal from './EditorModal'
import { useExport } from '../hooks/useGenerate'

export default function VariantsGallery({ variants, onVariantUpdate }) {
  const [selectedVariants, setSelectedVariants] = useState(new Set())
  const [editingVariant, setEditingVariant] = useState(null)
  const [viewMode, setViewMode] = useState('grid') // 'grid' or 'list'
  const [filterChannel, setFilterChannel] = useState('all')
  const [favoriteVariants, setFavoriteVariants] = useState(new Set())
  const exportMutation = useExport()

  const channels = ['all', ...new Set(variants?.map(v => Object.keys(v.variants || {})).flat())]

  const handleVariantSelect = (variantId) => {
    const newSelected = new Set(selectedVariants)
    if (newSelected.has(variantId)) {
      newSelected.delete(variantId)
    } else {
      newSelected.add(variantId)
    }
    setSelectedVariants(newSelected)
  }

  const handleSelectAll = (channel) => {
    if (channel === 'all') {
      const allVariantIds = variants?.flatMap(v => 
        Object.values(v.variants || {}).flat().map(variant => variant.id)
      ) || []
      setSelectedVariants(new Set(allVariantIds))
    } else {
      const channelVariantIds = variants?.flatMap(v => 
        (v.variants?.[channel] || []).map(variant => variant.id)
      ) || []
      setSelectedVariants(new Set(channelVariantIds))
    }
  }

  const handleDeselectAll = () => {
    setSelectedVariants(new Set())
  }

  const handleBulkExport = async () => {
    if (selectedVariants.size === 0) {
      alert('Please select variants to export')
      return
    }

    try {
      const result = await exportMutation.mutateAsync({
        job_id: variants?.[0]?.job_id || 'demo',
        format: 'csv',
        selected_variants: Array.from(selectedVariants)
      })
      
      // Create download link
      const link = document.createElement('a')
      link.href = result.file_url
      link.download = result.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      alert(`Exported ${selectedVariants.size} variants successfully!`)
    } catch (error) {
      console.error('Export failed:', error)
      alert('Failed to export variants. Please try again.')
    }
  }

  const handleVariantEdit = (variant) => {
    setEditingVariant(variant)
  }

  const handleVariantSave = (updatedVariant) => {
    if (onVariantUpdate) {
      onVariantUpdate(updatedVariant)
    }
    setEditingVariant(null)
  }

  const handleVariantAccept = (variantId) => {
    // TODO: Implement accept logic
    console.log('Accepted variant:', variantId)
  }

  const handleVariantCopy = (variantId) => {
    // TODO: Show copy feedback
    console.log('Copied variant:', variantId)
  }

  const handleVariantDownload = (variantId) => {
    // TODO: Implement individual download
    console.log('Downloaded variant:', variantId)
  }

  const handleToggleFavorite = (variantId, isFavorited) => {
    const newFavorites = new Set(favoriteVariants)
    if (isFavorited) {
      newFavorites.add(variantId)
    } else {
      newFavorites.delete(variantId)
    }
    setFavoriteVariants(newFavorites)
  }

  const filteredVariants = variants?.filter(v => 
    filterChannel === 'all' || v.variants?.[filterChannel]
  ) || []

  if (!variants || variants.length === 0) {
    return (
      <div className="bg-navy-800 rounded-lg border border-navy-700 p-12 text-center">
        <div className="text-navy-400 mb-4">
          <Grid className="w-16 h-16 mx-auto" />
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">No Variants Generated</h3>
        <p className="text-navy-300">
          Generate content variants to see them displayed here.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Generated Variants</h2>
          <p className="text-navy-300">
            {selectedVariants.size > 0 && `${selectedVariants.size} selected`}
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          {/* View Mode Toggle */}
          <div className="flex bg-navy-700 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded transition-colors ${
                viewMode === 'grid' 
                  ? 'bg-accent text-white' 
                  : 'text-navy-300 hover:text-white'
              }`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded transition-colors ${
                viewMode === 'list' 
                  ? 'bg-accent text-white' 
                  : 'text-navy-300 hover:text-white'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>

          {/* Channel Filter */}
          <select
            value={filterChannel}
            onChange={(e) => setFilterChannel(e.target.value)}
            className="bg-navy-700 border border-navy-600 rounded-lg text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent"
          >
            {channels.map(channel => (
              <option key={channel} value={channel}>
                {channel === 'all' ? 'All Channels' : channel.charAt(0).toUpperCase() + channel.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Bulk Actions */}
      {selectedVariants.size > 0 && (
        <div className="bg-navy-800 rounded-lg border border-navy-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <span className="text-white font-medium">
                {selectedVariants.size} variants selected
              </span>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleSelectAll(filterChannel)}
                  className="text-accent hover:text-accent/80 text-sm font-medium"
                >
                  Select All {filterChannel !== 'all' ? filterChannel : ''}
                </button>
                <span className="text-navy-400">•</span>
                <button
                  onClick={handleDeselectAll}
                  className="text-navy-300 hover:text-white text-sm font-medium"
                >
                  Deselect All
                </button>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={handleBulkExport}
                disabled={exportMutation.isPending}
                className="bg-accent hover:bg-accent/90 disabled:bg-navy-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Export Selected</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Variants Grid */}
      <div className={`${
        viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
          : 'space-y-4'
      }`}>
        {filteredVariants.map((job) => 
          Object.entries(job.variants || {}).map(([channel, channelVariants]) => 
            channelVariants.map((variant) => (
              <VariantCard
                key={variant.id}
                variant={variant}
                channel={channel}
                onEdit={handleVariantEdit}
                onAccept={handleVariantAccept}
                onCopy={handleVariantCopy}
                onDownload={handleVariantDownload}
                onToggleFavorite={handleToggleFavorite}
              />
            ))
          ).flat()
        )}
      </div>

      {/* Editor Modal */}
      <EditorModal
        isOpen={!!editingVariant}
        onClose={() => setEditingVariant(null)}
        variant={editingVariant}
        onSave={handleVariantSave}
      />
    </div>
  )
}
