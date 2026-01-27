import React from 'react';
import { View, Text, StyleSheet, ViewStyle, TextStyle } from 'react-native';
import { useTheme } from '../contexts/ThemeContext';

interface BadgeProps {
  text: string;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export const Badge: React.FC<BadgeProps> = ({
  text,
  variant = 'default',
  size = 'md',
  color,
  style,
  textStyle,
}) => {
  const { theme } = useTheme();

  const getVariantStyles = (): { container: ViewStyle; text: TextStyle } => {
    const customColor = color || theme.colors.primary;
    
    switch (variant) {
      case 'success':
        return {
          container: { backgroundColor: '#D1FAE5' },
          text: { color: '#059669' },
        };
      case 'warning':
        return {
          container: { backgroundColor: '#FEF3C7' },
          text: { color: '#D97706' },
        };
      case 'error':
        return {
          container: { backgroundColor: '#FEE2E2' },
          text: { color: '#DC2626' },
        };
      case 'info':
        return {
          container: { backgroundColor: '#DBEAFE' },
          text: { color: '#2563EB' },
        };
      case 'outline':
        return {
          container: { 
            backgroundColor: 'transparent', 
            borderWidth: 1, 
            borderColor: customColor 
          },
          text: { color: customColor },
        };
      default:
        return {
          container: { backgroundColor: `${customColor}20` },
          text: { color: customColor },
        };
    }
  };

  const getSizeStyles = (): { container: ViewStyle; text: TextStyle } => {
    switch (size) {
      case 'sm':
        return {
          container: { paddingHorizontal: 6, paddingVertical: 2 },
          text: { fontSize: 10 },
        };
      case 'lg':
        return {
          container: { paddingHorizontal: 12, paddingVertical: 6 },
          text: { fontSize: 14 },
        };
      default:
        return {
          container: { paddingHorizontal: 8, paddingVertical: 4 },
          text: { fontSize: 12 },
        };
    }
  };

  const variantStyles = getVariantStyles();
  const sizeStyles = getSizeStyles();

  return (
    <View style={[styles.container, variantStyles.container, sizeStyles.container, style]}>
      <Text style={[styles.text, variantStyles.text, sizeStyles.text, textStyle]}>
        {text}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  text: {
    fontWeight: '600',
  },
});
