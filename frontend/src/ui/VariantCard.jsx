import { useState } from "react";
import {
  Check,
  Edit,
  Copy,
  Download,
  Heart,
  MoreHorizontal,
} from "lucide-react";

export default function VariantCard({
  variant,
  channel,
  isSelected,
  onEdit,
  onAccept,
  onCopy,
  onDownload,
  onToggleFavorite,
  onSelect,
}) {
  const [isFavorited, setIsFavorited] = useState(false);

  const handleToggleFavorite = () => {
    setIsFavorited(!isFavorited);
    onToggleFavorite?.(variant.id, !isFavorited);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(variant.text);
      onCopy?.(variant.id);
    } catch (error) {
      console.error("Failed to copy text:", error);
    }
  };

  const getReadabilityColor = (readability) => {
    switch (readability.toLowerCase()) {
      case "excellent":
        return "text-green-400";
      case "good":
        return "text-blue-400";
      case "fair":
        return "text-yellow-400";
      case "poor":
        return "text-red-400";
      default:
        return "text-gray-500 dark:text-gray-400";
    }
  };

  const getChannelIcon = (channel) => {
    switch (channel.toLowerCase()) {
      case "linkedin":
        return "💼";
      case "twitter":
        return "🐦";
      case "newsletter":
        return "📧";
      case "blog":
        return "📝";
      default:
        return "📄";
    }
  };

  return (
    <div
      data-testid="variant-card"
      className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:border-gray-300 dark:hover:border-gray-600 transition-colors"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{getChannelIcon(channel)}</span>
          <div>
            <h4 className="text-gray-900 dark:text-white font-semibold capitalize">
              {channel}
            </h4>
            <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
              <span>{variant.length} chars</span>
              <span>•</span>
              <span className={getReadabilityColor(variant.readability)}>
                {variant.readability}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            data-testid="select-variant"
            checked={!!isSelected}
            onChange={() => onSelect?.()}
            className="w-4 h-4 accent-accent cursor-pointer"
            aria-label="Select variant"
          />
          <button
            onClick={handleToggleFavorite}
            className={`p-2 rounded-lg transition-colors ${
              isFavorited
                ? "text-red-400 bg-red-900/20"
                : "text-gray-500 dark:text-gray-400 hover:text-red-400 hover:bg-red-900/20"
            }`}
          >
            <Heart className={`w-4 h-4 ${isFavorited ? "fill-current" : ""}`} />
          </button>
          <button className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
            <MoreHorizontal className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="mb-4">
        <p className="text-gray-700 dark:text-gray-300 leading-relaxed line-clamp-4">
          {variant.text}
        </p>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <button
            data-testid="accept-button"
            onClick={() => onAccept?.(variant.id)}
            className="bg-accent hover:bg-accent/90 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
          >
            <Check className="w-4 h-4" />
            <span>Accept</span>
          </button>

          <button
            data-testid="edit-button"
            onClick={() => onEdit?.(variant)}
            className="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-900 dark:text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2 border border-gray-300 dark:border-gray-600"
          >
            <Edit className="w-4 h-4" />
            <span>Edit</span>
          </button>
        </div>

        <div className="flex items-center space-x-2">
          <button
            data-testid="copy-button"
            onClick={handleCopy}
            className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="Copy to clipboard"
          >
            <Copy className="w-4 h-4" />
          </button>

          <button
            data-testid="download-button"
            onClick={() => onDownload?.(variant.id)}
            className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="Download"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
