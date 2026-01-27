import React from 'react';
import { View, ActivityIndicator, StyleSheet, Text, Image } from 'react-native';
import { useWhiteLabel } from '../contexts/WhiteLabelContext';
import { useTheme } from '../contexts/ThemeContext';

const SplashScreen: React.FC = () => {
  const { config } = useWhiteLabel();
  const { theme } = useTheme();

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.primary }]}>
      {config.logoUrl ? (
        <Image source={{ uri: config.logoDarkUrl || config.logoUrl }} style={styles.logo} resizeMode="contain" />
      ) : (
        <Text style={styles.title}>{config.platformName}</Text>
      )}
      <ActivityIndicator size="large" color="#FFFFFF" style={styles.loader} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  logo: {
    width: 200,
    height: 80,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  loader: {
    marginTop: 24,
  },
});

export default SplashScreen;