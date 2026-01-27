// ProficientHub Mobile - Theme System Index
export { defaultColors, darkColors, type ColorScheme } from './colors';
export { spacing, borderRadius, shadows } from './spacing';
export { typography, textStyles } from './typography';

// Combined theme type
export interface Theme {
  colors: typeof import('./colors').defaultColors;
  spacing: typeof import('./spacing').spacing;
  borderRadius: typeof import('./spacing').borderRadius;
  shadows: typeof import('./spacing').shadows;
  typography: typeof import('./typography').typography;
  textStyles: typeof import('./typography').textStyles;
}
