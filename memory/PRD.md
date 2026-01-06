# ProficientHub - PRD (Product Requirements Document)

## Overview
**Product Name:** ProficientHub  
**Version:** 2.0  
**Date:** January 2025  
**Status:** MVP Complete with Full Features

## Original Problem Statement
Build a B2B/B2C SaaS platform for English proficiency exam preparation (TOEFL, IELTS, Cambridge, PTE, OET) with:
- Real-time exam simulators under exam conditions
- Premium instant AI feedback
- AI tutor agents with voice
- Offline capabilities
- B2B focus with institutional dashboard
- Multi-language support

## Features Implemented (Session 4)

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

## Test Results (Session 4)
- **Backend**: 100% (20/20 tests passed)
- **Frontend**: 100% (all features working)
- **Test File**: `/app/tests/test_exam_features.py`

## Credentials
- **Admin**: santaliestralimited@gmail.com / Admin123!

## URLs
- Landing: https://proficiencypal.preview.emergentagent.com
- Login: https://proficiencypal.preview.emergentagent.com/login
- Admin: https://proficiencypal.preview.emergentagent.com/admin
- AI Tutor: https://proficiencypal.preview.emergentagent.com/tutor/ielts
- Exam: https://proficiencypal.preview.emergentagent.com/exam/ielts

## Remaining Backlog

### P1 - High Priority
- [ ] ElevenLabs integration (when API key provided)
- [ ] More exam questions per section
- [ ] Student invite via email
- [ ] Video streaming for classes

### P2 - Medium Priority
- [ ] Real exam score conversion
- [ ] Learning path recommendations
- [ ] Gamification (badges, leaderboards)
- [ ] Mobile-responsive optimizations

### P3 - Nice to Have
- [ ] Additional language translations
- [ ] Video tutorials
- [ ] Community features
- [ ] API for third-party integrations

## Notes
- Voice features use OpenAI TTS/STT via Emergent LLM Key
- Ready for ElevenLabs when API key is provided
- Service Worker provides basic offline support
- "Made with Emergent" badge is platform feature, not in code
