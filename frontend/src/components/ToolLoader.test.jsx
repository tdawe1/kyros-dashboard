import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { vi } from "vitest";
import ToolLoader from "./ToolLoader";

// Mock the tool registry
vi.mock("../toolRegistry", () => ({
  getTool: vi.fn(),
  listTools: vi.fn(),
}));

const renderWithRoute = path => {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/tools/:toolName" element={<ToolLoader />} />
      </Routes>
    </MemoryRouter>
  );
};

describe("ToolLoader", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders tool not found when tool does not exist", async () => {
    const { getTool, listTools } = await import("../toolRegistry");
    getTool.mockReturnValue(null);
    listTools.mockReturnValue([]);

    renderWithRoute("/tools/nonexistent");

    expect(screen.getByText("Tool Not Found")).toBeInTheDocument();
    expect(
      screen.getByText(
        'The tool "nonexistent" could not be found or is not available.'
      )
    ).toBeInTheDocument();
  });

  it("renders tool disabled when tool is disabled", async () => {
    const { getTool } = await import("../toolRegistry");
    getTool.mockReturnValue({
      name: "test-tool",
      title: "Test Tool",
      enabled: false,
    });

    renderWithRoute("/tools/test-tool");

    expect(screen.getByText("Tool Disabled")).toBeInTheDocument();
    expect(
      screen.getByText('The tool "Test Tool" is currently disabled.')
    ).toBeInTheDocument();
  });

  it("renders component error when tool has no component", async () => {
    const { getTool } = await import("../toolRegistry");
    getTool.mockReturnValue({
      name: "test-tool",
      title: "Test Tool",
      enabled: true,
      component: null,
    });

    renderWithRoute("/tools/test-tool");

    expect(screen.getByText("Component Error")).toBeInTheDocument();
    expect(
      screen.getByText('The tool "Test Tool" component could not be loaded.')
    ).toBeInTheDocument();
  });

  it("renders tool component when tool exists and is enabled", async () => {
    const MockComponent = () => <div>Mock Tool Component</div>;
    const { getTool } = await import("../toolRegistry");
    getTool.mockReturnValue({
      name: "test-tool",
      title: "Test Tool",
      enabled: true,
      component: MockComponent,
    });

    renderWithRoute("/tools/test-tool");

    expect(screen.getByText("Mock Tool Component")).toBeInTheDocument();
  });
});
