import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import ToolLoader from './ToolLoader'

// Mock the tool registry
jest.mock('../toolRegistry', () => ({
  getTool: jest.fn(),
}))

const MockedToolLoader = ({ toolName }) => (
  <BrowserRouter>
    <ToolLoader />
  </BrowserRouter>
)

describe('ToolLoader', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders tool not found when tool does not exist', () => {
    const { getTool } = require('../toolRegistry')
    getTool.mockReturnValue(null)

    render(<MockedToolLoader toolName="nonexistent" />)

    expect(screen.getByText('Tool Not Found')).toBeInTheDocument()
    expect(screen.getByText('The tool "nonexistent" could not be found or is not available.')).toBeInTheDocument()
  })

  it('renders tool disabled when tool is disabled', () => {
    const { getTool } = require('../toolRegistry')
    getTool.mockReturnValue({
      name: 'test-tool',
      title: 'Test Tool',
      enabled: false,
    })

    render(<MockedToolLoader toolName="test-tool" />)

    expect(screen.getByText('Tool Disabled')).toBeInTheDocument()
    expect(screen.getByText('The tool "Test Tool" is currently disabled.')).toBeInTheDocument()
  })

  it('renders component error when tool has no component', () => {
    const { getTool } = require('../toolRegistry')
    getTool.mockReturnValue({
      name: 'test-tool',
      title: 'Test Tool',
      enabled: true,
      component: null,
    })

    render(<MockedToolLoader toolName="test-tool" />)

    expect(screen.getByText('Component Error')).toBeInTheDocument()
    expect(screen.getByText('The tool "Test Tool" component could not be loaded.')).toBeInTheDocument()
  })

  it('renders tool component when tool exists and is enabled', () => {
    const MockComponent = () => <div>Mock Tool Component</div>
    const { getTool } = require('../toolRegistry')
    getTool.mockReturnValue({
      name: 'test-tool',
      title: 'Test Tool',
      enabled: true,
      component: MockComponent,
    })

    render(<MockedToolLoader toolName="test-tool" />)

    expect(screen.getByText('Mock Tool Component')).toBeInTheDocument()
  })
})
