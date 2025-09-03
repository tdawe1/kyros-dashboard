import { createContext, useContext, useState, useEffect } from "react";

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    // Check if we're in a browser environment
    if (typeof window === "undefined") {
      return "light";
    }

    // Check localStorage first, then system preference
    let savedTheme = null;
    try {
      savedTheme = localStorage.getItem("kyros-theme");
    } catch (error) {
      console.warn("Failed to read from localStorage:", error);
    }

    if (savedTheme && (savedTheme === "light" || savedTheme === "dark")) {
      return savedTheme;
    }

    // Check system preference
    try {
      if (
        window.matchMedia &&
        window.matchMedia("(prefers-color-scheme: dark)").matches
      ) {
        return "dark";
      }
    } catch (error) {
      console.warn("Failed to check system preference:", error);
    }

    return "light";
  });

  useEffect(() => {
    // Apply theme to document
    document.documentElement.classList.remove("light", "dark");
    document.documentElement.classList.add(theme);

    // Save to localStorage
    try {
      localStorage.setItem("kyros-theme", theme);
    } catch (error) {
      console.error("Failed to save theme to localStorage:", error);
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === "light" ? "dark" : "light"));
  };

  const value = {
    theme,
    toggleTheme,
    isDark: theme === "dark",
    isLight: theme === "light",
  };

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
};
