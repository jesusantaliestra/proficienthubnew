# ProficientHub - PRD (Product Requirements Document)

## Overview
**Product Name:** ProficientHub  
**Version:** 3.0  
**Date:** January 27, 2026  
**Status:** Supreme CRM + React Native Base Complete

## Features Implemented (Session 7) - January 27, 2026

### 🆕 React Native Mobile App Base Structure
- **Project Scaffolding**: Complete Expo 50 project in `/app/mobile/`
- **White-Label Ready**: Configuration file `white-label.config.js` for institutional customization
- **Theme System**: Complete design tokens (colors, spacing, typography) in `src/theme/`
- **Core Components**: Button, Card, Input, Badge with theme support
- **Custom Hooks**: `useOffline` for offline functionality, `useVoice` for audio recording
- **EAS Build Configuration**: Ready for iOS/Android builds (`eas.json`)
- **TypeScript Support**: Full type safety with `tsconfig.json`

### ⚡ CRM Supreme - Advanced CRM Features
- **New Tab**: "CRM Supreme" with PRO badge in Institution Dashboard
- **Email Templates**: 
  - Create reusable email templates with HTML
  - Dynamic variables: `{{contact_name}}`, `{{institution_name}}`, `{{platform_name}}`
  - Categories: Welcome, Follow-up, Reminder, Promotion, Notification
  - Default templates auto-generated
- **Automation Rules**:
  - Trigger types: Lead Created, Stage Change, Inactivity, Score Threshold, Date-based
  - Multiple actions: Send Email, Create Task, Assign To, Slack Notification, Update Score
  - Enable/disable rules
  - Execution tracking
- **Tasks Management**:
  - Create tasks with priority levels
  - Due dates and lead association
  - Checkbox completion tracking
- **Advanced Reports**:
  - KPI Cards: Conversion Rate, Avg Deal Size, Response Time, Active Leads
  - Pipeline Health visualization with progress bars by stage

### 📁 New Files Created
- `/app/mobile/white-label.config.js` - White-label configuration
- `/app/mobile/src/theme/colors.ts` - Color system
- `/app/mobile/src/theme/spacing.ts` - Spacing and shadows
- `/app/mobile/src/theme/typography.ts` - Typography system
- `/app/mobile/src/theme/index.ts` - Theme exports
- `/app/mobile/src/components/Button.tsx` - Button component
- `/app/mobile/src/components/Card.tsx` - Card component
- `/app/mobile/src/components/Input.tsx` - Input component
- `/app/mobile/src/components/Badge.tsx` - Badge component
- `/app/mobile/src/components/index.ts` - Component exports
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
│   ├── server.py           # FastAPI app (1700+ lines)
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
│   │   │   ├── InstitutionDashboard.jsx
│   │   │   ├── StudentDashboard.jsx
│   │   │   ├── PaymentSuccess.jsx
│   │   │   └── Auth.jsx
│   │   ├── hooks/
│   │   │   └── useOffline.js        # Offline hook
│   │   ├── locales/
│   │   │   └── translations.json    # i18n translations
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx
│   │   ├── components/ui/           # Shadcn components
│   │   ├── i18n.js                  # i18next config
│   │   └── App.js
│   ├── public/
│   │   └── service-worker.js        # Offline support
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
- Landing: https://whitlabel-app.preview.emergentagent.com
- Login: https://whitlabel-app.preview.emergentagent.com/login
- Admin: https://whitlabel-app.preview.emergentagent.com/admin
- Student Portal: https://whitlabel-app.preview.emergentagent.com/student-portal
- White-Label Portal: https://whitlabel-app.preview.emergentagent.com/student-portal/demo-language-academy
- AI Tutor: https://whitlabel-app.preview.emergentagent.com/tutor/ielts
- Exam: https://whitlabel-app.preview.emergentagent.com/exam/ielts

## Remaining Backlog

### P0 - Next Priority
- [ ] UI for exam selection (dropdown to choose exam #1-20)
- [ ] Full Admin Panel functionality (Users, Revenue, API Keys management)

### P1 - High Priority
- [ ] Whitelabel Management UI (upload logo, set colors from dashboard)
- [ ] ElevenLabs integration (when API key provided)
- [ ] Student invite via email with provisional credentials
- [ ] Institutional media library with offline content

### P2 - Medium Priority
- [ ] Gamification (badges, points, leaderboards)
- [ ] Learning path recommendations
- [ ] Mobile-responsive optimizations
- [ ] Video streaming for classes

### P3 - Nice to Have
- [ ] Additional language translations (200 languages)
- [ ] Video tutorials
- [ ] Community features
- [ ] API for third-party integrations

## Notes
- Voice features use OpenAI TTS/STT via Emergent LLM Key
- Ready for ElevenLabs when API key is provided
- Service Worker provides basic offline support
- "Made with Emergent" badge is platform feature, not in code
