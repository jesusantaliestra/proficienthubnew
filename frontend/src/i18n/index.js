import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Top 80 most spoken languages
export const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English', native: 'English', flag: '🇺🇸' },
  { code: 'es', name: 'Spanish', native: 'Español', flag: '🇪🇸' },
  { code: 'zh', name: 'Chinese', native: '中文', flag: '🇨🇳' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी', flag: '🇮🇳' },
  { code: 'ar', name: 'Arabic', native: 'العربية', flag: '🇸🇦' },
  { code: 'pt', name: 'Portuguese', native: 'Português', flag: '🇧🇷' },
  { code: 'bn', name: 'Bengali', native: 'বাংলা', flag: '🇧🇩' },
  { code: 'ru', name: 'Russian', native: 'Русский', flag: '🇷🇺' },
  { code: 'ja', name: 'Japanese', native: '日本語', flag: '🇯🇵' },
  { code: 'pa', name: 'Punjabi', native: 'ਪੰਜਾਬੀ', flag: '🇮🇳' },
  { code: 'de', name: 'German', native: 'Deutsch', flag: '🇩🇪' },
  { code: 'jv', name: 'Javanese', native: 'Basa Jawa', flag: '🇮🇩' },
  { code: 'ko', name: 'Korean', native: '한국어', flag: '🇰🇷' },
  { code: 'fr', name: 'French', native: 'Français', flag: '🇫🇷' },
  { code: 'te', name: 'Telugu', native: 'తెలుగు', flag: '🇮🇳' },
  { code: 'vi', name: 'Vietnamese', native: 'Tiếng Việt', flag: '🇻🇳' },
  { code: 'mr', name: 'Marathi', native: 'मराठी', flag: '🇮🇳' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்', flag: '🇮🇳' },
  { code: 'tr', name: 'Turkish', native: 'Türkçe', flag: '🇹🇷' },
  { code: 'ur', name: 'Urdu', native: 'اردو', flag: '🇵🇰' },
  { code: 'it', name: 'Italian', native: 'Italiano', flag: '🇮🇹' },
  { code: 'th', name: 'Thai', native: 'ไทย', flag: '🇹🇭' },
  { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી', flag: '🇮🇳' },
  { code: 'pl', name: 'Polish', native: 'Polski', flag: '🇵🇱' },
  { code: 'uk', name: 'Ukrainian', native: 'Українська', flag: '🇺🇦' },
  { code: 'ml', name: 'Malayalam', native: 'മലയാളം', flag: '🇮🇳' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ', flag: '🇮🇳' },
  { code: 'or', name: 'Odia', native: 'ଓଡ଼ିଆ', flag: '🇮🇳' },
  { code: 'my', name: 'Burmese', native: 'မြန်မာ', flag: '🇲🇲' },
  { code: 'fa', name: 'Persian', native: 'فارسی', flag: '🇮🇷' },
  { code: 'ro', name: 'Romanian', native: 'Română', flag: '🇷🇴' },
  { code: 'nl', name: 'Dutch', native: 'Nederlands', flag: '🇳🇱' },
  { code: 'hu', name: 'Hungarian', native: 'Magyar', flag: '🇭🇺' },
  { code: 'el', name: 'Greek', native: 'Ελληνικά', flag: '🇬🇷' },
  { code: 'cs', name: 'Czech', native: 'Čeština', flag: '🇨🇿' },
  { code: 'sv', name: 'Swedish', native: 'Svenska', flag: '🇸🇪' },
  { code: 'he', name: 'Hebrew', native: 'עברית', flag: '🇮🇱' },
  { code: 'id', name: 'Indonesian', native: 'Bahasa Indonesia', flag: '🇮🇩' },
  { code: 'ms', name: 'Malay', native: 'Bahasa Melayu', flag: '🇲🇾' },
  { code: 'fi', name: 'Finnish', native: 'Suomi', flag: '🇫🇮' },
  { code: 'da', name: 'Danish', native: 'Dansk', flag: '🇩🇰' },
  { code: 'no', name: 'Norwegian', native: 'Norsk', flag: '🇳🇴' },
  { code: 'sk', name: 'Slovak', native: 'Slovenčina', flag: '🇸🇰' },
  { code: 'bg', name: 'Bulgarian', native: 'Български', flag: '🇧🇬' },
  { code: 'sr', name: 'Serbian', native: 'Српски', flag: '🇷🇸' },
  { code: 'hr', name: 'Croatian', native: 'Hrvatski', flag: '🇭🇷' },
  { code: 'lt', name: 'Lithuanian', native: 'Lietuvių', flag: '🇱🇹' },
  { code: 'lv', name: 'Latvian', native: 'Latviešu', flag: '🇱🇻' },
  { code: 'et', name: 'Estonian', native: 'Eesti', flag: '🇪🇪' },
  { code: 'sl', name: 'Slovenian', native: 'Slovenščina', flag: '🇸🇮' },
  { code: 'fil', name: 'Filipino', native: 'Filipino', flag: '🇵🇭' },
  { code: 'sw', name: 'Swahili', native: 'Kiswahili', flag: '🇰🇪' },
  { code: 'am', name: 'Amharic', native: 'አማርኛ', flag: '🇪🇹' },
  { code: 'ne', name: 'Nepali', native: 'नेपाली', flag: '🇳🇵' },
  { code: 'si', name: 'Sinhala', native: 'සිංහල', flag: '🇱🇰' },
  { code: 'km', name: 'Khmer', native: 'ខ្មែរ', flag: '🇰🇭' },
  { code: 'zu', name: 'Zulu', native: 'isiZulu', flag: '🇿🇦' },
  { code: 'xh', name: 'Xhosa', native: 'isiXhosa', flag: '🇿🇦' },
  { code: 'af', name: 'Afrikaans', native: 'Afrikaans', flag: '🇿🇦' },
  { code: 'ca', name: 'Catalan', native: 'Català', flag: '🇪🇸' },
  { code: 'eu', name: 'Basque', native: 'Euskara', flag: '🇪🇸' },
  { code: 'gl', name: 'Galician', native: 'Galego', flag: '🇪🇸' },
  { code: 'is', name: 'Icelandic', native: 'Íslenska', flag: '🇮🇸' },
  { code: 'ga', name: 'Irish', native: 'Gaeilge', flag: '🇮🇪' },
  { code: 'cy', name: 'Welsh', native: 'Cymraeg', flag: '🏴󠁧󠁢󠁷󠁬󠁳󠁿' },
  { code: 'mt', name: 'Maltese', native: 'Malti', flag: '🇲🇹' },
  { code: 'lb', name: 'Luxembourgish', native: 'Lëtzebuergesch', flag: '🇱🇺' },
  { code: 'sq', name: 'Albanian', native: 'Shqip', flag: '🇦🇱' },
  { code: 'mk', name: 'Macedonian', native: 'Македонски', flag: '🇲🇰' },
  { code: 'bs', name: 'Bosnian', native: 'Bosanski', flag: '🇧🇦' },
  { code: 'az', name: 'Azerbaijani', native: 'Azərbaycan', flag: '🇦🇿' },
  { code: 'ka', name: 'Georgian', native: 'ქართული', flag: '🇬🇪' },
  { code: 'hy', name: 'Armenian', native: 'Հայերdelays', flag: '🇦🇲' },
  { code: 'kk', name: 'Kazakh', native: 'Қазақша', flag: '🇰🇿' },
  { code: 'uz', name: 'Uzbek', native: "O'zbek", flag: '🇺🇿' },
  { code: 'mn', name: 'Mongolian', native: 'Монгол', flag: '🇲🇳' },
  { code: 'lo', name: 'Lao', native: 'ລາວ', flag: '🇱🇦' },
  { code: 'ps', name: 'Pashto', native: 'پښتو', flag: '🇦🇫' },
  { code: 'tg', name: 'Tajik', native: 'Тоҷикӣ', flag: '🇹🇯' }
];

// Translation resources - Core strings
const resources = {
  en: {
    translation: {
      // Navigation
      nav: {
        home: 'Home',
        features: 'Features',
        pricing: 'Pricing',
        about: 'About',
        login: 'Sign In',
        register: 'Get Started',
        dashboard: 'Dashboard',
        logout: 'Sign Out'
      },
      // Landing
      landing: {
        hero_title: 'Master Your Exam with AI-Powered Preparation',
        hero_subtitle: 'Practice with realistic simulations, get instant feedback, and track your progress with our intelligent tutoring system.',
        get_started: 'Get Started Free',
        request_demo: 'Request Demo',
        trusted_by: 'Trusted by leading institutions worldwide'
      },
      // Pricing
      pricing: {
        title: 'Simple, Transparent Pricing',
        subtitle: 'Choose the plan that fits your institution',
        per_license: 'per license',
        per_month: '/month',
        individual_license: 'Individual License',
        duration: 'Contract Duration',
        months: 'months',
        month: 'month',
        total: 'Total',
        buy_now: 'Buy Now',
        request_demo: 'Request Free Demo',
        license_note: 'Each license is individual and gives full access to 1 student',
        licenses: 'licenses'
      },
      // Dashboard
      dashboard: {
        welcome: 'Welcome',
        my_exams: 'My Exams',
        progress: 'Progress',
        available: 'Available',
        completed: 'Completed',
        locked: 'Locked',
        start_exam: 'Start Exam',
        continue: 'Continue',
        view_results: 'View Results',
        credits_remaining: 'Credits Remaining'
      },
      // Exams
      exams: {
        mock_exam: 'Mock Exam',
        full_test: 'Full Test',
        section: 'Section',
        time_remaining: 'Time Remaining',
        questions: 'Questions',
        submit: 'Submit',
        next: 'Next',
        previous: 'Previous',
        finish: 'Finish Exam'
      },
      // Common
      common: {
        loading: 'Loading...',
        error: 'An error occurred',
        success: 'Success',
        save: 'Save',
        cancel: 'Cancel',
        delete: 'Delete',
        edit: 'Edit',
        search: 'Search',
        filter: 'Filter',
        all: 'All',
        yes: 'Yes',
        no: 'No'
      }
    }
  },
  es: {
    translation: {
      nav: {
        home: 'Inicio',
        features: 'Características',
        pricing: 'Precios',
        about: 'Nosotros',
        login: 'Iniciar Sesión',
        register: 'Comenzar',
        dashboard: 'Panel',
        logout: 'Cerrar Sesión'
      },
      landing: {
        hero_title: 'Domina tu Examen con Preparación Impulsada por IA',
        hero_subtitle: 'Practica con simulaciones realistas, obtén retroalimentación instantánea y sigue tu progreso con nuestro sistema de tutoría inteligente.',
        get_started: 'Comenzar Gratis',
        request_demo: 'Solicitar Demo',
        trusted_by: 'Confiado por instituciones líderes en todo el mundo'
      },
      pricing: {
        title: 'Precios Simples y Transparentes',
        subtitle: 'Elige el plan que se adapte a tu institución',
        per_license: 'por licencia',
        per_month: '/mes',
        individual_license: 'Licencia Individual',
        duration: 'Duración del Contrato',
        months: 'meses',
        month: 'mes',
        total: 'Total',
        buy_now: 'Contratar Ahora',
        request_demo: 'Solicitar Demo Gratuita',
        license_note: 'Cada licencia es individual y da acceso completo a 1 estudiante',
        licenses: 'licencias'
      },
      dashboard: {
        welcome: 'Bienvenido',
        my_exams: 'Mis Exámenes',
        progress: 'Progreso',
        available: 'Disponibles',
        completed: 'Completados',
        locked: 'Bloqueados',
        start_exam: 'Iniciar Examen',
        continue: 'Continuar',
        view_results: 'Ver Resultados',
        credits_remaining: 'Créditos Restantes'
      },
      exams: {
        mock_exam: 'Examen de Práctica',
        full_test: 'Test Completo',
        section: 'Sección',
        time_remaining: 'Tiempo Restante',
        questions: 'Preguntas',
        submit: 'Enviar',
        next: 'Siguiente',
        previous: 'Anterior',
        finish: 'Finalizar Examen'
      },
      common: {
        loading: 'Cargando...',
        error: 'Ocurrió un error',
        success: 'Éxito',
        save: 'Guardar',
        cancel: 'Cancelar',
        delete: 'Eliminar',
        edit: 'Editar',
        search: 'Buscar',
        filter: 'Filtrar',
        all: 'Todos',
        yes: 'Sí',
        no: 'No'
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
    debug: false,
    interpolation: {
      escapeValue: false
    },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage']
    }
  });

export default i18n;
