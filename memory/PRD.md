# ProficientHub - PRD (Product Requirements Document)

## Overview
**Product Name:** ProficientHub  
**Version:** 1.1  
**Date:** January 2025  
**Status:** MVP Complete with B2B Features

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

## User Personas

### 1. Institution Admin
- Language schools, universities, corporate training
- Needs: student management, analytics, risk metrics, ROI tracking, content library
- Goals: 10x student capacity with same teachers, improve pass rates, reduce no-show

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
- [x] Pricing with exam selector and student tiers

### Pricing Structure (85-95% Margins)
Tiers by student count (accounting for ElevenLabs + OpenAI costs):
- **Starter** (1-10 students): $149/mo (1 exam), $238/mo (2 exams), $328/mo (3+)
- **Growth** (11-50 students): $349/mo (1 exam), $558/mo (2 exams), $768/mo (3+)
- **Professional** (51-100 students): $699/mo (1 exam), $1,118/mo (2 exams), $1,538/mo (3+)
- **Enterprise** (101-200 students): $1,299/mo + $8/extra student

### Institution Dashboard
- [x] Student management with risk metrics
- [x] Premium analytics (pass probability, risk score, engagement)
- [x] **Library Section** for content management
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

### ROI Calculator Metrics
- 10x student capacity with AI (100:1 vs 15:1 ratio)
- +20% pass rate improvement
- 60% no-show reduction
- Teacher time saved: 30h/week per teacher
- Revenue + cost savings calculation

## Technical Architecture

```
Frontend (React 19 + Duolingo-style)
├── /src
│   ├── /pages (Landing, Auth, Dashboards, Exam, Tutor)
│   ├── /components/ui (Shadcn components)
│   ├── /contexts (AuthContext)
│   └── /i18n (EN, ES, PT, DE, IT, FR)

Backend (FastAPI)
├── server.py (main API)
│   ├── Auth endpoints
│   ├── Institution endpoints
│   ├── Library endpoints
│   ├── Exam endpoints
│   ├── AI Tutor endpoints
│   ├── Pricing endpoints
│   └── Admin endpoints
├── MongoDB (users, exams, library_items, conversations)
└── External APIs (OpenAI, Stripe, ElevenLabs ready)
```

## Database Collections
- users (all user types with language preference)
- exam_attempts (practice history)
- tutor_conversations (AI chat logs)
- library_items (materials, flashcards, audio, video)
- admin_settings

## What's Been Implemented (January 2025)

### Iteration 1
- Basic MVP with dark theme
- Auth, dashboards, exam simulator, AI tutor

### Iteration 2
- Duolingo-style green design
- B2B focused messaging
- Realistic ROI calculator (10x multiplier)
- New pricing with exam count and student tiers
- Library section for institutions
- Multi-language support (6 languages)
- Flashcard creation
- Library item management

## Prioritized Backlog

### P0 - Critical (Next Phase)
1. ElevenLabs integration for voice-enabled AI tutors
2. Audio recording/playback for speaking tests
3. Video streaming and recording for classes
4. Stripe webhook integration for live payments
5. Admin panel full implementation with API key management

### P1 - High Priority
1. Offline mode with service workers
2. More practice questions per exam (real exam-style)
3. Student invite via email
4. Institution branding/white-label for Enterprise

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

## Test Results
- Backend: 88.7% tests passing
- Frontend: 98% tests passing
- All core flows working

## Next Tasks
1. Integrate ElevenLabs for voice AI agents
2. Add audio recording component for speaking tests
3. Implement video streaming (WebRTC or pre-recorded)
4. Complete Stripe webhook handling
5. Build admin panel with API key configuration
