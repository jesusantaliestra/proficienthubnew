/**
 * White-Label Service for Dynamic Branding
 * Handles institution-specific branding in the mobile app
 */

import { Preferences } from '@capacitor/preferences';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Default branding
const DEFAULT_BRANDING = {
  name: 'ProficientHub',
  primaryColor: '#7c3aed',
  secondaryColor: '#4f46e5',
  accentColor: '#10b981',
  logoUrl: null,
  tagline: 'Master English Proficiency',
  fontFamily: 'Inter'
};

class WhiteLabelService {
  constructor() {
    this.currentBranding = { ...DEFAULT_BRANDING };
    this.institutionId = null;
  }

  /**
   * Initialize branding from stored preferences or fetch from API
   */
  async initialize() {
    try {
      // Check stored branding
      const { value: storedBranding } = await Preferences.get({ key: 'institution_branding' });
      const { value: storedInstId } = await Preferences.get({ key: 'institution_id' });

      if (storedBranding) {
        this.currentBranding = JSON.parse(storedBranding);
        this.institutionId = storedInstId;
      }

      return this.currentBranding;
    } catch (error) {
      console.error('WhiteLabel init error:', error);
      return DEFAULT_BRANDING;
    }
  }

  /**
   * Load branding for a specific institution
   * @param {string} institutionId - Institution ID from user login
   */
  async loadBranding(institutionId) {
    try {
      const token = localStorage.getItem('token');
      
      const response = await axios.get(`${API_URL}/api/institution/branding`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const branding = {
        ...DEFAULT_BRANDING,
        ...response.data,
        name: response.data.name || response.data.institution_name || DEFAULT_BRANDING.name,
        primaryColor: response.data.primary_color || DEFAULT_BRANDING.primaryColor,
        secondaryColor: response.data.secondary_color || DEFAULT_BRANDING.secondaryColor,
        accentColor: response.data.accent_color || DEFAULT_BRANDING.accentColor,
        logoUrl: response.data.logo_url,
        tagline: response.data.tagline || DEFAULT_BRANDING.tagline
      };

      // Store for offline use
      await Preferences.set({
        key: 'institution_branding',
        value: JSON.stringify(branding)
      });
      await Preferences.set({
        key: 'institution_id',
        value: institutionId
      });

      this.currentBranding = branding;
      this.institutionId = institutionId;

      // Apply branding to DOM
      this.applyBranding(branding);

      return branding;
    } catch (error) {
      console.error('Failed to load branding:', error);
      return this.currentBranding;
    }
  }

  /**
   * Load branding by institution slug (for white-label URLs)
   * @param {string} slug - Institution slug from URL
   */
  async loadBrandingBySlug(slug) {
    try {
      const response = await axios.get(`${API_URL}/api/institution/branding/${slug}`);

      const branding = {
        ...DEFAULT_BRANDING,
        ...response.data,
        name: response.data.name || DEFAULT_BRANDING.name,
        primaryColor: response.data.primary_color || DEFAULT_BRANDING.primaryColor,
        secondaryColor: response.data.secondary_color || DEFAULT_BRANDING.secondaryColor,
        accentColor: response.data.accent_color || DEFAULT_BRANDING.accentColor,
        logoUrl: response.data.logo_url,
        tagline: response.data.tagline || DEFAULT_BRANDING.tagline
      };

      this.currentBranding = branding;
      this.applyBranding(branding);

      return branding;
    } catch (error) {
      console.error('Failed to load branding by slug:', error);
      return DEFAULT_BRANDING;
    }
  }

  /**
   * Apply branding to the app via CSS variables
   * @param {object} branding - Branding configuration
   */
  applyBranding(branding) {
    const root = document.documentElement;

    // Set CSS variables for theming
    root.style.setProperty('--brand-primary', branding.primaryColor);
    root.style.setProperty('--brand-secondary', branding.secondaryColor);
    root.style.setProperty('--brand-accent', branding.accentColor);
    
    if (branding.fontFamily) {
      root.style.setProperty('--brand-font', branding.fontFamily);
    }

    // Update meta theme-color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', branding.primaryColor);
    }

    // Update page title
    document.title = branding.name;
  }

  /**
   * Get current branding
   */
  getBranding() {
    return this.currentBranding;
  }

  /**
   * Clear branding (on logout)
   */
  async clearBranding() {
    await Preferences.remove({ key: 'institution_branding' });
    await Preferences.remove({ key: 'institution_id' });
    this.currentBranding = { ...DEFAULT_BRANDING };
    this.institutionId = null;
    this.applyBranding(DEFAULT_BRANDING);
  }

  /**
   * Check if running in Capacitor native app
   */
  isNativeApp() {
    return window.Capacitor?.isNativePlatform?.() || false;
  }

  /**
   * Get platform (web, ios, android)
   */
  getPlatform() {
    return window.Capacitor?.getPlatform?.() || 'web';
  }
}

// Singleton instance
const whiteLabelService = new WhiteLabelService();
export default whiteLabelService;
