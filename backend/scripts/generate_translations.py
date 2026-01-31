"""
Translation Generation Script for ProficientHub

This script generates translations for all 80 supported languages
using the LLM translation service.

Run with: python -m scripts.generate_translations
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient

# Source texts in English (complete set)
SOURCE_TEXTS = {
    # Navigation
    "nav.home": "Home",
    "nav.features": "Features",
    "nav.pricing": "Pricing",
    "nav.about": "About",
    "nav.login": "Sign In",
    "nav.register": "Get Started",
    "nav.dashboard": "Dashboard",
    "nav.logout": "Sign Out",
    "nav.settings": "Settings",
    "nav.students": "Students",
    "nav.analytics": "Analytics",
    "nav.exams": "Exams",
    "nav.community": "Community",
    "nav.ai_tutor": "AI Tutor",
    
    # Landing page
    "landing.hero_title": "Scale Your Academy 10x With AI",
    "landing.hero_subtitle": "Your current teachers can handle 10x more students with AI tutors, instant feedback, and premium analytics.",
    "landing.get_started": "Start Free Trial",
    "landing.request_demo": "Request Demo",
    "landing.trusted_by": "Trusted by leading institutions worldwide",
    "landing.b2b_platform": "B2B Platform for Language Institutions",
    "landing.features_title": "Everything Your Institution Needs",
    "landing.features_subtitle": "Premium features designed for scale and student success",
    "landing.roi_calculator": "Calculate Your ROI",
    "landing.exams_badge": "10 Major Exams Supported",
    "landing.exams_title": "All Major English Proficiency Exams",
    "landing.exams_subtitle": "One platform, complete preparation with real exam conditions and AI-powered feedback",
    "landing.student_capacity": "Student Capacity",
    "landing.pass_rate_increase": "Pass Rate Increase",
    "landing.time_saved": "Time Saved",
    "landing.revenue_increase": "Revenue Increase",
    "landing.footer_tagline": "The most advanced B2B platform for language exam preparation",
    "landing.footer_product": "Product",
    "landing.footer_company": "Company",
    "landing.footer_support": "Support",
    "landing.contact_us": "Contact Us",
    "landing.help_center": "Help Center",
    "landing.privacy": "Privacy",
    "landing.terms": "Terms",
    
    # Pricing
    "pricing.title": "Simple, Transparent Pricing",
    "pricing.subtitle": "Choose the plan that fits your institution",
    "pricing.per_license": "per license",
    "pricing.per_month": "per month",
    "pricing.individual_license": "Individual License Price",
    "pricing.duration": "Contract Duration",
    "pricing.months": "months",
    "pricing.month": "month",
    "pricing.total": "Total",
    "pricing.buy_now": "Buy Now",
    "pricing.request_demo": "Request Free Demo",
    "pricing.license_note": "Each license is individual and gives full access to 1 student",
    "pricing.licenses": "licenses",
    "pricing.most_popular": "Most Popular",
    "pricing.enterprise": "Enterprise",
    "pricing.contact_sales": "Contact Sales",
    
    # Dashboard
    "dashboard.welcome": "Welcome back",
    "dashboard.my_exams": "My Exams",
    "dashboard.progress": "Progress",
    "dashboard.available": "Available",
    "dashboard.completed": "Completed",
    "dashboard.locked": "Locked",
    "dashboard.start_exam": "Start Exam",
    "dashboard.continue": "Continue",
    "dashboard.view_results": "View Results",
    "dashboard.credits_remaining": "Credits Remaining",
    "dashboard.total_students": "Total Students",
    "dashboard.pass_rate": "Pass Rate",
    "dashboard.at_risk": "At Risk Students",
    "dashboard.exams_completed": "Exams Completed",
    "dashboard.overview": "Overview",
    "dashboard.performance": "Performance Trend",
    "dashboard.distribution": "Exam Distribution",
    
    # Exams
    "exams.mock_exam": "Mock Exam",
    "exams.full_test": "Full Test",
    "exams.section": "Section",
    "exams.time_remaining": "Time Remaining",
    "exams.questions": "Questions",
    "exams.submit": "Submit",
    "exams.next": "Next",
    "exams.previous": "Previous",
    "exams.finish": "Finish Exam",
    "exams.start": "Start",
    "exams.resume": "Resume",
    "exams.full_mode": "Full Exam",
    "exams.section_mode": "By Sections",
    "exams.full_mode_desc": "Take all sections in one sitting, simulating real exam conditions.",
    "exams.section_mode_desc": "Complete each section separately, at your own pace.",
    "exams.sections_completed": "sections completed",
    "exams.in_progress": "In Progress",
    "exams.exam_used_warning": "Once started, the exam attempt will be used.",
    "exams.listening": "Listening",
    "exams.reading": "Reading",
    "exams.writing": "Writing",
    "exams.speaking": "Speaking",
    
    # Institution
    "institution.add_student": "Add Student",
    "institution.students": "Students",
    "institution.settings": "Settings",
    "institution.crm": "CRM & Sales",
    "institution.marketplace": "Marketplace",
    "institution.video_classes": "Video Classes",
    "institution.library": "Library",
    "institution.notifications": "Notifications",
    "institution.api_keys": "API Keys",
    "institution.integrations": "Integrations",
    "institution.erp": "ERP",
    "institution.sso": "SSO Configuration",
    "institution.alerts": "Alerts",
    
    # Common
    "common.loading": "Loading...",
    "common.error": "An error occurred",
    "common.success": "Success",
    "common.save": "Save",
    "common.cancel": "Cancel",
    "common.delete": "Delete",
    "common.edit": "Edit",
    "common.search": "Search",
    "common.filter": "Filter",
    "common.all": "All",
    "common.yes": "Yes",
    "common.no": "No",
    "common.add": "Add",
    "common.remove": "Remove",
    "common.view": "View",
    "common.download": "Download",
    "common.upload": "Upload",
    "common.back": "Back",
    "common.close": "Close",
    "common.confirm": "Confirm",
    "common.from_last_month": "from last month",
    "common.from_last_week": "from last week",
    "common.and": "and",
    "common.or": "or",
    "common.minutes": "minutes",
    "common.hours": "hours",
    "common.days": "days",
    "common.free": "Free",
    "common.included": "Included",
    "common.optional": "Optional",
    "common.required": "Required",
    "common.available": "Available",
    "common.unavailable": "Unavailable",
    
    # Features
    "features.ai_tutoring": "AI Tutoring Agents",
    "features.ai_tutoring_desc": "Personal AI tutor for each exam with voice conversations",
    "features.exam_practice": "Mock Exam Practice",
    "features.exam_practice_desc": "Full exam simulations with real conditions",
    "features.analytics": "Premium Analytics",
    "features.analytics_desc": "Detailed performance tracking and insights",
    "features.speaking": "Speaking Practice",
    "features.speaking_desc": "Dynamic conversations with AI avatar",
    "features.add_ai_tutor": "Add AI Tutor?",
    "features.no_ai_tutor": "No AI Tutor",
    "features.include_ai_tutor": "Include AI Tutor",
    "features.ai_tutor_conversation": "AI Tutor conversation",
    
    # Language selector
    "language.select": "Select Language",
    "language.search": "Search languages...",
    "language.popular": "Popular",
    "language.all_languages": "All Languages",
    "language.supported": "languages supported",
    
    # Auth
    "auth.login": "Login",
    "auth.signup": "Sign Up",
    "auth.email": "Email",
    "auth.password": "Password",
    "auth.confirm_password": "Confirm Password",
    "auth.forgot_password": "Forgot Password?",
    "auth.remember_me": "Remember me",
    "auth.no_account": "Don't have an account?",
    "auth.have_account": "Already have an account?",
    "auth.back_to_home": "Back to Home",
    "auth.select_user_type": "Select User Type",
    "auth.individual": "Individual Student",
    "auth.institution": "Institution",
    
    # Packs Manager
    "packs.title": "My Exam Packs",
    "packs.subtitle": "Create custom packs with mocks, AI tutor and your own services",
    "packs.create": "Create Pack",
    "packs.my_packs": "My Packs",
    "packs.sales": "Sales",
    "packs.no_packs": "No packs created",
    "packs.no_packs_desc": "Create your first exam pack combining mocks, AI tutor and your own services.",
    "packs.create_first": "Create my first Pack",
    "packs.basic_info": "Basic Information",
    "packs.pack_name": "Pack Name",
    "packs.exam_type": "Exam Type",
    "packs.profession": "Profession",
    "packs.all_professions": "All professions",
    "packs.description": "Description",
    "packs.features": "Pack Features",
    "packs.mock_exams": "Mock Exams",
    "packs.num_mocks": "Number of mocks",
    "packs.ai_tutor": "AI Tutor",
    "packs.ai_minutes": "Minutes (-1 = unlimited)",
    "packs.dynamic_speaking": "Dynamic Speaking",
    "packs.sessions": "Sessions (-1 = unlimited)",
    "packs.writing_evaluation": "Writing Evaluation",
    "packs.evaluations": "Evaluations (-1 = unlimited)",
    "packs.your_services": "Your Own Services",
    "packs.services_hint": "classes, books, tutoring...",
    "packs.service_name": "Service name",
    "packs.service_desc": "Description (optional)",
    "packs.price_validity": "Price and Validity",
    "packs.price": "Price",
    "packs.currency": "Currency",
    "packs.validity_days": "Validity (days)",
    "packs.display_options": "Display Options",
    "packs.mark_popular": "Mark as Popular",
    "packs.badge_text": "Badge text (e.g., Best Value)",
    "packs.save_changes": "Save Changes",
    "packs.pack_created": "Pack created",
    "packs.pack_updated": "Pack updated",
    "packs.pack_deleted": "Pack deleted",
    "packs.pack_duplicated": "Pack duplicated",
    "packs.sold": "sold",
    "packs.days": "days",
    "packs.unlimited": "unlimited",
    
    # Sales
    "sales.revenue": "Revenue (30 days)",
    "sales.total_sales": "Total Sales",
    "sales.average_ticket": "Average Ticket",
    "sales.by_pack": "Sales by Pack",
    "sales.recent": "Recent Sales"
}

# Target languages (excluding en, es, pt, de which are already fully translated)
TARGET_LANGUAGES = [
    'zh', 'hi', 'ar', 'bn', 'ru', 'ja', 'pa', 'jv', 'ko', 'fr', 'te', 'vi',
    'mr', 'ta', 'tr', 'ur', 'it', 'th', 'gu', 'pl', 'uk', 'ml', 'kn', 'or',
    'my', 'fa', 'ro', 'nl', 'hu', 'el', 'cs', 'sv', 'he', 'id', 'ms', 'fi',
    'da', 'no', 'sk', 'bg', 'sr', 'hr', 'lt', 'lv', 'et', 'sl', 'fil', 'sw',
    'am', 'ne', 'si', 'km', 'zu', 'xh', 'af', 'ca', 'eu', 'gl', 'is', 'ga',
    'cy', 'mt', 'lb', 'sq', 'mk', 'bs', 'az', 'ka', 'hy', 'kk', 'uz', 'mn',
    'lo', 'ps', 'tg'
]


async def generate_translations_for_language(api_url: str, language: str, source_texts: dict):
    """Generate translations for a single language"""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{api_url}/api/translations/translate-bulk",
                json={"target_language": language, "source_texts": source_texts},
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "language": language,
                        "status": "success",
                        "stats": data.get("stats", {})
                    }
                else:
                    error = await response.text()
                    return {"language": language, "status": "error", "error": error}
    except Exception as e:
        return {"language": language, "status": "error", "error": str(e)}


async def main():
    """Main function to generate all translations"""
    import aiohttp
    
    api_url = os.environ.get("API_URL", "http://localhost:8001")
    
    print(f"🌐 Translation Generation Script for ProficientHub")
    print(f"📦 Source texts: {len(SOURCE_TEXTS)} keys")
    print(f"🎯 Target languages: {len(TARGET_LANGUAGES)}")
    print(f"🔗 API URL: {api_url}")
    print("-" * 50)
    
    results = []
    
    for i, lang in enumerate(TARGET_LANGUAGES):
        print(f"\n[{i+1}/{len(TARGET_LANGUAGES)}] Generating translations for: {lang}")
        result = await generate_translations_for_language(api_url, lang, SOURCE_TEXTS)
        results.append(result)
        
        if result["status"] == "success":
            stats = result.get("stats", {})
            print(f"  ✅ Success - Total: {stats.get('total', 0)}, Cached: {stats.get('from_cache', 0)}, New: {stats.get('newly_translated', 0)}")
        else:
            print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(1)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = len(results) - success_count
    
    print(f"✅ Successful: {success_count}/{len(TARGET_LANGUAGES)}")
    print(f"❌ Errors: {error_count}/{len(TARGET_LANGUAGES)}")
    
    if error_count > 0:
        print("\nFailed languages:")
        for r in results:
            if r["status"] == "error":
                print(f"  - {r['language']}: {r.get('error', 'Unknown')}")


if __name__ == "__main__":
    asyncio.run(main())
