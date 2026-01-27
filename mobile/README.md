# ProficientHub Mobile App

React Native (Expo) app with **White-Label Support** for iOS and Android.

## 🚀 Features

### White-Label System
- **Custom Domain Support**: Each institution can have their own domain
- **Dynamic Theming**: Colors, fonts, and branding from backend config
- **Institution Code Entry**: Students enter their academy code at startup
- **Custom Logo & Branding**: Institution logos displayed throughout

### Offline Mode
- **Download Materials**: Save PDFs, flashcards, and audio for offline use
- **Secure Storage**: Encrypted local storage for user data
- **Sync on Reconnect**: Automatic data sync when back online

### Core Features
- 📚 **Study Materials**: Access learning resources
- 📝 **Practice Exams**: Take mock tests (Reading, Writing, Listening, Speaking)
- 📊 **Progress Tracking**: View scores and improvement
- 🤖 **AI Tutor**: Chat with AI for help
- 🎙️ **Speaking Practice**: Voice recording and feedback

## 📱 Screens

| Screen | Description |
|--------|-------------|
| `InstitutionSelectScreen` | Enter institution code for white-label |
| `LoginScreen` | User authentication |
| `HomeScreen` | Dashboard with stats and quick actions |
| `ExamsScreen` | Practice tests by section |
| `MaterialsScreen` | Study materials with offline support |
| `ProgressScreen` | Performance analytics |
| `ProfileScreen` | User settings and preferences |

## 🎨 White-Label Configuration

The app automatically loads branding based on institution:

```typescript
// Example white-label config
{
  platformName: "Oxford Academy",
  logoUrl: "https://...",
  primaryColor: "#003366",
  secondaryColor: "#0066CC",
  showPoweredBy: false, // Hide "Powered by ProficientHub"
}
```

## 🛠️ Setup

### Prerequisites
- Node.js 18+
- Expo CLI: `npm install -g expo-cli`
- iOS: Xcode (Mac only)
- Android: Android Studio

### Installation

```bash
cd mobile
yarn install
```

### Development

```bash
# Start Expo dev server
yarn start

# Run on iOS
yarn ios

# Run on Android
yarn android
```

### Building for Production

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Build for both platforms
eas build --platform all

# Or separately
eas build --platform ios
eas build --platform android
```

## 📁 Project Structure

```
mobile/
├── App.tsx                    # App entry point
├── app.json                   # Expo configuration
├── package.json               # Dependencies
└── src/
    ├── contexts/
    │   ├── AuthContext.tsx    # Authentication state
    │   ├── ThemeContext.tsx   # Dynamic theming
    │   └── WhiteLabelContext.tsx  # Institution branding
    ├── navigation/
    │   ├── RootNavigator.tsx  # Auth flow navigation
    │   └── MainTabs.tsx       # Bottom tab navigation
    ├── screens/
    │   ├── SplashScreen.tsx
    │   ├── InstitutionSelectScreen.tsx
    │   ├── LoginScreen.tsx
    │   ├── HomeScreen.tsx
    │   ├── ExamsScreen.tsx
    │   ├── MaterialsScreen.tsx
    │   ├── ProgressScreen.tsx
    │   └── ProfileScreen.tsx
    ├── services/
    │   ├── api.ts             # API client
    │   └── offlineStorage.ts  # Offline data management
    └── theme/
        └── (theme utilities)
```

## 🔧 Configuration

### API URL

Update the API URL in `src/services/api.ts`:

```typescript
const API_BASE_URL = 'https://your-api-url.com/api';
```

Or use Expo config:

```json
// app.json
{
  "expo": {
    "extra": {
      "apiUrl": "https://your-api-url.com/api"
    }
  }
}
```

### White-Label for Different Institutions

Each institution gets their own branded app by:

1. **Runtime Detection**: Student enters institution code
2. **Build Variants**: Create separate builds with different configs

For production, create `app.config.js`:

```javascript
export default {
  name: process.env.APP_NAME || "ProficientHub",
  slug: process.env.APP_SLUG || "proficienthub",
  // ... other config
  extra: {
    institutionSlug: process.env.INSTITUTION_SLUG,
    apiUrl: process.env.API_URL,
  }
};
```

## 📲 App Store Submission

### iOS (App Store)
1. Create app in App Store Connect
2. Run `eas build --platform ios`
3. Submit using `eas submit --platform ios`

### Android (Google Play)
1. Create app in Google Play Console
2. Run `eas build --platform android`
3. Submit using `eas submit --platform android`

## 🔒 Security

- User credentials stored in Expo SecureStore
- JWT tokens for API authentication
- Offline data encrypted locally

## 📞 Support

For issues or questions, contact support@proficienthub.com
