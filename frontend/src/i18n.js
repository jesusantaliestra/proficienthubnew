import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  en: {
    translation: {
      nav: {
        features: 'Features',
        exams: 'Exams',
        pricing: 'Pricing',
        login: 'Log In',
        getStarted: 'Get Started',
        dashboard: 'Dashboard'
      },
      hero: {
        title: 'Master English Proficiency',
        titleHighlight: 'With AI-Powered Learning',
        subtitle: 'Prepare for TOEFL, IELTS, Cambridge, PTE, and OET exams with real-time simulations, instant AI feedback, and expert tutoring.',
        cta: 'Start Free Trial',
        ctaSecondary: 'Book a Demo',
        statsStudents: 'Students Trained',
        statsInstitutions: 'Partner Institutions',
        statsPassRate: 'Pass Rate Improvement'
      },
      calculator: {
        title: 'ROI Calculator',
        subtitle: 'See how ProficientHub can transform your institution',
        students: 'Current Students',
        teachers: 'Number of Teachers',
        passRate: 'Current Pass Rate',
        noShowRate: 'No-Show Rate',
        calculate: 'Calculate ROI',
        results: {
          additionalStudents: 'Additional Students You Can Teach',
          improvedPassRate: 'Projected Pass Rate',
          reducedNoShow: 'Reduced No-Show Rate',
          revenueIncrease: 'Estimated Revenue Increase',
          timeSaved: 'Teacher Hours Saved/Week'
        }
      },
      features: {
        title: 'Why Institutions Choose Us',
        subtitle: 'Premium features designed for scale and results',
        ai: {
          title: 'AI-Powered Tutoring',
          description: 'Personalized learning paths with instant feedback powered by advanced AI'
        },
        exams: {
          title: 'All Major Exams',
          description: 'TOEFL, IELTS, Cambridge, PTE, and OET - all in one platform'
        },
        analytics: {
          title: 'Premium Analytics',
          description: 'Risk prediction, pass probability, and engagement metrics'
        },
        speaking: {
          title: 'Speaking Tests',
          description: 'AI-powered speaking evaluation with real-time feedback'
        }
      },
      pricing: {
        title: 'Simple, Transparent Pricing',
        subtitle: 'Choose the plan that fits your institution',
        monthly: 'Monthly',
        yearly: 'Yearly',
        perMonth: '/month',
        perYear: '/year',
        getStarted: 'Get Started',
        contactSales: 'Contact Sales',
        popular: 'Most Popular'
      },
      footer: {
        description: 'The leading AI-powered platform for English proficiency exam preparation.',
        product: 'Product',
        company: 'Company',
        legal: 'Legal',
        copyright: '© 2024 ProficientHub. All rights reserved.'
      },
      dashboard: {
        overview: 'Overview',
        students: 'Students',
        exams: 'Exams',
        analytics: 'Analytics',
        settings: 'Settings',
        aiTutor: 'AI Tutor',
        totalStudents: 'Total Students',
        avgPassRate: 'Avg Pass Probability',
        atRisk: 'At Risk Students',
        examsCompleted: 'Exams Completed'
      },
      exams: {
        toefl: 'TOEFL',
        ielts: 'IELTS',
        cambridge: 'Cambridge',
        pte: 'PTE',
        oet: 'OET',
        startPractice: 'Start Practice',
        viewProgress: 'View Progress'
      }
    }
  },
  es: {
    translation: {
      nav: {
        features: 'Características',
        exams: 'Exámenes',
        pricing: 'Precios',
        login: 'Iniciar Sesión',
        getStarted: 'Comenzar',
        dashboard: 'Panel'
      },
      hero: {
        title: 'Domina el Inglés',
        titleHighlight: 'Con Aprendizaje IA',
        subtitle: 'Prepárate para TOEFL, IELTS, Cambridge, PTE y OET con simulaciones en tiempo real y tutoría experta.',
        cta: 'Prueba Gratis',
        ctaSecondary: 'Reservar Demo',
        statsStudents: 'Estudiantes',
        statsInstitutions: 'Instituciones',
        statsPassRate: 'Mejora Tasa Aprobación'
      }
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
