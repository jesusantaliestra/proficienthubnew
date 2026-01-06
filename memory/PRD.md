# ProficientHub - PRD (Product Requirements Document)

## Overview
**Product Name:** ProficientHub  
**Version:** 1.2  
**Date:** January 2025  
**Status:** MVP Complete with B2B Features + Pricing + Stripe

## Original Problem Statement
Build a B2B/B2C SaaS platform for English proficiency exam preparation (TOEFL, IELTS, Cambridge, PTE, OET) with:
- Real-time exam simulators under exam conditions
- Premium instant AI feedback
- AI tutor agents for each exam (with voice)
- Offline capabilities
- B2B focus with institutional dashboard
- Student risk metrics and pass probability
- ROI calculator with realistic 10x AI multiplier
- Multi-language support (EN, ES, PT, DE, IT, FR)
- Stripe payments
- Admin panel with API configuration
- Library for institutions (materials, flashcards, audio, video, streaming)
- Pricing with 70-90% margins accounting for ElevenLabs + OpenAI costs
- **Writing & Speaking test packages for institutions to resell and monetize**

## User Personas

### 1. Institution Admin
- Language schools, universities, corporate training
- Needs: student management, analytics, risk metrics, ROI tracking, content library, test monetization
- Goals: 10x student capacity with same teachers, improve pass rates, reduce no-show, generate additional revenue

### 2. Individual Learner
- Self-study students preparing for proficiency exams
- Needs: practice tests, AI feedback, progress tracking
- Goals: pass target exam, improve specific skills

### 3. Student (Institution)
- Enrolled through institution
- Needs: guided practice, AI tutoring, exam simulation, access to institution library
- Goals: achieve required score for institution

### 4. Platform Admin
- System administrator
- Needs: API management, user management, analytics
- Goals: maintain platform, monitor usage

## Core Features Implemented

### Landing Page (B2B Focus)
- [x] Duolingo-style green design
- [x] B2B messaging in English
- [x] ROI Calculator with teacher salary input
- [x] Realistic 10x student capacity calculation
- [x] Feature showcase
- [x] Exam types display (TOEFL, IELTS, Cambridge, PTE, OET)

### Pricing Structure (Per-Student, Volume-Based)
- [x] **3-tier credit system**: Basic (50), Medium (100), Intensive (200)
- [x] **Volume discounts**: 1-10, 11-50, 51-100, 101-200, 201-500 students
- [x] **Exam multipliers**: 1 exam, 2 exams, All 5 exams
- [x] **Extra credits pricing**: Per-tier rates for additional credits
- [x] **Yearly discount**: 17% savings

### Writing & Speaking Test Packages (NEW)
- [x] **Writing packages**: 10, 50, 100, 250, 500, 1000 tests
- [x] **Speaking packages**: 10, 50, 100, 250, 500, 1000 tests
- [x] **Volume discounts**: Lower per-test price with higher volume
- [x] **Monetization calculator**: Shows profit potential for institutions
- [x] **Subscription recovery**: Shows how many tests to sell to recover subscription cost

### Stripe Payment Integration (NEW)
- [x] Checkout session creation for subscriptions
- [x] Checkout session creation for test packages
- [x] Payment status checking
- [x] Webhook handling
- [x] PaymentSuccess page with polling

### Institution Dashboard
- [x] Student management with risk metrics
- [x] Premium analytics (pass probability, risk score, engagement)
- [x] Library Section for content management
- [x] Language selector (EN, ES, PT, DE, IT, FR)
- [x] Exam management

### Library Features
- [x] Upload study materials
- [x] Create flashcard sets
- [x] Audio summaries (ready for ElevenLabs)
- [x] Video uploads and classes
- [x] Offline availability flag
- [x] Exam-type tagging

### Authentication & Authorization
- [x] JWT-based authentication
- [x] Role-based access (institution, individual, student, admin)
- [x] Language preference per user

### AI Integration
- [x] AI Tutor chat for each exam type
- [x] AI-powered feedback on exam submissions
- [x] OpenAI integration via Emergent Universal Key
- [ ] Voice-enabled AI agents (ElevenLabs - ready for integration)

## Technical Architecture

```
Frontend (React 19 + Duolingo-style)
├── /src
│   ├── /pages
│   │   ├── Landing.jsx (pricing, ROI calc, monetization calc)
│   │   ├── PaymentSuccess.jsx (Stripe success/failure)
│   │   ├── Auth.jsx
│   │   ├── InstitutionDashboard.jsx
│   │   ├── StudentDashboard.jsx
│   │   ├── ExamSimulator.jsx
│   │   └── AITutor.jsx
│   ├── /components/ui (Shadcn components)
│   ├── /contexts (AuthContext)
│   └── /i18n (EN, ES, PT, DE, IT, FR)

Backend (FastAPI)
├── server.py
│   ├── Auth endpoints
│   ├── Institution endpoints
│   ├── Library endpoints
│   ├── Exam endpoints
│   ├── AI Tutor endpoints
│   ├── Pricing endpoints (NEW: test packages, monetization)
│   ├── Stripe Checkout endpoints (NEW)
│   └── Admin endpoints
├── MongoDB (users, exams, library_items, conversations, payment_transactions)
└── External APIs (OpenAI, Stripe, ElevenLabs ready)
```

## API Endpoints

### Pricing (Updated)
- `GET /api/pricing/calculate` - Calculate per-student pricing
- `GET /api/pricing/tiers` - Get all pricing tiers
- `GET /api/pricing/credit-tiers` - Get credit tier options
- `GET /api/pricing/test-packages` - Get writing/speaking packages
- `POST /api/pricing/monetization-calculator` - Calculate profit potential
- `GET /api/pricing/institutional` - Get institutional pricing

### Stripe Checkout (NEW)
- `POST /api/checkout/subscription` - Create subscription checkout
- `POST /api/checkout/test-package` - Create test package checkout
- `GET /api/checkout/status/{session_id}` - Get payment status
- `POST /api/webhook/stripe` - Handle Stripe webhooks

## Database Collections
- users (all user types with language preference)
- exam_attempts (practice history)
- tutor_conversations (AI chat logs)
- library_items (materials, flashcards, audio, video)
- admin_settings
- payment_transactions (NEW - for Stripe payments)

## What's Been Implemented (January 2025)

### Session 1
- Basic MVP with dark theme
- Auth, dashboards, exam simulator, AI tutor

### Session 2
- Duolingo-style green design
- B2B focused messaging
- Realistic ROI calculator (10x multiplier)
- New pricing with exam count and student tiers
- Library section for institutions
- Multi-language support (6 languages)
- Flashcard creation
- Library item management

### Session 3 (Current)
- **3-tier credit system** (Basic/Medium/Intensive)
- **Writing & Speaking test packages** for institutions
- **Monetization calculator** showing profit potential
- **Stripe payment integration** via emergent library
- **PaymentSuccess page** with polling
- Comprehensive test suite for pricing features

## Prioritized Backlog

### P0 - Critical (Next Phase)
1. ElevenLabs integration for voice-enabled AI tutors
2. Audio recording/playback for speaking tests
3. Admin panel full implementation with API key management

### P1 - High Priority
1. Offline mode with service workers
2. More practice questions per exam (real exam-style)
3. Student invite via email
4. Institution branding/white-label for Enterprise
5. Video streaming and recording for classes

### P2 - Medium Priority
1. Real exam score conversion (band scores)
2. Learning path recommendations
3. Gamification (badges, leaderboards)
4. Mobile-responsive optimizations

### P3 - Nice to Have
1. Additional language translations
2. Video tutorials
3. Community features
4. API for third-party integrations

## Test Results (Session 3)
- Backend: 100% (18/18 tests passed)
- Frontend: 100% (all pricing features working)
- All core flows working

## Notes
- "Made with Emergent" badge is platform feature in preview, not in code
- Stripe integration uses emergent integration library (sk_test_emergent)
- AI costs factored into pricing model but hidden from clients
