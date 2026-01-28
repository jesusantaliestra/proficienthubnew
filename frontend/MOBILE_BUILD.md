# ProficientHub Mobile App - Build Instructions

## Prerequisites

1. **Node.js** >= 18
2. **Yarn** package manager
3. **Android Studio** (for Android builds)
4. **Xcode** (for iOS builds, Mac only)
5. **Capacitor CLI** (already installed in project)

## Project Structure

```
/app/frontend/
├── capacitor.config.json    # Capacitor configuration
├── android/                 # Android native project (generated)
├── ios/                     # iOS native project (generated)
├── public/
│   └── service-worker.js    # PWA service worker
└── src/
    └── services/
        ├── whiteLabelService.js      # Dynamic branding
        ├── pushNotificationService.js # Push notifications
        └── offlineContentService.js   # Offline content
```

## Setup Commands

### 1. Build React App
```bash
cd /app/frontend
yarn build
```

### 2. Initialize Capacitor Platforms
```bash
npx cap add android
npx cap add ios
```

### 3. Sync Web Assets to Native Projects
```bash
npx cap sync
```

### 4. Open in IDE
```bash
# Android
npx cap open android

# iOS (Mac only)
npx cap open ios
```

## Building for Release

### Android APK/AAB

1. Open Android Studio: `npx cap open android`
2. Go to **Build > Generate Signed Bundle / APK**
3. Create or select keystore
4. Build APK or Android App Bundle (AAB for Play Store)

**Or via command line:**
```bash
cd android
./gradlew assembleRelease    # APK
./gradlew bundleRelease      # AAB
```

### iOS IPA

1. Open Xcode: `npx cap open ios`
2. Select your team in Signing & Capabilities
3. Go to **Product > Archive**
4. Export for App Store or Ad Hoc distribution

## White-Label Configuration

The app uses **dynamic white-labeling**. When a user logs in:
1. Backend returns `institution_id` with user data
2. App fetches branding from `/api/institution/branding`
3. UI updates with institution's logo, colors, name

### No code changes needed per institution!

## Push Notifications Setup

### Android (Firebase)
1. Create Firebase project
2. Add `google-services.json` to `android/app/`
3. Push tokens auto-registered via backend

### iOS (APNs)
1. Enable Push Notifications in Apple Developer Portal
2. Add capability in Xcode
3. Configure APNs key in backend

## Offline Mode

The app includes:
- **Service Worker** for caching
- **IndexedDB** for offline exam storage
- **Background Sync** for pending results

Students can download exams and practice offline!

## Environment Variables

Set in `.env` before build:
```
REACT_APP_BACKEND_URL=https://your-api-domain.com
```

## Premium App (Dedicated Store Listing)

For institutions wanting their own app in stores:

### Setup Fee: $2,000
### Monthly Fee: $200

**What they get:**
- Custom app name in stores
- Custom icon and splash screen
- Own App Store / Play Store listing
- Dedicated build pipeline
- Priority support

### Build Process for Premium:
1. Clone project
2. Update `capacitor.config.json`:
   - `appId`: `com.institution.appname`
   - `appName`: `Institution Name`
3. Replace icons in `android/app/src/main/res/` and `ios/App/Assets.xcassets/`
4. Build and submit to stores

## Quick Commands Reference

```bash
# Development
yarn start                    # Start dev server
npx cap sync                  # Sync web to native

# Build
yarn build                    # Build React
npx cap build android         # Build Android
npx cap build ios             # Build iOS

# Run on device
npx cap run android           # Run on Android device
npx cap run ios               # Run on iOS device

# Live reload during development
npx cap run android -l --external
npx cap run ios -l --external
```

## Troubleshooting

### "Module not found" errors
```bash
yarn install
npx cap sync
```

### Android build fails
- Update Android Studio
- Accept SDK licenses: `./android/gradlew --version`

### iOS build fails
- Run `pod install` in ios/App
- Update Xcode

## Support

For deployment issues, contact: support@proficienthub.com
