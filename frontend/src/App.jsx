import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { ThemeProvider } from "./contexts/ThemeContext";
import AppShell from "./layouts/AppShell";
import Dashboard from "./pages/Dashboard";
import Jobs from "./pages/Jobs";
import Studio from "./pages/Studio";
import Scheduler from "./pages/Scheduler";
import Settings from "./pages/Settings";
import ToolLoader from "./components/ToolLoader";
import ErrorBoundary from "./components/ErrorBoundary";
import ToastProvider from "./components/ToastProvider";
import "./App.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

function App() {
  return (
    <ThemeProvider>
      <ErrorBoundary>
        <QueryClientProvider client={queryClient}>
          <ToastProvider>
            <Router>
              <Routes>
                <Route path="/" element={<AppShell />}>
                  <Route index element={<Dashboard />} />
                  <Route path="jobs" element={<Jobs />} />
                  <Route path="studio" element={<Studio />} />
                  <Route path="scheduler" element={<Scheduler />} />
                  <Route path="settings" element={<Settings />} />
                  {/* Tool routes */}
                  <Route path="tools/:toolName" element={<ToolLoader />} />
                </Route>
              </Routes>
            </Router>
            {import.meta.env.DEV && (
              <ReactQueryDevtools initialIsOpen={false} />
            )}
          </ToastProvider>
        </QueryClientProvider>
      </ErrorBoundary>
    </ThemeProvider>
  );
}

export default App;
