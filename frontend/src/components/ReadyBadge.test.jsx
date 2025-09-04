import { render, screen, waitFor, act } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { vi } from "vitest";
import ReadyBadge from "./ReadyBadge";

// Mock fetch
global.fetch = vi.fn();

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        refetchOnWindowFocus: false,
        gcTime: 0,
        staleTime: 0,
      },
    },
  });

const renderWithQueryClient = (component) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe("ReadyBadge", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset fetch mock
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("shows UP when /ready returns 200", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: "ok" }),
    });

    renderWithQueryClient(<ReadyBadge />);

    await waitFor(() => {
      expect(screen.getByTestId("ready-badge")).toBeInTheDocument();
      expect(screen.getByText("/ready:UP")).toBeInTheDocument();
    }, { timeout: 10000 });
  });

  it("shows DOWN when /ready returns error", async () => {
    fetch.mockRejectedValueOnce(new Error("Network error"));

    renderWithQueryClient(<ReadyBadge />);

    await waitFor(() => {
      expect(screen.getByTestId("ready-badge")).toBeInTheDocument();
      expect(screen.getByText("/ready:DOWN")).toBeInTheDocument();
    }, { timeout: 10000 });
  });

  it("shows DOWN when /ready returns non-200 status", async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    renderWithQueryClient(<ReadyBadge />);

    await waitFor(() => {
      expect(screen.getByTestId("ready-badge")).toBeInTheDocument();
      expect(screen.getByText("/ready:DOWN")).toBeInTheDocument();
    }, { timeout: 10000 });
  });

  it("applies correct styling for UP status", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: "ok" }),
    });

    renderWithQueryClient(<ReadyBadge />);

    await waitFor(() => {
      const badge = screen.getByTestId("ready-badge");
      expect(badge).toHaveClass("bg-green-100", "text-green-800");
    }, { timeout: 10000 });
  });

  it("applies correct styling for DOWN status", async () => {
    fetch.mockRejectedValueOnce(new Error("Network error"));

    renderWithQueryClient(<ReadyBadge />);

    await waitFor(() => {
      const badge = screen.getByTestId("ready-badge");
      expect(badge).toHaveClass("bg-red-100", "text-red-800");
    }, { timeout: 10000 });
  });

  it("shows LOADING state initially", () => {
    // Mock a slow response to catch loading state
    fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    renderWithQueryClient(<ReadyBadge />);

    expect(screen.getByTestId("ready-badge")).toBeInTheDocument();
    expect(screen.getByText("/ready:LOADING")).toBeInTheDocument();
  });

  it("applies correct styling for LOADING status", () => {
    fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    renderWithQueryClient(<ReadyBadge />);

    const badge = screen.getByTestId("ready-badge");
    expect(badge).toHaveClass("bg-yellow-100", "text-yellow-800");
  });
});
