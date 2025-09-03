import { useState } from "react";
import { Plus, Edit, Trash2, Save, X } from "lucide-react";
import {
  usePresets,
  useCreatePreset,
  useUpdatePreset,
  useDeletePreset,
} from "../hooks/usePresets";
import { useConfig, useModelSelection } from "../hooks/useConfig";

export default function Settings() {
  const [activeTab, setActiveTab] = useState("presets");
  const { data: presets, isLoading: presetsLoading } = usePresets();
  const createPreset = useCreatePreset();
  const _updatePreset = useUpdatePreset();
  const deletePreset = useDeletePreset();
  const { config, isDemoMode } = useConfig();
  const { selectedModel, updateModel, validModels } = useModelSelection();

  const [glossary, setGlossary] = useState([
    { id: 1, term: "AI", definition: "Artificial Intelligence" },
    { id: 2, term: "ML", definition: "Machine Learning" },
    { id: 3, term: "API", definition: "Application Programming Interface" },
  ]);
  const [editingPreset, setEditingPreset] = useState(null);
  const [editingGlossary, setEditingGlossary] = useState(null);
  const [exportFormat, setExportFormat] = useState("csv");

  const tabs = [
    { id: "presets", name: "Presets & Templates" },
    { id: "glossary", name: "Glossary & Terms" },
    { id: "api", name: "API Settings" },
    { id: "export", name: "Export Settings" },
  ];

  const handleAddPreset = async () => {
    try {
      const newPreset = await createPreset.mutateAsync({
        name: "New Preset",
        description: "Custom preset",
        config: { tone: "professional", length: "medium" },
      });
      setEditingPreset(newPreset.id);
    } catch (error) {
      console.error("Failed to create preset:", error);
    }
  };

  const handleDeletePreset = async id => {
    try {
      await deletePreset.mutateAsync(id);
    } catch (error) {
      console.error("Failed to delete preset:", error);
    }
  };

  const handleAddGlossary = () => {
    const newTerm = {
      id: Date.now(),
      term: "New Term",
      definition: "Definition",
    };
    setGlossary([...glossary, newTerm]);
    setEditingGlossary(newTerm.id);
  };

  const handleDeleteGlossary = id => {
    setGlossary(glossary.filter(g => g.id !== id));
  };

  return (
    <div className="space-y-8">
      <div>
        <h1
          data-testid="page-title"
          className="text-3xl font-bold text-gray-900 dark:text-white mb-2"
        >
          Settings
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Manage your presets, glossary, and application settings
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? "border-accent text-accent"
                  : "border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:border-gray-400 dark:hover:border-gray-300"
              }`}
            >
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === "presets" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">
              Content Presets
            </h2>
            <button
              onClick={handleAddPreset}
              className="bg-accent hover:bg-accent/90 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>Add Preset</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {presetsLoading ? (
              <div className="col-span-full text-center text-gray-500 dark:text-gray-400">
                Loading presets...
              </div>
            ) : (
              presets?.map(preset => (
                <div
                  key={preset.id}
                  className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700"
                >
                  {editingPreset === preset.id ? (
                    <div className="space-y-4">
                      <input
                        type="text"
                        defaultValue={preset.name}
                        className="w-full p-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
                      />
                      <textarea
                        defaultValue={preset.description}
                        className="w-full p-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-gray-900 dark:text-white h-20 resize-none"
                      />
                      <div className="flex space-x-2">
                        <button
                          onClick={() => {
                            // TODO: Implement preset save functionality
                            setEditingPreset(null);
                          }}
                          className="bg-accent hover:bg-accent/90 text-white px-3 py-1 rounded text-sm"
                        >
                          <Save className="w-4 h-4 inline mr-1" />
                          Save
                        </button>
                        <button
                          onClick={() => setEditingPreset(null)}
                          className="bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-900 dark:text-white px-3 py-1 rounded text-sm"
                        >
                          <X className="w-4 h-4 inline mr-1" />
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {preset.name}
                        </h3>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => setEditingPreset(preset.id)}
                            className="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeletePreset(preset.id)}
                            className="text-red-400 hover:text-red-300"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                      <p className="text-gray-600 dark:text-gray-300 text-sm mb-3">
                        {preset.description}
                      </p>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        <div>Tone: {preset.config.tone}</div>
                        <div>Length: {preset.config.length}</div>
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {activeTab === "glossary" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">
              Glossary & Terms
            </h2>
            <button
              onClick={handleAddGlossary}
              className="bg-accent hover:bg-accent/90 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>Add Term</span>
            </button>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Terms & Definitions
              </h3>
            </div>
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {glossary.map(item => (
                <div key={item.id} className="p-6">
                  {editingGlossary === item.id ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <input
                        type="text"
                        defaultValue={item.term}
                        className="p-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-gray-900 dark:text-white"
                        placeholder="Term"
                      />
                      <input
                        type="text"
                        defaultValue={item.definition}
                        className="p-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-gray-900 dark:text-white"
                        placeholder="Definition"
                      />
                      <div className="md:col-span-2 flex space-x-2">
                        <button
                          onClick={() => {
                            // TODO: Implement glossary save functionality
                            setEditingGlossary(null);
                          }}
                          className="bg-accent hover:bg-accent/90 text-white px-3 py-1 rounded text-sm"
                        >
                          <Save className="w-4 h-4 inline mr-1" />
                          Save
                        </button>
                        <button
                          onClick={() => setEditingGlossary(null)}
                          className="bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-900 dark:text-white px-3 py-1 rounded text-sm"
                        >
                          <X className="w-4 h-4 inline mr-1" />
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="font-semibold text-gray-900 dark:text-white">
                          {item.term}
                        </div>
                        <div className="text-gray-600 dark:text-gray-300 text-sm">
                          {item.definition}
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => setEditingGlossary(item.id)}
                          className="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteGlossary(item.id)}
                          className="text-red-400 hover:text-red-300"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === "api" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              API Configuration
            </h2>
            {isDemoMode && (
              <span className="bg-yellow-100 text-yellow-800 text-xs font-medium px-2.5 py-0.5 rounded-full dark:bg-yellow-900 dark:text-yellow-300">
                Demo Mode Active
              </span>
            )}
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  API Mode
                </label>
                <div className="text-sm text-gray-600 dark:text-gray-400 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  {isDemoMode
                    ? "Demo Mode - Using canned responses"
                    : "Real Mode - Using OpenAI API"}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Model Selection
                </label>
                <select
                  value={selectedModel}
                  onChange={e => updateModel(e.target.value)}
                  className="w-full p-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
                >
                  {validModels.map(model => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Selected model will be used for content generation
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  API Base URL
                </label>
                <input
                  type="text"
                  value={config?.apiBaseUrl || "http://localhost:8000"}
                  readOnly={isDemoMode}
                  className="w-full p-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
                />
              </div>

              {!isDemoMode && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    OpenAI API Key
                  </label>
                  <input
                    type="password"
                    placeholder="Enter your OpenAI API key"
                    value={config?.openaiApiKey || ""}
                    onChange={() => {
                      // TODO: Implement API key persistence
                      // API key changed - implement secure storage
                    }}
                    className="w-full p-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
                  />
                </div>
              )}

              <button className="bg-accent hover:bg-accent/90 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                Save Configuration
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === "export" && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Export Settings
          </h2>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Default Export Format
                </label>
                <select
                  value={exportFormat}
                  onChange={e => setExportFormat(e.target.value)}
                  className="w-full p-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white"
                >
                  <option value="csv">CSV</option>
                  <option value="docx">Word Document</option>
                  <option value="json">JSON</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Include Metadata
                </label>
                <input type="checkbox" className="mr-2" defaultChecked />
                <span className="text-gray-600 dark:text-gray-300">
                  Include timestamps and source information
                </span>
              </div>
              <button className="bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                Save Settings
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
