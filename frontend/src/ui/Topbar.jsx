import { Menu, Bell, User } from "lucide-react";
import { useLocation } from "react-router-dom";
import { useConfig } from "../hooks/useConfig";
import ReadyBadge from "../components/ReadyBadge";

const pageTitles = {
  "/": "Dashboard",
  "/jobs": "Job Monitor",
  "/studio": "Repurposer Studio",
  "/scheduler": "Scheduler",
  "/settings": "Settings",
};

export default function Topbar({ onMenuClick }) {
  const location = useLocation();
  const pageTitle = pageTitles[location.pathname] || "Dashboard";
  const { isDemoMode } = useConfig();

  return (
    <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between h-16 px-6">
        {/* Mobile menu button */}
        <button
          data-testid="mobile-menu"
          onClick={onMenuClick}
          className="lg:hidden text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
        >
          <Menu className="w-6 h-6" />
        </button>

        {/* Page title - dynamic based on route */}
        <div className="flex-1 lg:flex-none flex items-center space-x-3">
          <h1
            data-testid="page-title"
            className="text-xl font-semibold text-gray-900 dark:text-gray-100"
          >
            {pageTitle}
          </h1>
          <ReadyBadge />
          {isDemoMode && (
            <span className="bg-yellow-100 text-yellow-800 text-xs font-medium px-2.5 py-0.5 rounded-full dark:bg-yellow-900 dark:text-yellow-300">
              Demo Mode
            </span>
          )}
        </div>

        {/* Right side actions */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 relative">
            <Bell className="w-6 h-6" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-accent rounded-full"></span>
          </button>

          {/* User menu */}
          <button className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100">
            <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
              <User className="w-4 h-4" />
            </div>
            <span className="hidden md:block text-sm">Admin</span>
          </button>
        </div>
      </div>
    </div>
  );
}
