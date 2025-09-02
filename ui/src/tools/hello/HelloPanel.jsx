import { useState } from 'react'
import { MessageCircle, Info, Settings, CheckCircle } from 'lucide-react'

export default function HelloPanel() {
  const [message, setMessage] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [info, setInfo] = useState(null)

  const handlePing = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/tools/hello/ping', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message || 'Hello' }),
      })
      const data = await res.json()
      setResponse(data)
    } catch (error) {
      console.error('Ping failed:', error)
      setResponse({ error: 'Failed to ping the Hello World tool' })
    } finally {
      setLoading(false)
    }
  }

  const handleGetInfo = async () => {
    try {
      const res = await fetch('/api/tools/hello/info')
      const data = await res.json()
      setInfo(data)
    } catch (error) {
      console.error('Failed to get info:', error)
      setInfo({ error: 'Failed to get tool information' })
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">Hello World Tool</h1>
        <p className="text-gray-600 dark:text-gray-400">A simple demonstration of the modular tool architecture</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Ping Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center mb-4">
            <MessageCircle className="w-6 h-6 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Ping Test</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Message to send
              </label>
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Enter a message..."
                className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              onClick={handlePing}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Pinging...</span>
                </>
              ) : (
                <>
                  <MessageCircle className="w-4 h-4" />
                  <span>Send Ping</span>
                </>
              )}
            </button>
          </div>

          {response && (
            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Response:</h4>
              {response.error ? (
                <p className="text-red-600 dark:text-red-400">{response.error}</p>
              ) : (
                <div className="space-y-2">
                  <p className="text-gray-700 dark:text-gray-300">{response.message}</p>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    <p>Tool: {response.tool}</p>
                    <p>Status: {response.status}</p>
                    <p>Timestamp: {new Date(response.timestamp).toLocaleString()}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Info Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center mb-4">
            <Info className="w-6 h-6 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Tool Information</h3>
          </div>

          <button
            onClick={handleGetInfo}
            className="w-full bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2 mb-4"
          >
            <Info className="w-4 h-4" />
            <span>Get Tool Info</span>
          </button>

          {info && (
            <div className="space-y-3">
              {info.error ? (
                <p className="text-red-600 dark:text-red-400">{info.error}</p>
              ) : (
                <div className="space-y-3">
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-gray-100">{info.name}</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{info.description}</p>
                  </div>

                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    <p><strong>Tool:</strong> {info.tool}</p>
                    <p><strong>Version:</strong> {info.version}</p>
                  </div>

                  <div>
                    <h5 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Features:</h5>
                    <ul className="space-y-1">
                      {info.features?.map((feature, index) => (
                        <li key={index} className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                          <CheckCircle className="w-3 h-3 text-green-500 mr-2" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Architecture Demo */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center mb-4">
          <Settings className="w-6 h-6 text-purple-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Modular Architecture Demo</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="text-2xl mb-2">🔧</div>
            <h4 className="font-medium text-gray-900 dark:text-gray-100">Backend Tool</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">Self-contained API endpoints</p>
          </div>

          <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div className="text-2xl mb-2">🎨</div>
            <h4 className="font-medium text-gray-900 dark:text-gray-100">Frontend Panel</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">Isolated UI components</p>
          </div>

          <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
            <div className="text-2xl mb-2">⚡</div>
            <h4 className="font-medium text-gray-900 dark:text-gray-100">Dynamic Loading</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">Registry-based discovery</p>
          </div>
        </div>

        <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            This Hello World tool demonstrates how easy it is to add new tools to the system.
            The tool is completely self-contained with its own backend API and frontend UI,
            and is automatically discovered and loaded by the registry system.
          </p>
        </div>
      </div>
    </div>
  )
}
