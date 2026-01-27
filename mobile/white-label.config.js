// ProficientHub Mobile - White-Label Configuration
// This file controls all white-label customization options

module.exports = {
  // Institution Configuration (Replace with your institution details)
  institution: {
    id: 'proficienthub',
    name: 'ProficientHub',
    slug: 'proficienthub',
    tagline: 'Master Your English Exams',
    supportEmail: 'support@proficienthub.com',
    website: 'https://proficienthub.com',
  },

  // API Configuration
  api: {
    // Base URL for the API
    baseUrl: process.env.API_URL || 'https://your-api-domain.com/api',
    // Timeout in milliseconds
    timeout: 30000,
  },

  // Branding Configuration
  branding: {
    // Colors (can be overridden per institution)
    colors: {
      primary: '#58CC02',
      primaryDark: '#46a302',
      secondary: '#1CB0F6',
      accent: '#FF4B4B',
      background: '#FFFFFF',
      text: '#1F2937',
    },

    // Logo URLs
    logo: {
      // Light background logo
      light: null, // Will use default if null
      // Dark background logo
      dark: null,
      // App icon
      icon: null,
    },

    // Typography
    fonts: {
      // Custom fonts (must be bundled with the app)
      heading: null, // Uses system font if null
      body: null,
    },
  },

  // Feature Toggles
  features: {
    // AI Tutor with voice
    aiTutor: true,
    // Voice input/output
    voiceFeatures: true,
    // Offline mode
    offlineMode: true,
    // Dark mode toggle
    darkMode: true,
    // Multi-language support
    multiLanguage: true,
    // Push notifications
    pushNotifications: true,
    // Progress analytics
    analytics: true,
    // Gamification features
    gamification: true,
    // Video classes
    videoClasses: true,
    // Flashcards
    flashcards: true,
  },

  // Supported Languages
  languages: [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'pt', name: 'Português', flag: '🇧🇷' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
    { code: 'it', name: 'Italiano', flag: '🇮🇹' },
  ],

  // Supported Exam Types
  examTypes: [
    { id: 'ielts', name: 'IELTS', color: '#FF4B4B', icon: 'clipboard-list' },
    { id: 'toefl', name: 'TOEFL', color: '#1CB0F6', icon: 'school' },
    { id: 'cambridge', name: 'Cambridge', color: '#CE82FF', icon: 'award' },
    { id: 'trinity', name: 'Trinity', color: '#EC4899', icon: 'certificate' },
    { id: 'toeic', name: 'TOEIC', color: '#6366F1', icon: 'briefcase' },
    { id: 'celpip', name: 'CELPIP', color: '#06B6D4', icon: 'maple-leaf' },
    { id: 'pte', name: 'PTE', color: '#FF9600', icon: 'microphone' },
    { id: 'oet', name: 'OET', color: '#58CC02', icon: 'stethoscope' },
  ],

  // App Store Configuration (for EAS builds)
  appStore: {
    ios: {
      bundleIdentifier: 'com.proficienthub.app',
      appStoreId: null, // App Store ID once published
    },
    android: {
      packageName: 'com.proficienthub.app',
      playStoreUrl: null, // Play Store URL once published
    },
  },

  // Analytics Configuration
  analytics: {
    // Enable analytics tracking
    enabled: true,
    // Providers (configure in app.json extra)
    providers: ['internal'], // Options: 'internal', 'firebase', 'amplitude', 'mixpanel'
  },

  // Notification Configuration
  notifications: {
    // Enable push notifications
    enabled: true,
    // Notification channels (Android)
    channels: [
      { id: 'study_reminders', name: 'Study Reminders', importance: 'high' },
      { id: 'progress_updates', name: 'Progress Updates', importance: 'default' },
      { id: 'live_classes', name: 'Live Classes', importance: 'high' },
      { id: 'promotional', name: 'Promotional', importance: 'low' },
    ],
  },

  // Deep Linking Configuration
  deepLinking: {
    scheme: 'proficienthub',
    prefixes: ['proficienthub://', 'https://app.proficienthub.com'],
  },

  // Custom Screens to Hide/Show
  screens: {
    showOnboarding: true,
    showTutorial: true,
    showReferral: true,
    showLeaderboard: true,
    showCommunity: false, // Coming soon
  },
};
