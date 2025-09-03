import { Sun, Moon } from "lucide-react";
import { useTheme } from "../contexts/ThemeContext";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      data-testid="theme-toggle"
      onClick={toggleTheme}
      className="relative p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200"
      aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
    >
      <div className="relative w-5 h-5">
        <Sun
          className={`absolute inset-0 w-5 h-5 text-yellow-500 transition-all duration-300 ${
            theme === "light"
              ? "opacity-100 rotate-0 scale-100"
              : "opacity-0 rotate-90 scale-75"
          }`}
        />
        <Moon
          className={`absolute inset-0 w-5 h-5 text-blue-400 transition-all duration-300 ${
            theme === "dark"
              ? "opacity-100 rotate-0 scale-100"
              : "opacity-0 -rotate-90 scale-75"
          }`}
        />
      </div>
    </button>
  );
}
