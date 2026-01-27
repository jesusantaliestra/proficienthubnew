import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../services/api';

interface WhiteLabelConfig {
  platformName: string;
  logoUrl: string | null;
  logoDarkUrl: string | null;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  backgroundColor: string;
  textColor: string;
  fontFamily: string;
  showPoweredBy: boolean;
  institutionSlug: string | null;
}

const defaultConfig: WhiteLabelConfig = {
  platformName: 'ProficientHub',
  logoUrl: null,
  logoDarkUrl: null,
  primaryColor: '#58CC02',
  secondaryColor: '#1CB0F6',
  accentColor: '#FF4B4B',
  backgroundColor: '#FFFFFF',
  textColor: '#1F2937',
  fontFamily: 'System',
  showPoweredBy: true,
  institutionSlug: null,
};

interface WhiteLabelContextType {
  config: WhiteLabelConfig;
  loading: boolean;
  setInstitutionSlug: (slug: string) => Promise<void>;
  refreshConfig: () => Promise<void>;
}

const WhiteLabelContext = createContext<WhiteLabelContextType | undefined>(undefined);

export const WhiteLabelProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [config, setConfig] = useState<WhiteLabelConfig>(defaultConfig);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSavedConfig();
  }, []);

  const loadSavedConfig = async () => {
    try {
      const savedSlug = await AsyncStorage.getItem('institutionSlug');
      if (savedSlug) {
        await fetchConfigBySlug(savedSlug);
      }
    } catch (error) {
      console.error('Failed to load saved config:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchConfigBySlug = async (slug: string) => {
    try {
      const response = await api.get(`/whitelabel/by-domain/${slug}`);
      if (response.data.config && !response.data.is_default) {
        const c = response.data.config;
        setConfig({
          platformName: c.platform_name || defaultConfig.platformName,
          logoUrl: c.logo_url,
          logoDarkUrl: c.logo_dark_url,
          primaryColor: c.primary_color || defaultConfig.primaryColor,
          secondaryColor: c.secondary_color || defaultConfig.secondaryColor,
          accentColor: c.accent_color || defaultConfig.accentColor,
          backgroundColor: c.background_color || defaultConfig.backgroundColor,
          textColor: c.text_color || defaultConfig.textColor,
          fontFamily: c.font_family || defaultConfig.fontFamily,
          showPoweredBy: c.show_powered_by ?? true,
          institutionSlug: slug,
        });
      }
    } catch (error) {
      console.error('Failed to fetch white-label config:', error);
    }
  };

  const setInstitutionSlug = async (slug: string) => {
    await AsyncStorage.setItem('institutionSlug', slug);
    await fetchConfigBySlug(slug);
  };

  const refreshConfig = async () => {
    if (config.institutionSlug) {
      await fetchConfigBySlug(config.institutionSlug);
    }
  };

  return (
    <WhiteLabelContext.Provider value={{ config, loading, setInstitutionSlug, refreshConfig }}>
      {children}
    </WhiteLabelContext.Provider>
  );
};

export const useWhiteLabel = () => {
  const context = useContext(WhiteLabelContext);
  if (!context) {
    throw new Error('useWhiteLabel must be used within WhiteLabelProvider');
  }
  return context;
};