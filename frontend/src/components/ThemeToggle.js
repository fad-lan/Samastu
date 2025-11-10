import React from 'react';
import { Sun, Moon } from 'lucide-react';

const ThemeToggle = ({ theme, onToggleTheme, className = '' }) => {
  return (
    <button
      onClick={onToggleTheme}
      data-testid="theme-toggle-button"
      className={`p-2 rounded-full transition-colors ${className}`}
      style={{ 
        backgroundColor: 'var(--bg-secondary)',
        color: 'var(--text-primary)'
      }}
      aria-label="Toggle theme"
    >
      {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
    </button>
  );
};

export default ThemeToggle;
