import React, { createContext, useContext, useState, ReactNode } from 'react';
import { useWhiteLabel } from './WhiteLabelContext';

interface Theme {
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    border: string;
    success: string;
    warning: string;
    error: string;
  };
  spacing: {
    xs: number;
    sm: number;
    md: number;
    lg: number;
    xl: number;
  };
  borderRadius: {
    sm: number;
    md: number;
    lg: number;
    full: number;
  };
  typography: {
    fontFamily: string;
    sizes: {
      xs: number;
      sm: number;
      md: number;
      lg: number;
      xl: number;
      xxl: number;
    };
  };
}

const createTheme = (primaryColor: string, secondaryColor: string, accentColor: string, backgroundColor: string, textColor: string, fontFamily: string): Theme => ({
  colors: {
    primary: primaryColor,
    secondary: secondaryColor,
    accent: accentColor,
    background: backgroundColor,
    surface: '#FFFFFF',
    text: textColor,
    textSecondary: '#6B7280',
    border: '#E5E7EB',
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 16,
    full: 9999,
  },
  typography: {
    fontFamily,
    sizes: {
      xs: 10,
      sm: 12,
      md: 14,
      lg: 16,
      xl: 20,
      xxl: 28,
    },
  },
});

interface ThemeContextType {
  theme: Theme;
  isDark: boolean;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { config } = useWhiteLabel();
  const [isDark, setIsDark] = useState(false);

  const theme = createTheme(
    config.primaryColor,
    config.secondaryColor,
    config.accentColor,
    isDark ? '#1F2937' : config.backgroundColor,
    isDark ? '#FFFFFF' : config.textColor,
    config.fontFamily
  );

  const toggleTheme = () => setIsDark(!isDark);

  return (
    <ThemeContext.Provider value={{ theme, isDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};