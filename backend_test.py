import requests
import sys
import json
from datetime import datetime
import uuid

class ProficientHubAPITester:
    def __init__(self, base_url="https://proftest-suite.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test_name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    Details: {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}, Expected: {expected_status}"
            
            if not success:
                try:
                    error_detail = response.json()
                    details += f", Response: {error_detail}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test(name, success, details)
            
            if success:
                try:
                    return response.json()
                except:
                    return {"status": "success"}
            return None

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def test_health_endpoints(self):
        """Test basic health endpoints"""
        print("\n🔍 Testing Health Endpoints...")
        
        # Test root endpoint
        self.run_test("Root Endpoint", "GET", "", 200)
        
        # Test health check
        self.run_test("Health Check", "GET", "health", 200)

    def test_pricing_endpoints(self):
        """Test pricing endpoints"""
        print("\n💰 Testing Pricing Endpoints...")
        
        # Test institutional pricing
        response = self.run_test("Institutional Pricing", "GET", "pricing/institutional", 200)
        if response and 'plans' in response:
            self.log_test("Pricing Plans Structure", True, f"Found {len(response['plans'])} plans")
        else:
            self.log_test("Pricing Plans Structure", False, "Missing plans in response")
        
        # Test individual pricing
        self.run_test("Individual Pricing", "GET", "pricing/individual", 200)
        
        # Test ROI calculator
        roi_params = "current_students=100&current_teachers=5&current_pass_rate=65&current_no_show_rate=20&teacher_salary=3000"
        response = self.run_test("ROI Calculator", "POST", f"pricing/calculate-roi?{roi_params}", 200)
        if response:
            required_fields = ['additional_students', 'improved_pass_rate', 'total_annual_benefit']
            missing_fields = [field for field in required_fields if field not in response]
            if not missing_fields:
                self.log_test("ROI Calculator Response Structure", True, "All required fields present")
            else:
                self.log_test("ROI Calculator Response Structure", False, f"Missing fields: {missing_fields}")
        
        # Test institutional pricing with exam count parameter
        response = self.run_test("Institutional Pricing with Exam Count", "GET", "pricing/institutional?exam_count=1", 200)
        if response and 'plans' in response:
            self.log_test("Pricing with Exam Count", True, f"Found {len(response['plans'])} plans for 1 exam")
        
        response = self.run_test("Institutional Pricing 3+ Exams", "GET", "pricing/institutional?exam_count=3", 200)
        if response and 'plans' in response:
            self.log_test("Pricing with 3+ Exams", True, f"Found {len(response['plans'])} plans for 3+ exams")

    def test_b2b_pricing_model(self):
        """Test new B2B pricing model endpoints"""
        print("\n🏢 Testing B2B Pricing Model...")
        
        # Test platform plans endpoint
        response = self.run_test("Platform Plans Endpoint", "GET", "pricing/platform-plans", 200)
        if response:
            # Verify exam_plans structure
            if 'exam_plans' in response:
                exam_plans = response['exam_plans']
                expected_plans = ['plan_5', 'plan_10', 'plan_20', 'plan_40', 'plan_60', 'plan_100']
                found_plan_ids = [plan['id'] for plan in exam_plans]
                missing_plans = [plan for plan in expected_plans if plan not in found_plan_ids]
                
                if len(exam_plans) == 6 and not missing_plans:
                    self.log_test("Exam Plans Structure", True, f"Found all 6 exam plans: {found_plan_ids}")
                else:
                    self.log_test("Exam Plans Structure", False, f"Expected 6 plans, found {len(exam_plans)}. Missing: {missing_plans}")
            else:
                self.log_test("Exam Plans Structure", False, "Missing exam_plans in response")
            
            # Verify volume_pricing structure
            if 'volume_pricing' in response:
                volume_tiers = response['volume_pricing']
                expected_tiers = ['tier_1_100', 'tier_101_500', 'tier_501_2000', 'tier_2001_10000']
                found_tier_ids = [tier['id'] for tier in volume_tiers]
                missing_tiers = [tier for tier in expected_tiers if tier not in found_tier_ids]
                
                if len(volume_tiers) == 4 and not missing_tiers:
                    self.log_test("Volume Pricing Structure", True, f"Found all 4 volume tiers: {found_tier_ids}")
                else:
                    self.log_test("Volume Pricing Structure", False, f"Expected 4 tiers, found {len(volume_tiers)}. Missing: {missing_tiers}")
            else:
                self.log_test("Volume Pricing Structure", False, "Missing volume_pricing in response")
            
            # Verify ai_tutor_options structure
            if 'ai_tutor_options' in response:
                ai_options = response['ai_tutor_options']
                expected_options = ['none', 'basic', 'standard', 'premium', 'unlimited']
                found_option_ids = [option['id'] for option in ai_options]
                missing_options = [option for option in expected_options if option not in found_option_ids]
                
                if len(ai_options) == 5 and not missing_options:
                    self.log_test("AI Tutor Options Structure", True, f"Found all 5 AI tutor options: {found_option_ids}")
                else:
                    self.log_test("AI Tutor Options Structure", False, f"Expected 5 options, found {len(ai_options)}. Missing: {missing_options}")
            else:
                self.log_test("AI Tutor Options Structure", False, "Missing ai_tutor_options in response")
        
        # Test pricing calculator with different scenarios
        test_scenarios = [
            {
                "name": "Plan 10 - 50 students - No AI",
                "params": "exam_plan=plan_10&num_students=50&ai_tutor_option=none&resale_price_per_student=25",
                "expected_cost": 9.40,
                "expected_price": 18.80
            },
            {
                "name": "Plan 20 - 200 students - Basic AI",
                "params": "exam_plan=plan_20&num_students=200&ai_tutor_option=basic&resale_price_per_student=50",
                "expected_tier": "tier_101_500"
            },
            {
                "name": "Plan 100 - 1000 students - Premium AI",
                "params": "exam_plan=plan_100&num_students=1000&ai_tutor_option=premium&resale_price_per_student=25",
                "expected_tier": "tier_501_2000"
            },
            {
                "name": "Plan 20 - 5000 students - Standard AI",
                "params": "exam_plan=plan_20&num_students=5000&ai_tutor_option=standard&resale_price_per_student=50",
                "expected_tier": "tier_2001_10000"
            }
        ]
        
        for scenario in test_scenarios:
            response = self.run_test(f"Calculator - {scenario['name']}", "GET", f"pricing/calculator?{scenario['params']}", 200)
            if response:
                # Verify response structure
                required_fields = ['plan', 'volume_tier', 'ai_tutor', 'pricing', 'customer_roi']
                missing_fields = [field for field in required_fields if field not in response]
                
                if not missing_fields:
                    self.log_test(f"Calculator Response Structure - {scenario['name']}", True, "All required fields present")
                    
                    # Verify pricing structure
                    if 'pricing' in response:
                        pricing = response['pricing']
                        pricing_fields = ['cost_per_student', 'price_per_student', 'total_cost', 'total_price', 'profit', 'margin_percentage']
                        missing_pricing_fields = [field for field in pricing_fields if field not in pricing]
                        
                        if not missing_pricing_fields:
                            self.log_test(f"Pricing Fields - {scenario['name']}", True, "All pricing fields present")
                            
                            # Test specific calculations for plan_10 scenario
                            if scenario['name'] == "Plan 10 - 50 students - No AI":
                                cost_per_student = pricing.get('cost_per_student', 0)
                                price_per_student = pricing.get('price_per_student', 0)
                                
                                if abs(cost_per_student - 9.40) < 0.01:
                                    self.log_test("Cost Calculation Accuracy", True, f"Cost per student: ${cost_per_student}")
                                else:
                                    self.log_test("Cost Calculation Accuracy", False, f"Expected $9.40, got ${cost_per_student}")
                                
                                if abs(price_per_student - 18.80) < 0.01:
                                    self.log_test("Price Calculation Accuracy", True, f"Price per student: ${price_per_student}")
                                else:
                                    self.log_test("Price Calculation Accuracy", False, f"Expected $18.80, got ${price_per_student}")
                        else:
                            self.log_test(f"Pricing Fields - {scenario['name']}", False, f"Missing pricing fields: {missing_pricing_fields}")
                    
                    # Verify volume tier assignment
                    if 'expected_tier' in scenario:
                        volume_tier = response.get('volume_tier', {}).get('id', '')
                        if volume_tier == scenario['expected_tier']:
                            self.log_test(f"Volume Tier Assignment - {scenario['name']}", True, f"Correct tier: {volume_tier}")
                        else:
                            self.log_test(f"Volume Tier Assignment - {scenario['name']}", False, f"Expected {scenario['expected_tier']}, got {volume_tier}")
                else:
                    self.log_test(f"Calculator Response Structure - {scenario['name']}", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test(f"Calculator - {scenario['name']}", False, "No response received")

    def test_admin_pricing_analysis(self):
        """Test admin pricing analysis endpoint"""
        print("\n👑 Testing Admin Pricing Analysis...")
        
        # First, try to login as admin
        admin_login_data = {
            "email": "santaliestralimited@gmail.com",
            "password": "Admin123!"
        }
        
        # Store current token
        original_token = self.token
        
        response = self.run_test("Admin Login", "POST", "auth/login", 200, admin_login_data)
        if response and 'access_token' in response:
            admin_token = response['access_token']
            self.token = admin_token
            self.log_test("Admin Authentication", True, "Admin login successful")
            
            # Test admin pricing analysis endpoint
            response = self.run_test("Admin Pricing Analysis", "GET", "admin/pricing-analysis", 200)
            if response:
                # Verify response structure
                required_sections = ['exam_costs', 'individual_test_costs', 'tier_analysis', 'ai_tutor_addon_analysis']
                missing_sections = [section for section in required_sections if section not in response]
                
                if not missing_sections:
                    self.log_test("Admin Analysis Structure", True, "All required sections present")
                    
                    # Verify tier_analysis structure
                    if 'tier_analysis' in response:
                        tier_analysis = response['tier_analysis']
                        if isinstance(tier_analysis, list) and len(tier_analysis) > 0:
                            first_tier = tier_analysis[0]
                            tier_fields = ['tier_id', 'licenses_range', 'price_per_license', 'price_per_exam', 'discount', 'internal_cost', 'profit_per_license', 'margin_percentage']
                            missing_tier_fields = [field for field in tier_fields if field not in first_tier]
                            
                            if not missing_tier_fields:
                                self.log_test("Tier Analysis Fields", True, "All tier analysis fields present")
                            else:
                                self.log_test("Tier Analysis Fields", False, f"Missing tier fields: {missing_tier_fields}")
                        else:
                            self.log_test("Tier Analysis Data", False, "Tier analysis is empty or not a list")
                    
                    # Verify exam_costs structure
                    if 'exam_costs' in response:
                        exam_costs = response['exam_costs']
                        if isinstance(exam_costs, dict) and len(exam_costs) > 0:
                            self.log_test("Exam Costs Data", True, f"Found exam costs for {len(exam_costs)} exam types")
                        else:
                            self.log_test("Exam Costs Data", False, "Exam costs data is empty or invalid")
                    
                    # Verify individual_test_costs
                    if 'individual_test_costs' in response:
                        test_costs = response['individual_test_costs']
                        expected_tests = ['writing', 'speaking']
                        found_tests = [test for test in expected_tests if test in test_costs]
                        
                        if len(found_tests) == len(expected_tests):
                            self.log_test("Individual Test Costs", True, f"Found costs for: {found_tests}")
                        else:
                            missing_tests = [test for test in expected_tests if test not in found_tests]
                            self.log_test("Individual Test Costs", False, f"Missing test costs: {missing_tests}")
                else:
                    self.log_test("Admin Analysis Structure", False, f"Missing sections: {missing_sections}")
            else:
                self.log_test("Admin Pricing Analysis", False, "No response received")
        else:
            self.log_test("Admin Authentication", False, "Admin login failed")
        
        # Restore original token
        self.token = original_token

    def test_exam_endpoints(self):
        """Test exam-related endpoints"""
        print("\n📚 Testing Exam Endpoints...")
        
        # Test exam types (public endpoint)
        response = self.run_test("Exam Types", "GET", "exams/types", 200)
        if response:
            if 'exam_types' in response and 'sections' in response:
                self.log_test("Exam Types Structure", True, f"Found {len(response['exam_types'])} exam types")
            else:
                self.log_test("Exam Types Structure", False, "Missing exam_types or sections")

    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication...")
        
        # Generate unique test user
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_email = f"test_institution_{timestamp}@example.com"
        test_password = "TestPassword123!"
        
        # Test registration
        register_data = {
            "email": test_email,
            "password": test_password,
            "name": f"Test Institution {timestamp}",
            "user_type": "institution",
            "institution_name": f"Test Academy {timestamp}"
        }
        
        response = self.run_test("User Registration", "POST", "auth/register", 200, register_data)
        if response and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            self.log_test("Registration Token Received", True, "Token stored for subsequent tests")
        else:
            self.log_test("Registration Token Received", False, "No token in registration response")
            return False
        
        # Test login with same credentials
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        response = self.run_test("User Login", "POST", "auth/login", 200, login_data)
        if response and 'access_token' in response:
            # Update token with login token
            self.token = response['access_token']
            self.log_test("Login Token Received", True, "Login successful")
        else:
            self.log_test("Login Token Received", False, "Login failed")
        
        # Test protected endpoint - get current user
        response = self.run_test("Get Current User", "GET", "auth/me", 200)
        if response and 'id' in response:
            self.log_test("Protected Route Access", True, "Successfully accessed protected endpoint")
        else:
            self.log_test("Protected Route Access", False, "Failed to access protected endpoint")
        
        return True

    def test_institution_features(self):
        """Test institution-specific features"""
        if not self.token:
            self.log_test("Institution Features", False, "No authentication token available")
            return
        
        print("\n🏫 Testing Institution Features...")
        
        # Test getting institution metrics
        response = self.run_test("Institution Metrics", "GET", "institution/metrics", 200)
        if response:
            required_metrics = ['total_students', 'avg_pass_probability', 'at_risk_students']
            missing_metrics = [metric for metric in required_metrics if metric not in response]
            if not missing_metrics:
                self.log_test("Metrics Structure", True, "All required metrics present")
            else:
                self.log_test("Metrics Structure", False, f"Missing metrics: {missing_metrics}")
        
        # Test getting students list (should be empty initially)
        response = self.run_test("Get Students List", "GET", "institution/students", 200)
        if response is not None:
            self.log_test("Students List Access", True, f"Retrieved {len(response)} students")
        
        # Test adding a student
        student_data = {
            "email": f"student_{datetime.now().strftime('%H%M%S')}@example.com",
            "name": f"Test Student {datetime.now().strftime('%H%M%S')}",
            "password": "StudentPass123!"
        }
        
        response = self.run_test("Add Student", "POST", "institution/students", 200, student_data)
        if response and 'id' in response:
            self.log_test("Student Creation", True, f"Student created with ID: {response['id']}")
            
            # Test getting updated students list
            response = self.run_test("Updated Students List", "GET", "institution/students", 200)
            if response and len(response) > 0:
                self.log_test("Student List Updated", True, f"Now showing {len(response)} students")
            else:
                self.log_test("Student List Updated", False, "Student list not updated after creation")
        else:
            self.log_test("Student Creation", False, "Failed to create student")

    def test_exam_practice_protected(self):
        """Test exam practice endpoints that require authentication"""
        if not self.token:
            self.log_test("Exam Practice Protected", False, "No authentication token available")
            return
        
        print("\n📝 Testing Protected Exam Features...")
        
        # Test getting practice questions
        response = self.run_test("Practice Questions TOEFL", "GET", "exams/toefl/practice?section=reading", 200)
        if response:
            if 'questions' in response and 'exam_type' in response:
                self.log_test("Practice Questions Structure", True, f"Retrieved {len(response['questions'])} questions")
            else:
                self.log_test("Practice Questions Structure", False, "Missing questions or exam_type")
        
        # Test exam history
        self.run_test("Exam History", "GET", "exams/history", 200)

    def test_ai_tutor(self):
        """Test AI tutor functionality"""
        if not self.token:
            self.log_test("AI Tutor", False, "No authentication token available")
            return
        
        print("\n🤖 Testing AI Tutor...")
        
        # Test AI tutor chat
        tutor_data = {
            "message": "How can I improve my IELTS reading score?",
            "exam_type": "ielts",
            "context": "I'm struggling with time management"
        }
        
        response = self.run_test("AI Tutor Chat", "POST", "ai-tutor/chat", 200, tutor_data)
        if response and 'response' in response:
            self.log_test("AI Tutor Response", True, f"Received response: {response['response'][:50]}...")
        else:
            self.log_test("AI Tutor Response", False, "No response from AI tutor")

    def test_library_features(self):
        """Test library functionality"""
        if not self.token:
            self.log_test("Library Features", False, "No authentication token available")
            return
        
        print("\n📚 Testing Library Features...")
        
        # Test getting library items (should be empty initially)
        response = self.run_test("Get Library Items", "GET", "library/items", 200)
        if response is not None:
            self.log_test("Library Items Access", True, f"Retrieved {len(response)} items")
        
        # Test creating a library item
        library_item_data = {
            "title": f"Test Material {datetime.now().strftime('%H%M%S')}",
            "item_type": "material",
            "content": "This is test content for the library item",
            "description": "A test library item for automated testing",
            "exam_type": "ielts",
            "tags": ["test", "reading"]
        }
        
        response = self.run_test("Create Library Item", "POST", "library/items", 200, library_item_data)
        if response and 'id' in response:
            item_id = response['id']
            self.log_test("Library Item Creation", True, f"Item created with ID: {item_id}")
            
            # Test getting updated library items list
            response = self.run_test("Updated Library Items", "GET", "library/items", 200)
            if response and len(response) > 0:
                self.log_test("Library Items Updated", True, f"Now showing {len(response)} items")
            else:
                self.log_test("Library Items Updated", False, "Library items not updated after creation")
            
            # Test deleting the library item
            self.run_test("Delete Library Item", "DELETE", f"library/items/{item_id}", 200)
        else:
            self.log_test("Library Item Creation", False, "Failed to create library item")
        
        # Test creating flashcards
        flashcard_data = {
            "title": f"Test Flashcards {datetime.now().strftime('%H%M%S')}",
            "cards": [
                {"front": "What is IELTS?", "back": "International English Language Testing System"},
                {"front": "TOEFL stands for?", "back": "Test of English as a Foreign Language"}
            ],
            "exam_type": "ielts",
            "tags": ["vocabulary", "test"]
        }
        
        response = self.run_test("Create Flashcard Set", "POST", "library/flashcards", 200, flashcard_data)
        if response and 'id' in response:
            self.log_test("Flashcard Creation", True, f"Flashcard set created with ID: {response['id']}")
        else:
            self.log_test("Flashcard Creation", False, "Failed to create flashcard set")

    def test_language_support(self):
        """Test language support endpoints"""
        print("\n🌍 Testing Language Support...")
        
        # Test getting supported languages
        response = self.run_test("Supported Languages", "GET", "languages", 200)
        if response and 'languages' in response:
            languages = response['languages']
            expected_languages = ['en', 'es', 'pt', 'de', 'it', 'fr']
            missing_languages = [lang for lang in expected_languages if lang not in languages]
            if not missing_languages:
                self.log_test("Language Support Complete", True, f"All {len(expected_languages)} languages supported")
            else:
                self.log_test("Language Support Complete", False, f"Missing languages: {missing_languages}")
        else:
            self.log_test("Language Support Complete", False, "No languages data in response")
        
        # Test updating user language settings (requires authentication)
        if self.token:
            settings_data = {"language": "es"}
            response = self.run_test("Update Language Settings", "PUT", "auth/settings", 200, settings_data)
            if response:
                self.log_test("Language Settings Update", True, "Language updated successfully")
            else:
                self.log_test("Language Settings Update", False, "Failed to update language")

    def test_unauthorized_access(self):
        """Test that protected endpoints properly reject unauthorized access"""
        print("\n🚫 Testing Unauthorized Access...")
        
        # Temporarily remove token
        original_token = self.token
        self.token = None
        
        # Test protected endpoints without token
        self.run_test("Unauthorized Metrics Access", "GET", "institution/metrics", 401)
        self.run_test("Unauthorized Students Access", "GET", "institution/students", 401)
        self.run_test("Unauthorized User Info", "GET", "auth/me", 401)
        
        # Test with invalid token
        self.token = "invalid_token_12345"
        self.run_test("Invalid Token Access", "GET", "auth/me", 401)
        
        # Restore original token
        self.token = original_token
        """Test that protected endpoints properly reject unauthorized access"""
        print("\n🚫 Testing Unauthorized Access...")
        
        # Temporarily remove token
        original_token = self.token
        self.token = None
        
        # Test protected endpoints without token
        self.run_test("Unauthorized Metrics Access", "GET", "institution/metrics", 401)
        self.run_test("Unauthorized Students Access", "GET", "institution/students", 401)
        self.run_test("Unauthorized User Info", "GET", "auth/me", 401)
        
        # Test with invalid token
        self.token = "invalid_token_12345"
        self.run_test("Invalid Token Access", "GET", "auth/me", 401)
        
        # Restore original token
        self.token = original_token

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting ProficientHub API Tests...")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Run test suites in order
        self.test_health_endpoints()
        self.test_pricing_endpoints()
        self.test_exam_endpoints()
        
        # Authentication tests
        auth_success = self.test_authentication()
        
        if auth_success:
            self.test_institution_features()
            self.test_library_features()
            self.test_exam_practice_protected()
            self.test_ai_tutor()
        
        self.test_language_support()
        self.test_unauthorized_access()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  - {test['test_name']}: {test['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = ProficientHubAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/test_reports/backend_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total_tests': tester.tests_run,
                'passed_tests': tester.tests_passed,
                'failed_tests': tester.tests_run - tester.tests_passed,
                'success_rate': (tester.tests_passed/tester.tests_run)*100 if tester.tests_run > 0 else 0
            },
            'detailed_results': tester.test_results,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())