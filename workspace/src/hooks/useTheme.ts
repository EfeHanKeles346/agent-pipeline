import { useState, useEffect } from 'react';
import { safeLocalStorage } from '@/lib/utils';

export type Theme = 'light' | 'dark';

export const useTheme = () => {
  const [theme, setTheme] = useState<Theme>(() => {
    // SSR safety check
    if (typeof window === 'undefined') {
      return 'dark';
    }

    const storage = safeLocalStorage();
    
    // Check localStorage first
    const saved = storage.getItem('theme');
    if (saved === 'light' || saved === 'dark') {
      return saved as Theme;
    }
    
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    
    return 'dark'; // Default to dark as per project requirements
  });

  useEffect(() => {
    const root = document.documentElement;
    
    if (theme === 'dark') {
      root.classList.add('dark');
      root.classList.remove('light');
    } else {
      root.classList.add('light');
      root.classList.remove('dark');
    }
    
    const storage = safeLocalStorage();
    storage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return { theme, toggleTheme };
};
