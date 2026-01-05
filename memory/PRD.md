# ProficientHub - PRD (Product Requirements Document)

## Overview
**Product Name:** ProficientHub  
**Version:** 1.0 MVP  
**Date:** January 2025  
**Status:** MVP Complete

## Original Problem Statement
Build a B2B/B2C SaaS platform for English proficiency exam preparation (TOEFL, IELTS, Cambridge, PTE, OET) with:
- Real-time exam simulators under exam conditions
- Premium instant AI feedback
- AI tutor agents for each exam
- Offline capabilities (planned)
- B2B focus with institutional dashboard
- Student risk metrics and pass probability
- ROI calculator for institutions
- Multi-language support (200 languages)
- Stripe payments
- Admin panel with API configuration

## User Personas

### 1. Institution Admin
- Language schools, universities, corporate training
- Needs: student management, analytics, risk metrics, ROI tracking
- Goals: improve pass rates, reduce no-show, scale teaching capacity

### 2. Individual Learner
- Self-study students preparing for proficiency exams
- Needs: practice tests, AI feedback, progress tracking
- Goals: pass target exam, improve specific skills

### 3. Student (Institution)
- Enrolled through institution
- Needs: guided practice, AI tutoring, exam simulation
- Goals: achieve required score for institution

### 4. Platform Admin
- System administrator
- Needs: API management, user management, analytics
- Goals: maintain platform, monitor usage

## Core Requirements (Static)

### Authentication & Authorization
- [x] JWT-based authentication
- [x] Role-based access (institution, individual, student, admin)
- [x] Secure password hashing (bcrypt)
- [x] Protected routes

### Landing Page (B2B Focus)
- [x] ROI Calculator with real-time results
- [x] Feature showcase
- [x] Exam types display
- [x] Pricing plans (institutional)
- [x] CTA sections

### Institution Dashboard
- [x] Student management (add, view)
- [x] Risk metrics (at-risk students, pass probability)
- [x] Performance analytics with charts
- [x] Exam distribution visualization

### Student Dashboard
- [x] Progress overview
- [x] Exam selection
- [x] Practice history
- [x] AI Tutor access

### Exam Simulator
- [x] All 5 exam types (TOEFL, IELTS, Cambridge, PTE, OET)
- [x] All sections (reading, listening, speaking, writing)
- [x] Timed practice sessions
- [x] Multiple question types
- [x] Score calculation

### AI Integration
- [x] AI Tutor chat for each exam type
- [x] AI-powered feedback on exam submissions
- [x] OpenAI integration via Emergent Universal Key

### Pricing & Payments
- [x] Institutional pricing plans (Starter, Professional, Enterprise)
- [x] Individual pricing plans (Single Exam, All Access)
- [x] Stripe integration ready

## What's Been Implemented (January 2025)

### Backend (FastAPI + MongoDB)
- Complete REST API with 25+ endpoints
- JWT authentication system
- User management (CRUD)
- Exam system with practice questions
- AI integration (OpenAI via Emergent)
- ROI calculator logic
- Stripe checkout preparation

### Frontend (React + Tailwind + Shadcn)
- Landing page with ROI Calculator
- Auth pages (login/register)
- Institution Dashboard with metrics
- Student Dashboard with progress
- AI Tutor chat interface
- Exam Simulator with timer
- i18n setup for multi-language

### Database Collections
- users (all user types)
- exam_attempts (practice history)
- tutor_conversations (AI chat logs)
- admin_settings

## Prioritized Backlog

### P0 - Critical (Next Phase)
1. Speaking test with voice recording/playback
2. Listening test with audio integration
3. Admin panel full implementation
4. Stripe payment flow completion

### P1 - High Priority
1. Offline mode with service workers
2. More practice questions per exam
3. Student invite via email
4. Institution branding/white-label

### P2 - Medium Priority
1. Real exam score conversion (band scores)
2. Learning path recommendations
3. Gamification (badges, leaderboards)
4. Mobile-responsive optimizations

### P3 - Nice to Have
1. Full 200 language translations
2. Video tutorials
3. Community features
4. API for third-party integrations

## Technical Architecture

```
Frontend (React 19)
├── /src
│   ├── /pages (Landing, Auth, Dashboards, Exam, Tutor)
│   ├── /components/ui (Shadcn components)
│   ├── /contexts (AuthContext)
│   └── /i18n (translations)

Backend (FastAPI)
├── server.py (main API)
├── MongoDB (users, exams, conversations)
└── External APIs (OpenAI, Stripe)
```

## Metrics for Success
- Student pass rate improvement: Target +20%
- Institution retention: Target 90%
- Daily active users: Track growth
- AI tutor engagement: Sessions per user
- Exam completion rate: Target 80%

## Next Tasks
1. Add audio playback for listening sections
2. Implement voice recording for speaking tests
3. Complete admin panel with API key management
4. Set up Stripe webhooks for subscription management
5. Add more practice questions from real exam formats
