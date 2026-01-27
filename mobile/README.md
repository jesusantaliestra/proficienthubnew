# ProficientHub Mobile App

A React Native / Expo mobile application for English proficiency exam preparation with AI tutoring, offline support, and white-label customization.

## 🚀 Features

- **Multi-Platform**: iOS and Android from a single codebase
- **AI Tutoring**: Voice-enabled AI tutor for exam practice
- **Offline Mode**: Download and study materials offline
- **White-Label Ready**: Full customization for institutions
- **Dark Mode**: System-aware theme support
- **Multi-Language**: 6+ language support

## 📁 Project Structure

```
mobile/
├── App.tsx                      # App entry point
├── app.json                     # Expo configuration
├── eas.json                     # EAS Build configuration
├── white-label.config.js        # White-label customization
├── src/
│   ├── components/              # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Badge.tsx
│   │   └── index.ts
│   ├── contexts/                # React contexts
│   │   ├── AuthContext.tsx      # Authentication state
│   │   ├── ThemeContext.tsx     # Theme management
│   │   └── WhiteLabelContext.tsx # White-label config
│   ├── hooks/                   # Custom hooks
│   │   ├── useOffline.ts        # Offline functionality
│   │   ├── useVoice.ts          # Voice recording/playback
│   │   └── index.ts
│   ├── navigation/              # Navigation setup
│   │   ├── RootNavigator.tsx
│   │   └── MainTabs.tsx
│   ├── screens/                 # App screens
│   │   ├── HomeScreen.tsx
│   │   ├── ExamsScreen.tsx
│   │   ├── MaterialsScreen.tsx
│   │   ├── ProgressScreen.tsx
│   │   ├── ProfileScreen.tsx
│   │   ├── LoginScreen.tsx
│   │   └── SplashScreen.tsx
│   ├── services/                # API and storage services
│   │   ├── api.ts
│   │   └── offlineStorage.ts
│   ├── theme/                   # Design system
│   │   ├── colors.ts
│   │   ├── spacing.ts
│   │   ├── typography.ts
│   │   └── index.ts
│   └── assets/                  # Images, fonts, etc.
```

## 🛠 Setup

### Prerequisites

- Node.js 18+
- Yarn
- Expo CLI: `npm install -g expo-cli`
- EAS CLI: `npm install -g eas-cli`

### Installation

```bash
cd mobile
yarn install
```

### Development

```bash
# Start Expo development server
yarn start

# Run on iOS simulator
yarn ios

# Run on Android emulator
yarn android
```

### Building

```bash
# Login to Expo
eas login

# Build for development
eas build --profile development --platform all

# Build for preview (internal testing)
eas build --profile preview --platform all

# Build for production
eas build --profile production --platform all
```

## ⚙️ White-Label Configuration

Edit `white-label.config.js` to customize:

```javascript
module.exports = {
  institution: {
    name: 'Your Academy',
    slug: 'your-academy',
    tagline: 'Your Tagline',
  },
  branding: {
    colors: {
      primary: '#YOUR_COLOR',
      secondary: '#YOUR_COLOR',
    },
    logo: {
      light: 'https://...',
      dark: 'https://...',
    },
  },
  features: {
    aiTutor: true,
    offlineMode: true,
    // ... toggle features
  },
};
```

## 📱 App Features

### Exam Practice
- IELTS, TOEFL, Cambridge, Trinity, PTE, OET support
- Reading, Writing, Listening, Speaking sections
- Timed practice tests
- AI-powered feedback

### AI Tutor
- Voice-enabled conversations
- Exam-specific coaching
- Real-time feedback
- Multiple voice options

### Offline Mode
- Download study materials
- Practice without internet
- Auto-sync when online

### Progress Tracking
- Performance analytics
- Skill breakdown
- Study streak tracking

## 🔐 Authentication

The app supports:
- Email/Password login
- Institutional login (white-label)
- Provisional credentials for students
- Biometric authentication (optional)

## 🌐 API Integration

Update `src/services/api.ts` with your API URL:

```typescript
const API_BASE_URL = 'https://your-api-url.com/api';
```

Or set it in `app.json`:

```json
"extra": {
  "apiUrl": "https://your-api-url.com/api"
}
```

## 📦 Dependencies

- **expo**: ~50.0.0
- **react-native**: 0.73.2
- **react-navigation**: 6.x
- **expo-av**: Audio/Video handling
- **expo-secure-store**: Secure storage
- **expo-file-system**: File management
- **axios**: HTTP client

## 🚀 Deployment

### iOS App Store
1. Configure `eas.json` with your Apple credentials
2. Run `eas build --platform ios --profile production`
3. Run `eas submit --platform ios`

### Google Play Store
1. Add `google-services.json` for Firebase
2. Run `eas build --platform android --profile production`
3. Run `eas submit --platform android`

## 📄 License

Proprietary - ProficientHub

---

Built with ❤️ using Expo and React Native
