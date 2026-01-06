import requests
import sys
import json
from datetime import datetime
import uuid

class ProficientHubAPITester:
    def __init__(self, base_url="https://proficienthub.preview.emergentagent.com/api"):
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
        roi_data = {
            "current_students": 100,
            "current_teachers": 5,
            "current_pass_rate": 65,
            "current_no_show_rate": 20,
            "teacher_salary": 3000
        }
        response = self.run_test("ROI Calculator", "POST", "pricing/calculate-roi", 200, roi_data)
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