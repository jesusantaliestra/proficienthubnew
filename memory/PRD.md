# ProficientHub - PRD (Product Requirements Document)

## Overview
**Product Name:** ProficientHub  
**Version:** 4.0  
**Date:** January 27, 2026  
**Status:** Supreme Features Complete - Zoom, Email, Gamification, Restricted Dashboard

## Features Implemented (Session 8) - January 27, 2026

### 🎓 Student Dashboard Restricted
- **Exam Restriction**: Students only see their assigned exam (e.g., IELTS only)
- **No Exam Selection**: Removed ability for institutional students to browse other exams
- **Gamification Integration**: Shows XP, Level, Streak, Daily XP when enabled by institution
- **Live Classes**: Shows upcoming Zoom/video classes from their institution
- **Achievements**: Badges section with 10 achievement badges
- **Leaderboard**: Institution-wide ranking by XP
- **Weekly Challenges**: 3 customizable challenges with progress tracking

### 🤖 AI Avatar System (NEW)
- **Dual-Mode Architecture**:
  - **Animated Avatar (Free)**: Default option with 3 character styles (Prof. Smith, Ms. Johnson, Alex)
  - **HeyGen Premium**: Realistic AI video avatars for institutions that enable it
- **HeyGen Integration**:
  - API Key configuration per institution
  - Avatar selection (Sarah, James, Maya)
  - Voice selection
  - Monthly credit limit with usage tracking
  - Cost control with warnings
  - Video generation and status polling
- **Usage Dashboard**: Shows credits used vs limit, estimated costs absorbed

### ⚙️ Institution Settings (New Tab)
- **Avatar Tab** (NEW):
  - Toggle between Animated (free) and HeyGen (premium)
  - Avatar style selection for animated mode
  - HeyGen API configuration with usage tracking
  - Cost control warnings
- **Zoom Integration**:
  - Zoom Account ID, Client ID, Client Secret configuration
  - Enable/disable toggle
  - Test Connection button
- **Email SMTP Configuration**:
  - SMTP Host, Port, Username, Password
  - Quick presets: Gmail, Outlook, SendGrid, Mailgun
  - Send Test Email functionality
- **Gamification Settings**:
  - Master enable/disable toggle
  - XP per activity configuration
  - Streak bonus multiplier

### 🎮 Gamification System
- **XP System**: Earn XP for exams, sections, tutor sessions, live classes
- **Levels**: 10 levels from Beginner to Champion
- **Streaks**: Daily study streak tracking with bonus multiplier
- **Badges**: 10 achievement badges (First Steps, Week Warrior, Monthly Master, etc.)
- **Leaderboard**: Institution-wide ranking
- **Challenges**: Weekly challenges with XP rewards

### 📹 Zoom Integration
- **Meeting Creation**: Create scheduled Zoom meetings via API
- **JWT Signature Generation**: Secure signature for joining meetings
- **Meeting Storage**: Store meetings in MongoDB with join/start URLs
- **Student Access**: Students see upcoming classes with Join button

### 📁 New Files Created (Session 8)
- `/app/frontend/src/components/InstitutionSettings.jsx` - Settings UI (Avatar, Zoom, Email, Gamification)
- `/app/frontend/src/components/AIAvatar.jsx` - AI Avatar component (Animated + HeyGen)
- `/app/frontend/src/pages/StudentDashboardRestricted.jsx` - Restricted student dashboard

## Features Implemented (Session 7) - January 27, 2026

### 🆕 React Native Mobile App Base Structure
- **Project Scaffolding**: Complete Expo 50 project in `/app/mobile/`
- **White-Label Ready**: Configuration file `white-label.config.js`
- **Theme System**: Complete design tokens in `src/theme/`
- **Core Components**: Button, Card, Input, Badge
- **Custom Hooks**: `useOffline`, `useVoice`
- **EAS Build Configuration**: Ready for iOS/Android builds

### ⚡ CRM Supreme - Advanced CRM Features
- **Email Templates**: Reusable templates with dynamic variables
- **Automation Rules**: Triggers + Actions for automated workflows
- **Tasks Management**: Priority-based task tracking
- **Advanced Reports**: KPIs and Pipeline Health
- `/app/mobile/src/hooks/useOffline.ts` - Offline functionality hook
- `/app/mobile/src/hooks/useVoice.ts` - Audio recording hook
- `/app/mobile/src/hooks/index.ts` - Hook exports
- `/app/mobile/eas.json` - EAS Build configuration
- `/app/mobile/babel.config.js` - Babel configuration
- `/app/mobile/tsconfig.json` - TypeScript configuration
- `/app/frontend/src/components/CRMSupreme.jsx` - CRM Supreme UI component

## Original Problem Statement
Build a B2B/B2C SaaS platform for English proficiency exam preparation (TOEFL, IELTS, Cambridge, PTE, OET) with:
- Real-time exam simulators under exam conditions
- Premium instant AI feedback
- AI tutor agents with voice
- Offline capabilities
- B2B focus with institutional dashboard
- Multi-language support
- White-label student portals
- Provisional credential system

## Features Implemented (Session 6) - January 6, 2026

### 🆕 Nuevo Modelo de Precios por Paquetes de Exámenes
- **Análisis de costos completo** basado en precios reales de OpenAI y ElevenLabs 2025
- **Costos calculados por tipo de examen:**
  - TOEFL: $1.70/mock test
  - IELTS: $1.56/mock test
  - Cambridge: $1.90/mock test
  - PTE: $1.76/mock test
  - OET: $1.91/mock test
  - **Promedio: $1.77/mock test**
- **Costos individuales:**
  - Writing Test: $0.26/test
  - Speaking Test: $1.39/test
  - AI Tutor: $0.10/min (mixto)

### 📦 Paquetes de Exámenes
| Paquete | Mock Tests | AI Tutor | Precio | Margen |
|---------|------------|----------|--------|--------|
| Starter 20 | 20 | - | $118 | 70% |
| Starter 20 + AI | 20 | 60 min | $138 | 70% |
| Growth 40 | 40 | - | $354 | 80% |
| Growth 40 + AI | 40 | 150 min | $429 | 80% |
| Scale 100 | 100 | - | $1,770 | 90% |
| Scale 100 + AI | 100 | 500 min | $2,270 | 90% |

### 📊 Calculadora ROI de Paquetes
- Selector de paquete
- Número de estudiantes
- Precio por estudiante configurable
- Cálculo automático de: costo, margen, ganancia, ROI%
- Recomendaciones inteligentes

## Features Implemented (Session 5) - January 6, 2026

### 🆕 B2B Premium Authentication System
- **White-Label Student Portal**: `/student-portal/:slug` with institution branding (logo, colors, tagline)
- **Provisional Credentials**: Institutions create students with auto-generated 12-char passwords
- **Forced Password Change**: First login redirects to password change page
- **Password Requirements**: 8+ chars, uppercase, lowercase, number, special character
- **Student Credits System**: Credits for AI tutoring, writing feedback, voice practice
- **Institution Branding API**: `PUT /api/institution/branding` creates custom portal URLs

### Updated Add Student Dialog
- Exam Type selector (IELTS, TOEFL, Cambridge, PTE, OET)
- Initial credits allocation
- Shows provisional password after creation
- Copy credentials button

## Previous Features (Session 4)

### 1. 🎓 Complete Exam Simulators
- **5 Exam Types**: TOEFL, IELTS, Cambridge, PTE, OET
- **4 Sections Each**: Reading, Listening, Speaking, Writing
- **Real Questions**: Comprehensive question bank in `exam_questions.py`
- **Timed Tests**: Section-specific timers
- **Score Calculation**: Band scores, percentage, feedback

### 2. 🎤 AI Tutor with Voice (OpenAI TTS/STT)
- **Text Chat**: Conversational AI tutoring
- **Voice Mode**: Toggle voice on/off
- **9 TTS Voices**: alloy, ash, coral, echo, fable, nova, onyx, sage, shimmer
- **Speech-to-Text**: Voice input using Whisper
- **Exam-Specific**: Tutors for each exam type

### 3. 📴 Offline Mode
- **Service Worker**: `/public/service-worker.js`
- **Cache Strategy**: Static assets + API responses
- **Offline Indicator**: Shows when offline
- **useOffline Hook**: React hook for offline management

### 4. 🌍 Multi-Language Support
- **6 Languages**: English, Español, Português, Français, Deutsch, Italiano
- **Translations**: `/src/locales/translations.json`
- **i18n Integration**: Full i18next setup

### 5. 💰 Pricing & Payments
- **3-Tier Credits**: Basic (50), Medium (100), Intensive (200)
- **Test Packages**: Writing + Speaking packages for resale
- **Monetization Calculator**: ROI for institutions
- **Stripe Integration**: Checkout, webhooks, payment status

### 6. 🔐 Admin Panel
- **Dashboard Stats**: Users, institutions, transactions
- **API Key Management**: OpenAI, ElevenLabs, Stripe
- **System Status**: Backend, DB, Stripe indicators

## Technical Architecture

```
/app
├── backend/
│   ├── server.py           # FastAPI app (4900+ lines)
│   ├── exam_questions.py   # Question bank
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.jsx           # B2B landing + pricing
│   │   │   ├── ExamSimulator.jsx     # Full exam simulator
│   │   │   ├── AITutor.jsx           # Voice-enabled tutor
│   │   │   ├── AdminPanel.jsx        # Admin dashboard
│   │   │   ├── InstitutionDashboard.jsx  # Main institution portal
│   │   │   ├── StudentDashboard.jsx
│   │   │   ├── WhiteLabelSettings.jsx    # Premium white-label config
│   │   │   ├── PaymentSuccess.jsx
│   │   │   └── Auth.jsx
│   │   ├── components/
│   │   │   ├── CRMSupreme.jsx        # Advanced CRM component
│   │   │   └── ui/                   # Shadcn components
│   │   ├── hooks/
│   │   │   └── useOffline.js        # Offline hook
│   │   ├── locales/
│   │   │   └── translations.json    # i18n translations
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx
│   │   ├── i18n.js                  # i18next config
│   │   └── App.js
│   ├── public/
│   │   └── service-worker.js        # Offline support
│   └── package.json
├── mobile/                          # NEW: React Native App
│   ├── App.tsx                      # App entry point
│   ├── app.json                     # Expo config
│   ├── eas.json                     # EAS Build config
│   ├── white-label.config.js        # White-label settings
│   ├── src/
│   │   ├── components/              # Reusable components
│   │   ├── contexts/                # AuthContext, ThemeContext, WhiteLabelContext
│   │   ├── hooks/                   # useOffline, useVoice
│   │   ├── navigation/              # React Navigation setup
│   │   ├── screens/                 # App screens
│   │   ├── services/                # API and storage
│   │   └── theme/                   # Design system
│   └── package.json
└── memory/
    └── PRD.md
```

## API Endpoints

### B2B Authentication (NEW)
- `POST /api/auth/login` - Returns `requires_password_change` flag
- `POST /api/auth/change-password` - Change password (required on first login)
- `POST /api/institution/students/create` - Create student with provisional credentials
- `POST /api/institution/students/bulk-create` - Bulk student creation
- `PUT /api/institution/branding` - Set white-label branding (name, colors, logo)
- `GET /api/institution/branding/{slug}` - Get branding for student portal
- `GET /api/student/credits` - Get student credit balance
- `POST /api/student/use-credits` - Deduct credits for AI activities
- `PUT /api/institution/students/{id}/credits` - Update student credits
- `PUT /api/institution/students/{id}/exam` - Change student exam type

### Exams
- `GET /api/exams/types` - All exam types with configs
- `GET /api/exams/{examType}/practice` - Practice questions
- `GET /api/exams/{examType}/mock-test` - Full mock test
- `GET /api/exams/{examType}/speaking-prompts` - Speaking prompts
- `GET /api/exams/{examType}/writing-tasks` - Writing tasks
- `POST /api/exams/submit` - Submit exam attempt

### Voice (OpenAI TTS/STT)
- `GET /api/voice/available-voices` - List 9 TTS voices
- `POST /api/voice/text-to-speech` - Generate audio
- `POST /api/voice/speech-to-text` - Transcribe audio
- `POST /api/ai-tutor/voice-chat` - Voice chat with tutor
- `POST /api/speaking-test/submit` - Submit speaking for AI eval

### Pricing & Payments
- `GET /api/pricing/test-packages` - Writing/Speaking packages
- `POST /api/pricing/monetization-calculator` - Calculate profits
- `POST /api/checkout/subscription` - Stripe checkout
- `POST /api/checkout/test-package` - Package checkout
- `GET /api/checkout/status/{session_id}` - Payment status

### Admin
- `GET /api/admin/stats` - Dashboard statistics
- `GET /api/admin/settings` - API key settings
- `POST /api/admin/settings` - Save API keys

## Test Results (Session 5) - January 6, 2026
- **B2B Auth Backend**: 100% (17/17 tests passed)
- **B2B Auth Frontend**: 100% (all features working)
- **Test File**: `/app/tests/test_b2b_auth_system.py`

## Test Results (Session 4)
- **Backend**: 100% (20/20 tests passed)
- **Frontend**: 100% (all features working)
- **Test File**: `/app/tests/test_exam_features.py`

## Credentials
- **Admin**: santaliestralimited@gmail.com / Admin123!
- **Institution**: demo_academy@test.com / Demo123!
- **Student (first login)**: student1@demo.com / 62Wuaor4R4Qp (requires password change)

## URLs
- Landing: https://edutorpro.preview.emergentagent.com
- Login: https://edutorpro.preview.emergentagent.com/login
- Admin: https://edutorpro.preview.emergentagent.com/admin
- Student Portal: https://edutorpro.preview.emergentagent.com/student-portal
- White-Label Portal: https://edutorpro.preview.emergentagent.com/student-portal/demo-language-academy
- AI Tutor: https://edutorpro.preview.emergentagent.com/tutor/ielts
- Exam: https://edutorpro.preview.emergentagent.com/exam/ielts

## Remaining Backlog

### P0 - Completed ✅
- [x] React Native base structure with white-label support
- [x] CRM Supreme UI (Email Templates, Automations, Tasks, Reports)
- [x] Student Dashboard Restricted (only assigned exam)
- [x] Institution Settings (Avatar, Zoom, Email, Gamification)
- [x] Complete Gamification System (XP, Levels, Streaks, Badges, Leaderboard, Challenges)
- [x] Zoom SDK Integration (meetings, signatures)
- [x] Premium Avatar System (Animated free + HeyGen premium)
- [x] Content Library (Materials upload, Vocabulary, Flashcards, Offline)
- [x] Placement Test configurable (mandatory/optional/free)
- [x] Demo data for institutions showcase

### P1 - High Priority
- [ ] Integrate Avatar in AI Tutor (animated + premium option)
- [ ] Complete React Native app screens (login, exam, tutor, classes)
- [ ] WhatsApp/SMS provider configuration per institution
- [ ] Real email sending from CRM automations

### P2 - Medium Priority
- [ ] Video streaming with Zoom embedded in platform
- [ ] Push notifications for mobile
- [ ] Superadmin dashboard for ProficientHub

### P3 - Nice to Have
- [ ] AI-generated flashcard definitions
- [ ] Additional language translations

## Business Model Notes
- **Premium Avatar**: Included in institutional plan, institutions set credit limits
- **Free Minutes for Students**: Institutions can offer X free minutes of premium AI tutor to students for conversion
- **Placement Test**: Configurable per institution (mandatory/optional/free)
- **Mock Exams**: Pre-paid by students, no impact on institution credits

## Notes
- Voice features use OpenAI TTS/STT via Emergent LLM Key
- Zoom integration requires institution credentials
- Gamification is toggle-able per institution
- All content can be marked for offline availability
