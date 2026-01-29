# ProficientHub Mobile App Build Guide

## Overview
This guide explains how to build native iOS and Android apps from the ProficientHub React web application using Capacitor.

## Prerequisites

### Development Environment
- Node.js 18+ 
- npm or yarn
- Xcode 14+ (for iOS)
- Android Studio (for Android)
- CocoaPods (for iOS)

### Install Capacitor CLI
```bash
npm install -g @capacitor/cli
```

## Project Setup

### 1. Initialize Capacitor in Frontend
```bash
cd /app/frontend

# Install Capacitor core and CLI
yarn add @capacitor/core @capacitor/cli

# Initialize Capacitor (if not already done)
npx cap init "ProficientHub" "com.proficienthub.app" --web-dir=build
```

### 2. Add Platform Plugins
```bash
# Add iOS and Android platforms
yarn add @capacitor/ios @capacitor/android

# Add native plugins
yarn add @capacitor/splash-screen
yarn add @capacitor/status-bar
yarn add @capacitor/keyboard
yarn add @capacitor/push-notifications
yarn add @capacitor/camera
yarn add @capacitor/filesystem
yarn add @capacitor/share
```

### 3. Configure capacitor.config.ts
```typescript
// /app/frontend/capacitor.config.ts
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.proficienthub.app',
  appName: 'ProficientHub',
  webDir: 'build',
  server: {
    androidScheme: 'https',
    // For development, use your backend URL
    // url: 'https://your-backend-url.com',
    // cleartext: true
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      launchAutoHide: true,
      backgroundColor: "#58CC02",
      androidSplashResourceName: "splash",
      androidScaleType: "CENTER_CROP",
      showSpinner: false,
      splashFullScreen: true,
      splashImmersive: true,
    },
    StatusBar: {
      style: "DARK",
      backgroundColor: "#58CC02"
    },
    Keyboard: {
      resize: "body",
      resizeOnFullScreen: true
    },
    PushNotifications: {
      presentationOptions: ["badge", "sound", "alert"]
    }
  },
  ios: {
    contentInset: "automatic",
    preferredContentMode: "mobile"
  },
  android: {
    allowMixedContent: true
  }
};

export default config;
```

## Build Process

### Step 1: Build React App
```bash
cd /app/frontend

# Set production API URL
export REACT_APP_BACKEND_URL=https://your-production-api.com

# Build the React app
yarn build
```

### Step 2: Add Native Platforms
```bash
# Add iOS platform
npx cap add ios

# Add Android platform  
npx cap add android
```

### Step 3: Sync Web Assets
```bash
# Copy web assets to native projects
npx cap sync
```

### Step 4: Open in IDE

#### iOS (Xcode)
```bash
npx cap open ios
```

In Xcode:
1. Select your development team in Signing & Capabilities
2. Update Bundle Identifier if needed
3. Configure app icons in Assets.xcassets
4. Build and run on simulator or device

#### Android (Android Studio)
```bash
npx cap open android
```

In Android Studio:
1. Wait for Gradle sync to complete
2. Update applicationId in build.gradle if needed
3. Add app icons to res/mipmap folders
4. Build and run on emulator or device

## iOS Specific Configuration

### Info.plist Permissions
Add these to `ios/App/App/Info.plist`:
```xml
<!-- Camera for profile photos -->
<key>NSCameraUsageDescription</key>
<string>ProficientHub needs camera access for profile photos and document scanning</string>

<!-- Microphone for speaking practice -->
<key>NSMicrophoneUsageDescription</key>
<string>ProficientHub needs microphone access for speaking practice sessions</string>

<!-- Speech Recognition -->
<key>NSSpeechRecognitionUsageDescription</key>
<string>ProficientHub uses speech recognition to evaluate your speaking</string>

<!-- Photo Library -->
<key>NSPhotoLibraryUsageDescription</key>
<string>ProficientHub needs photo library access to upload profile pictures</string>
```

### App Icons
Place your app icons in:
- `ios/App/App/Assets.xcassets/AppIcon.appiconset/`

Required sizes:
- 20x20, 29x29, 40x40, 58x58, 60x60, 76x76, 80x80, 87x87, 120x120, 152x152, 167x167, 180x180, 1024x1024

### Splash Screen
Place splash image at:
- `ios/App/App/Assets.xcassets/Splash.imageset/`

## Android Specific Configuration

### AndroidManifest.xml Permissions
Add to `android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.VIBRATE" />
```

### App Icons
Place your app icons in:
- `android/app/src/main/res/mipmap-mdpi/` (48x48)
- `android/app/src/main/res/mipmap-hdpi/` (72x72)
- `android/app/src/main/res/mipmap-xhdpi/` (96x96)
- `android/app/src/main/res/mipmap-xxhdpi/` (144x144)
- `android/app/src/main/res/mipmap-xxxhdpi/` (192x192)

### Splash Screen
Configure in `android/app/src/main/res/values/styles.xml`

## Push Notifications Setup

### iOS (APNs)
1. Enable Push Notifications in Xcode Capabilities
2. Create APNs key in Apple Developer Portal
3. Upload key to your push notification service

### Android (FCM)
1. Create project in Firebase Console
2. Download `google-services.json`
3. Place in `android/app/`
4. Add Firebase dependencies to build.gradle

## Building for Release

### iOS App Store
```bash
# In Xcode:
# 1. Select "Any iOS Device" as build target
# 2. Product > Archive
# 3. Distribute App > App Store Connect
```

### Google Play Store
```bash
cd android

# Generate signed APK
./gradlew assembleRelease

# Or generate AAB (recommended)
./gradlew bundleRelease
```

The signed APK/AAB will be in:
- `android/app/build/outputs/apk/release/`
- `android/app/build/outputs/bundle/release/`

## Development Workflow

### Live Reload (Development)
```bash
# Start React dev server
cd /app/frontend
yarn start

# In capacitor.config.ts, set:
# server: { url: 'http://YOUR_IP:3000' }

# Sync and run
npx cap sync
npx cap run ios  # or android
```

### Update Native Projects
After code changes:
```bash
yarn build
npx cap sync
```

## Troubleshooting

### iOS Build Errors
- Clean build folder: Xcode > Product > Clean Build Folder
- Update CocoaPods: `cd ios && pod install --repo-update`

### Android Build Errors
- Clean project: `cd android && ./gradlew clean`
- Invalidate caches: Android Studio > File > Invalidate Caches

### Plugin Issues
```bash
# Reinstall plugins
npx cap sync --force
```

## White-Label Support

For white-labeled apps, update:

1. **capacitor.config.ts**: Change appId and appName
2. **package.json**: Update name
3. **iOS**: Update Bundle Identifier in Xcode
4. **Android**: Update applicationId in build.gradle
5. **Icons**: Replace with institution-specific branding
6. **Splash**: Replace with institution logo/colors

## Environment Variables

Create `.env.production`:
```env
REACT_APP_BACKEND_URL=https://api.proficienthub.com
REACT_APP_WS_URL=wss://api.proficienthub.com
```

## Support

For build issues, contact:
- Technical Support: support@proficienthub.com
- Documentation: docs.proficienthub.com
