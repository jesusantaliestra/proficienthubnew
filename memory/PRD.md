# ProficientHub - PRD (Product Requirements Document)

## Overview
**Product Name:** ProficientHub  
**Version:** 9.3  
**Date:** January 29, 2026  
**Status:** Production Ready - Enterprise Suite + CRM Enhancements Complete

---

## 🧪 Session 14.2 - January 29, 2026

### CRM Education Enhancements (P2 - COMPLETE)
- **Drag-and-Drop Pipeline**: HTML5 native draggable with visual feedback
- **Lead Detail Modal**: Opens on card click with full lead information
- **Stage Change from Modal**: Click stage to move lead with toast notification
- **Education-Specific Analytics**: Conversion rates by exam type (IELTS, TOEFL, PTE, OET, Cambridge, CELPIP, TOEIC)
- **Demo Data Seeded**: 18 leads, 21 invoices, 6 subscriptions

### Testing Results (Iteration 14)
| Component | Backend Tests | Frontend Tests | Status |
|-----------|--------------|----------------|--------|
| CRM Education | 17 endpoints ✅ | All features ✅ | PASS |
| ERP Dashboard | 4 endpoints ✅ | Data display ✅ | PASS |

**Test Results**: 17/17 backend tests passed (100%), all frontend features verified

---

## 🧪 Session 14 - January 29, 2026

### Backend Refactoring Progress (P0 - IN PROGRESS)
- **Active Modular Routers**: 9 core routers + 7 Public API + 3 ERP + 2 Integrations = **21 total**
- **New routers added**: `ai_agents.py` (AI tutor endpoints), `library.py` (content management)
- **Remaining work**: Move remaining ~150 endpoints from `server.py` to modular routers

### Enterprise Testing Complete (P1 - VERIFIED)
| Component | Backend Tests | Frontend Tests | Status |
|-----------|--------------|----------------|--------|
| API Keys Manager | 3 endpoints ✅ | Page verified ✅ | PASS |
| Integrations Hub | 3 endpoints ✅ | Page verified ✅ | PASS |
| ERP Dashboard | 4 endpoints ✅ | Page verified ✅ | PASS |
| CRM Education | 5 endpoints ✅ | Page verified ✅ | PASS |

**Test Results**: 22/22 backend tests passed (100%), 4/4 frontend pages verified (100%)

---

## 🎨 NEW: Enterprise Frontend UI (Session 13.2) - January 29, 2026

### Frontend Pages Added:
| Page | Route | Features |
|------|-------|----------|
| **API Keys Manager** | `/institution/api-keys` | Create, view, revoke, rotate API keys with scopes |
| **Integrations Hub** | `/institution/integrations` | Connect 13 CRM/ERP systems, visual integration cards |
| **ERP Dashboard** | `/institution/erp` | MRR/ARR metrics, invoices, subscriptions, accounting tabs |
| **CRM Education** | `/institution/crm` | Visual pipeline, 11 stages, lead scoring, analytics |

### Navigation Added:
- New "Enterprise" section in institution sidebar
- Links to API Keys, Integrations, ERP, CRM

---

## 🚀 Enterprise Premium Features (Session 13) - January 29, 2026

### 📡 PUBLIC API v1 (COMPLETE)
Full REST API for third-party integrations with versioning, authentication, and webhooks.

**API Key Management** (`/api/api-keys`)
- Create, list, revoke, rotate API keys
- Scoped permissions: `read`, `write`, `admin`
- Rate limiting per key (requests/hour)
- Usage analytics and statistics

**Versioned Endpoints** (`/api/v1/`)
| Endpoint Group | Features |
|----------------|----------|
| `/v1/institutions` | CRUD, stats, filtering, pagination |
| `/v1/students` | Create, bulk import, credits management |
| `/v1/exams` | Attempts, stats, types, progress tracking |
| `/v1/analytics` | Overview, trends, at-risk, cohorts, benchmarks |
| `/v1/billing` | Invoices, payments, subscriptions, revenue |
| `/v1/webhooks` | Configure, test, delivery history, retry |

**Webhook Events**: 15+ events including `student.created`, `exam.completed`, `invoice.paid`, `subscription.renewed`, etc.

### 💼 ERP PREMIUM MODULE (COMPLETE)
Enterprise-grade financial management with multi-currency and global tax compliance.

**Multi-Currency Support**: 50+ currencies including USD, EUR, GBP, JPY, INR, BDT, NGN, PHP, AUD, etc.

**Global Tax Compliance**:
| Region | Countries | Tax Types |
|--------|-----------|-----------|
| Europe | 15 EU + UK + Norway | VAT, reverse charge |
| Americas | US (50 states) + LATAM | Sales Tax, IVA |
| Asia Pacific | India, Japan, Korea, SEA | GST, Consumption Tax |
| Africa | Nigeria, South Africa, Kenya | VAT |
| Middle East | UAE, Saudi, Israel, Turkey | VAT, KDV |

**Invoicing** (`/api/erp/invoices`)
- Create, send, track invoices
- Line items with tax calculation
- Payment recording and status tracking
- Recurring invoices
- Multi-currency with exchange rates

**Accounting** (`/api/erp/accounting`)
- Full Chart of Accounts (assets, liabilities, equity, revenue, expenses)
- Double-entry journal entries
- Financial Reports: Trial Balance, Income Statement, Balance Sheet, Cash Flow
- Budgeting with variance analysis

**Subscriptions** (`/api/erp/subscriptions`)
- Subscription plans management
- MRR/ARR tracking
- Churn analysis
- Cohort retention analysis

### 🔌 EXTERNAL INTEGRATIONS (COMPLETE)
Connect with 13 external CRM and ERP systems.

**Supported CRMs**:
- Salesforce, HubSpot, Zoho CRM, Pipedrive, Freshsales, Monday.com

**Supported ERPs**:
- SAP Business One, Microsoft Dynamics 365, Oracle NetSuite, Odoo, QuickBooks, Xero, Sage Intacct

**Features**:
- OAuth2/API Key authentication
- Connection verification
- Bidirectional sync
- Custom field mapping
- Webhook receivers for real-time sync

### 🎓 CRM EDUCATION (ENHANCED)
Education-specific CRM with specialized pipeline and scoring.

**11-Stage Education Pipeline**:
Lead → Qualified → Demo Scheduled → Demo Completed → Trial → Proposal → Negotiation → Onboarding → Active → Churned/Lost

**Education Scoring Factors**:
- Institution size (small to enterprise)
- Exam types interested
- Decision maker role
- Budget timeline
- Engagement activities

**Automation Rules**: Auto-create tasks, send emails, change stages, notify team

**Analytics**: Pipeline analysis, revenue forecasting, conversion rates

---

## Bug Fixes (Session 12) - January 28, 2026

### 🐛 Student Dashboard Stats Display Fix (COMPLETE)
- **Issue**: Student dashboard metrics were showing as blank
- **Root Cause**: CSS conflict - `metric-card` had white background with white text
- **Fix**: Changed to dark theme classes (`bg-slate-900/50 border-slate-800`)
- **File Modified**: `/app/frontend/src/pages/StudentDashboardRestricted.jsx`

### 📧 Configurable Email Service (NEW - COMPLETE)
- **4 Providers Supported**: SendGrid, Resend, SMTP, Mailgun
- **Email Templates**: Welcome, Exam Reminder, Progress Report, Critical Alert
- **Per-Institution Configuration**: Each institution uses their own provider
- **API Endpoints**:
  - `GET /api/email/providers` - Provider list
  - `GET/POST /api/email/config` - Email configuration
  - `GET /api/email/templates` - Get/save templates
  - `POST /api/email/send` - Send email
  - `POST /api/email/test` - Test configuration

### 📱 Mobile App Ready for Deploy (NEW - COMPLETE)
- **Capacitor v6** configured for iOS and Android
- **Services Created**:
  - `whiteLabelService.js` - Dynamic branding per institution
  - `pushNotificationService.js` - Native push notifications
  - `offlineContentService.js` - Download exams for offline use
- **PWA Support**: manifest.json and service-worker.js
- **Build Documentation**: `/app/frontend/MOBILE_BUILD.md`

### 🔧 Backend Routers (10 Created, 7 Active)
| Router | Status | Description |
|--------|--------|-------------|
| superadmin.py | ✅ Active | Platform stats, institutions management |
| zoom.py | ✅ Active | Zoom meeting integration |
| alerts.py | ✅ Active | Real-time platform alerts |
| messaging.py | ✅ Active | SMS/WhatsApp multi-provider |
| pricing.py | ✅ Active | Dynamic pricing configuration |
| analytics.py | ✅ Active | Predictive analytics |
| email.py | ✅ Active | Configurable email service |
| auth.py | 🔲 Ready | Authentication (prepared) |
| exams.py | 🔲 Ready | Exam management (prepared) |
| institution.py | 🔲 Ready | Institution settings (prepared) |

## Features Implemented (Session 11 - Part 2) - January 28, 2026

### 🚨 Alert System for Superadmin (COMPLETE)
- **Real-time Platform Alerts** at `/superadmin`
  - Badge notification on Alertas button showing alert count
  - Critical alerts banner when urgent issues exist
  - Slide-out alerts panel
- **Alert Types**:
  - 🔴 **Créditos Bajos** (critical/warning) - Institution <20% credits remaining
  - ⚠️ **Institución Inactiva** (warning) - No activity in 7+ days
  - 🎉 **Nuevo Milestone** (success) - Institution reaches 50/100/250/500/1000 students
  - 💰 **Compra Significativa** (info) - Large credit purchase (500+)
  - 📉 **Alta Tasa de Errores** (warning) - >30% exam failures
- **API Endpoints**:
  - `GET /api/superadmin/alerts` - Get all alerts with filters
  - `GET /api/superadmin/alerts/summary` - Quick counts for badge
  - `POST /api/superadmin/alerts/{id}/dismiss` - Dismiss alert
  - `DELETE /api/superadmin/alerts/dismissed` - Clear dismissed

### 🔧 Backend Modularization Progress
- **New Modular Routers Created**:
  - `routers/alerts.py` - Alert system
  - `routers/messaging.py` - SMS/WhatsApp multi-provider
  - `routers/auth.py` - Authentication (prepared)
- **Total Routers**: 5 modular routers now active

## Features Implemented (Session 11 - Part 1) - January 28, 2026

### 🛡️ Superadmin Dashboard (NEW - P0 COMPLETE)
- **Platform Overview Page** at `/superadmin`
  - Total Institutions, Students, Individual Users
  - Active Users (7d and 30d)
  - Total Exams Taken
- **AI & Revenue Metrics**:
  - Total AI Interactions
  - Credits Purchased/Used
  - Estimated Revenue ($0.10/credit)
  - Platform Engagement Rate
- **Business Metrics**:
  - Avg Credits per Institution
  - Student to Institution Ratio
- **Institutions Management**:
  - List all institutions with search
  - View student count, AI credits, activity
  - Grant AI credits modal
  - View detailed institution info
- **Activity Log**: Recent exams, AI interactions, registrations
- **Exam Distribution Chart**: Visual breakdown by exam type
- **API Endpoints**:
  - `GET /api/superadmin/stats` - Full platform statistics
  - `GET /api/superadmin/institutions` - List with enriched data
  - `GET /api/superadmin/institutions/{id}` - Detailed info
  - `GET /api/superadmin/activity-log` - Recent activities
  - `GET /api/superadmin/revenue-report` - Revenue by period
  - `POST /api/superadmin/grant-credits` - Grant credits

### 🔧 Backend Refactoring Started
- Created `/app/backend/routers/` directory for modular routers
- Created `/app/backend/utils/` directory for utilities
- **Modular Files Created**:
  - `database.py` - MongoDB connection management
  - `utils/auth.py` - Authentication utilities
  - `routers/superadmin.py` - Superadmin endpoints
  - `routers/zoom.py` - Full Zoom integration router

### 📹 Zoom Integration Router (P0 COMPLETE)
- Full Zoom API integration in modular router
- **Endpoints**:
  - `POST /api/zoom/meetings/create` - Create meeting
  - `GET /api/zoom/meetings` - List meetings
  - `GET /api/zoom/meetings/{id}` - Get meeting details
  - `PUT /api/zoom/meetings/{id}` - Update meeting
  - `DELETE /api/zoom/meetings/{id}` - Delete meeting
  - `GET /api/zoom/meetings/{id}/signature` - SDK signature
  - `POST /api/zoom/test-connection` - Test credentials

### 📱 SMS/WhatsApp Global Providers (P0 COMPLETE)
- **16 Providers Supported**:
  - Global: Twilio, MessageBird, Vonage, Infobip, Sinch
  - US/Canada: Plivo, Bandwidth
  - UK/Europe: ClickSend, Esendex, Textlocal
  - India/Asia: MSG91, Gupshup, Kaleyra
  - Africa: Africa's Talking, Termii
  - Australia/NZ: Burst SMS
- **SDK Packages Installed**: twilio, vonage

### 🐛 Bug Fixes
- Fixed SMS/WhatsApp toggle switch in Institution Settings (added data-testid)
- Fixed MongoDB projection bug in get_institution_details endpoint

## Features Implemented (Session 10) - January 27, 2026

### 📱 React Native Mobile App Screens (NEW - P1 COMPLETE)
- **AITutorScreen.tsx**: Full multi-agent AI tutor for mobile
  - Agent selection with credits display
  - Message history with voice support
  - Quick actions per agent type
- **LiveClassesScreen.tsx**: Upcoming/past classes with Zoom join
  - Live indicator for ongoing classes
  - Refresh and pull-to-refresh support
- **ExamStartScreen.tsx**: Exam section selector
  - Full exam or individual section practice
  - Duration and question count display
  - Tips card for exam preparation
- **Updated MainTabs.tsx**: New navigation with AI Tutor and Classes tabs

### 📱 WhatsApp & SMS Configuration (NEW - P1 COMPLETE)
- **Provider Selection**: Twilio, MessageBird, Vonage
- **Configuration Options**:
  - Account SID / API Key
  - API Secret
  - SMS From Number
  - WhatsApp Number
  - Enable SMS / Enable WhatsApp toggles
- **Test Message**: Send test SMS or WhatsApp
- **Bulk Messaging**: Queue messages to multiple students
- **API Endpoints**:
  - `GET/POST /api/institution/messaging/config`
  - `POST /api/institution/messaging/test` (MOCKED)
  - `POST /api/institution/messaging/send-bulk` (MOCKED)

### 📧 White-Label Email Templates (NEW - P1 COMPLETE)
- **Default Templates**:
  - Welcome email with login credentials
  - Exam reminder with date
  - Progress report with weekly stats
- **Custom Templates**: Save and edit templates per institution
- **Placeholder System**: {student_name}, {institution_name}, {exam_type}, etc.
- **Live Preview**: Preview templates with sample data
- **API Endpoints**:
  - `GET /api/institution/email-templates`
  - `POST /api/institution/email-templates`
  - `POST /api/institution/email-templates/preview`

### 📊 Automatic Reports System (NEW - P1 COMPLETE)
- **Report Types**: Weekly and Monthly
- **Report Contents**:
  - AI Usage Stats (credits, agent usage)
  - Exam Statistics (attempts, scores)
  - Student Engagement (active students, activity rate)
  - Gamification (XP, levels, streaks)
- **Configuration**:
  - Delivery day selection (Monday-Sunday)
  - Content toggles
  - Recipient selection (Admins, Students)
- **On-Demand Generation**: Generate reports instantly
- **Highlights**: Auto-generated insights based on data
- **API Endpoints**:
  - `GET/POST /api/institution/reports/config`
  - `GET /api/institution/reports/generate?report_type=weekly|monthly`
  - `GET /api/institution/reports/history`

### 🔧 Institution Settings - 7 Tabs
1. **AI** - Multi-agent configuration, credits
2. **Avatar** - Animated/Premium avatar selection
3. **Zoom** - Video class integration
4. **Email** - SMTP configuration
5. **SMS** - WhatsApp/SMS providers
6. **Reports** - Automatic report settings
7. **XP** - Gamification settings

### 📁 New Files Created (Session 10)
- `/app/mobile/src/screens/AITutorScreen.tsx`
- `/app/mobile/src/screens/LiveClassesScreen.tsx`
- `/app/mobile/src/screens/ExamStartScreen.tsx`
- `/app/mobile/src/navigation/MainTabs.tsx` (updated)
- `/app/frontend/src/components/InstitutionSettings.jsx` (updated with MessagingConfigSection, ReportsConfigSection)

## Features Implemented (Session 9) - January 27, 2026

### 🤖 Multi-Agent AI Tutor System (P0 COMPLETE)
- **Three Specialized AI Agents**:
  - **🎓 Official Tutor**: Expert exam preparation with strategies, practice questions, detailed feedback (1 credit/message)
  - **🏆 Mock Coach**: Practice mode with 5 attempts per question, progressive hints system (2 credits/message)
  - **📋 Study Planner**: Personalized study schedules based on exam date and available time (1 credit/message)

- **Credit-Based System**:
  - Institutions start with 100 free credits
  - Individual users start with 10 free credits
  - Purchase tiers: 100/$10, 500/$40 (20% OFF), 1000/$70 (30% OFF), 5000/$300 (40% OFF)
  - Credits shared across all students and agents
  - Real-time balance tracking with usage history

- **Mock Coach Special Features**:
  - 5 attempts per question before revealing answer
  - Progressive hints after each wrong attempt
  - Gamified practice experience

- **Voice Support**:
  - Official Tutor and Mock Coach support voice responses
  - Integrates with OpenAI TTS (fallback from ElevenLabs)
  - Voice selection: Nova, Echo, Alloy, Fable

- **Institution Configuration**:
  - Enable/disable specific agents per institution
  - Custom voice settings per agent
  - AI Agents tab in Institution Settings

### 📁 New Files Created (Session 9)
- `/app/frontend/src/pages/AITutorMultiAgent.jsx` - Multi-agent tutor interface with sidebar, credits display
- `/app/frontend/src/components/InstitutionSettings.jsx` - Updated with AI Agents configuration tab

### 🔌 New API Endpoints (Session 9)
- `GET /api/ai-agents/available` - List available agents
- `GET /api/ai-agents/credits` - Get credit balance
- `POST /api/ai-agents/credits/purchase` - Purchase credits
- `GET /api/ai-agents/config` - Get agent configuration
- `POST /api/ai-agents/config` - Update agent configuration
- `POST /api/ai-agents/interact` - Interact with any agent
- `GET /api/ai-agents/sessions` - Get chat session history
- `GET /api/ai-agents/history/{session_id}` - Get conversation history
- `POST /api/ai-agents/mock-coach/start-question` - Start practice question
- `POST /api/ai-agents/mock-coach/check-answer` - Check answer with hints

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
- Landing: https://smartlearn-portal-1.preview.emergentagent.com
- Login: https://smartlearn-portal-1.preview.emergentagent.com/login
- Admin: https://smartlearn-portal-1.preview.emergentagent.com/admin
- **Superadmin**: https://smartlearn-portal-1.preview.emergentagent.com/superadmin
- Student Portal: https://smartlearn-portal-1.preview.emergentagent.com/student-portal
- White-Label Portal: https://smartlearn-portal-1.preview.emergentagent.com/student-portal/demo-language-academy
- AI Tutor: https://smartlearn-portal-1.preview.emergentagent.com/tutor/ielts
- Exam: https://smartlearn-portal-1.preview.emergentagent.com/exam/ielts

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
- [x] **Multi-Agent AI Tutor System** (3 agents, credit system, Mock Coach with hints)
- [x] **Superadmin Dashboard** - Platform stats, all institutions, grant credits, revenue metrics, exam distribution
- [x] **Full Zoom Integration Router** - Create, list, update, delete meetings + SDK signatures
- [x] **Global SMS/WhatsApp Providers** - 16 providers for global coverage

### P1 - Completed ✅
- [x] Complete React Native app screens (AITutor, LiveClasses, ExamStart)
- [x] WhatsApp/SMS provider configuration per institution (16 global providers)
- [x] White-Label Email Templates System (welcome, reminder, progress report)
- [x] Automatic Reports System (weekly/monthly with AI usage, exam stats, engagement)

### P2 - Medium Priority (In Progress)
- [x] **Backend Refactoring** - Created modular routers (7 routers prepared, 5 active)
- [ ] **Capacitor Mobile App** - Convert React to native app with white-label dinámico
- [ ] Video streaming with Zoom embedded in platform
- [ ] ElevenLabs voice integration for AI Tutor (currently using OpenAI TTS)
- [x] **Push Notifications System** - Expo Push for mobile, backend endpoints, institution panel

### P3 - Completed ✅
- [x] **AI-generated flashcard definitions** - Generate definitions from words or extract from text
- [x] **Offline content access** - Manifest, download, sync progress endpoints
- [x] **Superadmin dashboard** - Platform stats, all institutions, grant credits
- [x] **Alert System** - Real-time platform monitoring with 5 alert types

### Future Backlog
- [ ] **Capacitor App** - Native app with dynamic white-label
- [ ] Offline Content Access (Mobile) - Download and display materials offline
- [ ] Full White-Label Customization - All student-facing areas
- [ ] Custom Voice IDs for ElevenLabs - Institution-level voice config
- [ ] Replace Mocked Predictive Analytics - Real database aggregations
- [ ] Email notifications for critical alerts

## 📱 Mobile App Strategy (NEW)

### Arquitectura: Una App con White-Label Dinámico
```
📱 App "ProficientHub" (única en App Store / Play Store)
                    ↓
          Usuario hace LOGIN
                    ↓
    Backend identifica institution_id
                    ↓
    App carga branding dinámico:
    - Logo de la institución
    - Colores personalizados
    - Contenido específico
    - Clases Zoom propias
```

### Tecnología Elegida: **Capacitor**
- ✅ Reutiliza código React existente
- ✅ Una sola app = mantenimiento simple
- ✅ Push notifications nativas
- ✅ Acceso offline completo
- ✅ White-label sin republicar

### Modelo de Pricing - App Móvil

| Tier | Descripción | Precio |
|------|-------------|--------|
| **Standard** | White-label en app compartida "ProficientHub" | Incluido |
| **Premium** | App dedicada en stores con nombre/logo propio | $2,000 setup + $200/mes |
| **Enterprise** | App dedicada + backend dedicado + SLA | $5,000 setup + $500/mes |

**Upsell Premium App**:
- Nombre propio en App Store / Play Store
- Ícono personalizado
- Splash screen con marca
- URL de descarga propia
- Certificados y keys propios
- Build automatizado con cada release

## Exam Types (Updated)
- TOEFL
- **IELTS Academic** - For university admissions and professional registration
- **IELTS General** - For migration and work experience
- Cambridge (FCE, CAE, CPE)
- Trinity (GESE, ISE)
- TOEIC
- CELPIP
- **PTE Academic** - For study abroad and immigration
- **PTE Core** - For Canadian immigration and citizenship
- OET

## Business Model Notes
- **AI Credits**: Institutions buy credits, students consume them per interaction
- **Premium Avatar**: Included in institutional plan, institutions set credit limits
- **Free Minutes for Students**: Institutions can offer X free minutes of premium AI tutor to students for conversion
- **Placement Test**: Configurable per institution (mandatory/optional/free)
- **Mock Exams**: Pre-paid by students, no impact on institution credits

## Notes
- Voice features use OpenAI TTS/STT via Emergent LLM Key
- AI Tutor uses GPT-5.2 via Emergent LLM Key
- Zoom integration requires institution credentials
- Gamification is toggle-able per institution
- All content can be marked for offline availability
