// ProficientHub Mobile - Color System
// White-label ready color configuration

export const defaultColors = {
  // Brand Colors (can be overridden by white-label)
  primary: '#58CC02',
  primaryDark: '#46a302',
  primaryLight: '#7FDB33',
  
  secondary: '#1CB0F6',
  secondaryDark: '#0C8ECC',
  secondaryLight: '#53C3F8',
  
  accent: '#FF4B4B',
  accentDark: '#CC3C3C',
  accentLight: '#FF7373',
  
  // Background Colors
  background: '#FFFFFF',
  backgroundSecondary: '#F9FAFB',
  backgroundTertiary: '#F3F4F6',
  
  // Surface Colors
  surface: '#FFFFFF',
  surfaceElevated: '#FFFFFF',
  
  // Text Colors
  text: '#1F2937',
  textSecondary: '#6B7280',
  textTertiary: '#9CA3AF',
  textInverse: '#FFFFFF',
  
  // Border Colors
  border: '#E5E7EB',
  borderLight: '#F3F4F6',
  borderFocus: '#58CC02',
  
  // Status Colors
  success: '#10B981',
  successLight: '#D1FAE5',
  warning: '#F59E0B',
  warningLight: '#FEF3C7',
  error: '#EF4444',
  errorLight: '#FEE2E2',
  info: '#3B82F6',
  infoLight: '#DBEAFE',
  
  // Exam Type Colors
  examColors: {
    ielts: '#FF4B4B',
    toefl: '#1CB0F6',
    cambridge: '#CE82FF',
    trinity: '#EC4899',
    toeic: '#6366F1',
    celpip: '#06B6D4',
    pte: '#FF9600',
    oet: '#58CC02',
  },
  
  // Risk Level Colors
  riskColors: {
    low: '#10B981',
    medium: '#F59E0B',
    high: '#EF4444',
  },
  
  // Gradient Definitions
  gradients: {
    primary: ['#58CC02', '#46a302'],
    secondary: ['#1CB0F6', '#0C8ECC'],
    accent: ['#FF4B4B', '#CC3C3C'],
    success: ['#10B981', '#059669'],
    warning: ['#F59E0B', '#D97706'],
    error: ['#EF4444', '#DC2626'],
    purple: ['#8B5CF6', '#7C3AED'],
    blue: ['#3B82F6', '#2563EB'],
  },
};

export const darkColors = {
  ...defaultColors,
  background: '#111827',
  backgroundSecondary: '#1F2937',
  backgroundTertiary: '#374151',
  surface: '#1F2937',
  surfaceElevated: '#374151',
  text: '#F9FAFB',
  textSecondary: '#D1D5DB',
  textTertiary: '#9CA3AF',
  border: '#374151',
  borderLight: '#4B5563',
};

export type ColorScheme = typeof defaultColors;
