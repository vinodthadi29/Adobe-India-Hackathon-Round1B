#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Document Intelligence System
Tests all core functionality including PDF processing, embeddings, and API endpoints
"""

import requests
import json
import time
import os
from pathlib import Path
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

# Get backend URL from frontend .env file
def get_backend_url():
    frontend_env_path = Path("/app/frontend/.env")
    if frontend_env_path.exists():
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    return "http://localhost:8001"

BASE_URL = get_backend_url()
API_URL = f"{BASE_URL}/api"

print(f"Testing backend at: {API_URL}")

class DocumentIntelligenceTest:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message="", details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        })
        print()

    def create_test_pdf(self, content, filename):
        """Create a test PDF with given content"""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Split content into lines and add to PDF
        lines = content.split('\n')
        y_position = 750
        
        for line in lines:
            if y_position < 50:  # Start new page if needed
                p.showPage()
                y_position = 750
            p.drawString(50, y_position, line)
            y_position -= 20
            
        p.save()
        buffer.seek(0)
        
        # Save to temporary file
        temp_path = f"/tmp/{filename}"
        with open(temp_path, 'wb') as f:
            f.write(buffer.getvalue())
        
        return temp_path

    def test_api_health_check(self):
        """Test basic API health check"""
        try:
            response = self.session.get(f"{API_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Document Intelligence API" in data["message"]:
                    self.log_test("API Health Check", True, "API is responding correctly")
                    return True
                else:
                    self.log_test("API Health Check", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("API Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_status_endpoints(self):
        """Test status check endpoints"""
        try:
            # Test POST /api/status
            status_data = {"client_name": "test_client"}
            response = self.session.post(f"{API_URL}/status", json=status_data)
            
            if response.status_code == 200:
                created_status = response.json()
                if "id" in created_status and "client_name" in created_status:
                    self.log_test("Status Creation", True, "Status check created successfully")
                    
                    # Test GET /api/status
                    response = self.session.get(f"{API_URL}/status")
                    if response.status_code == 200:
                        statuses = response.json()
                        if isinstance(statuses, list) and len(statuses) > 0:
                            self.log_test("Status Retrieval", True, f"Retrieved {len(statuses)} status checks")
                            return True
                        else:
                            self.log_test("Status Retrieval", False, "No status checks found")
                            return False
                    else:
                        self.log_test("Status Retrieval", False, f"HTTP {response.status_code}")
                        return False
                else:
                    self.log_test("Status Creation", False, f"Invalid response format: {created_status}")
                    return False
            else:
                self.log_test("Status Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Status Endpoints", False, f"Error: {str(e)}")
            return False

    def test_document_analysis_basic(self):
        """Test basic document analysis functionality"""
        try:
            # Create test PDF files
            pdf1_content = """
            Software Engineering Best Practices
            
            This document covers essential software engineering practices for modern development teams.
            Code review is a critical process that ensures code quality and knowledge sharing.
            Test-driven development helps create more reliable and maintainable software.
            Continuous integration and deployment streamline the development workflow.
            """
            
            pdf2_content = """
            Data Science and Machine Learning
            
            Machine learning algorithms can solve complex business problems.
            Data preprocessing is crucial for model performance and accuracy.
            Feature engineering significantly impacts the success of ML projects.
            Model evaluation and validation ensure reliable predictions.
            """
            
            pdf1_path = self.create_test_pdf(pdf1_content, "software_engineering.pdf")
            pdf2_path = self.create_test_pdf(pdf2_content, "data_science.pdf")
            
            # Test document analysis
            persona = "Senior Software Engineer"
            job = "Looking for best practices in software development and code quality"
            
            files = [
                ('files', ('software_engineering.pdf', open(pdf1_path, 'rb'), 'application/pdf')),
                ('files', ('data_science.pdf', open(pdf2_path, 'rb'), 'application/pdf'))
            ]
            
            data = {
                'persona': persona,
                'job': job
            }
            
            response = self.session.post(f"{API_URL}/analyze", files=files, data=data)
            
            # Close files
            for _, (_, file_obj, _) in files:
                file_obj.close()
            
            # Clean up temp files
            os.unlink(pdf1_path)
            os.unlink(pdf2_path)
            
            if response.status_code == 200:
                result = response.json()
                
                # Validate response structure
                required_fields = ['id', 'persona', 'job', 'results', 'timestamp']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    self.log_test("Document Analysis - Response Structure", False, 
                                f"Missing fields: {missing_fields}")
                    return False
                
                # Validate results structure
                results = result['results']
                if not isinstance(results, list):
                    self.log_test("Document Analysis - Results Format", False, 
                                "Results should be a list")
                    return False
                
                if len(results) == 0:
                    self.log_test("Document Analysis - Results Content", False, 
                                "No results returned")
                    return False
                
                # Validate individual result structure
                first_result = results[0]
                required_result_fields = ['page', 'rank', 'score', 'text', 'summary']
                missing_result_fields = [field for field in required_result_fields 
                                       if field not in first_result]
                
                if missing_result_fields:
                    self.log_test("Document Analysis - Result Structure", False, 
                                f"Missing result fields: {missing_result_fields}")
                    return False
                
                # Validate data types and ranges
                validation_errors = []
                for i, res in enumerate(results):
                    if not isinstance(res['page'], int) or res['page'] < 1:
                        validation_errors.append(f"Result {i}: Invalid page number")
                    if not isinstance(res['rank'], int) or res['rank'] < 1 or res['rank'] > 10:
                        validation_errors.append(f"Result {i}: Invalid rank")
                    if not isinstance(res['score'], (int, float)) or res['score'] < 0 or res['score'] > 1:
                        validation_errors.append(f"Result {i}: Invalid score range")
                    if not isinstance(res['text'], str) or len(res['text']) < 10:
                        validation_errors.append(f"Result {i}: Invalid text content")
                    if not isinstance(res['summary'], str) or len(res['summary']) < 5:
                        validation_errors.append(f"Result {i}: Invalid summary")
                
                if validation_errors:
                    self.log_test("Document Analysis - Data Validation", False, 
                                f"Validation errors: {validation_errors[:3]}")  # Show first 3 errors
                    return False
                
                # Check if results are properly ranked
                scores = [res['score'] for res in results]
                if scores != sorted(scores, reverse=True):
                    self.log_test("Document Analysis - Ranking", False, 
                                "Results are not properly ranked by score")
                    return False
                
                self.log_test("Document Analysis - Basic Functionality", True, 
                            f"Successfully processed {len(results)} results with scores ranging from {min(scores):.3f} to {max(scores):.3f}")
                
                # Store analysis ID for later tests
                self.analysis_id = result['id']
                return True
                
            else:
                self.log_test("Document Analysis - Basic Functionality", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Document Analysis - Basic Functionality", False, f"Error: {str(e)}")
            return False

    def test_pdf_text_extraction(self):
        """Test PDF text extraction specifically"""
        try:
            # Create a PDF with specific content to verify extraction
            test_content = """
            PDF Text Extraction Test Document
            
            This is page 1 with specific content for testing.
            We want to verify that PyMuPDF correctly extracts this text.
            Special characters: @#$%^&*()
            Numbers: 12345 67890
            """
            
            pdf_path = self.create_test_pdf(test_content, "extraction_test.pdf")
            
            persona = "Test Engineer"
            job = "Testing PDF text extraction functionality"
            
            files = [('files', ('extraction_test.pdf', open(pdf_path, 'rb'), 'application/pdf'))]
            data = {'persona': persona, 'job': job}
            
            response = self.session.post(f"{API_URL}/analyze", files=files, data=data)
            
            # Close file and clean up
            files[0][1][1].close()
            os.unlink(pdf_path)
            
            if response.status_code == 200:
                result = response.json()
                results = result['results']
                
                # Check if extracted text contains expected content
                all_text = ' '.join([res['text'] for res in results])
                
                expected_phrases = ["PDF Text Extraction", "page 1", "PyMuPDF", "12345"]
                found_phrases = [phrase for phrase in expected_phrases if phrase in all_text]
                
                if len(found_phrases) >= 2:  # At least 2 phrases should be found
                    self.log_test("PDF Text Extraction", True, 
                                f"Successfully extracted text containing {len(found_phrases)}/{len(expected_phrases)} expected phrases")
                    return True
                else:
                    self.log_test("PDF Text Extraction", False, 
                                f"Text extraction incomplete. Found phrases: {found_phrases}")
                    return False
            else:
                self.log_test("PDF Text Extraction", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("PDF Text Extraction", False, f"Error: {str(e)}")
            return False

    def test_embedding_and_similarity(self):
        """Test embedding generation and similarity scoring"""
        try:
            # Create PDFs with content that should have different similarity scores
            high_similarity_content = """
            Software Development Best Practices
            
            As a senior software engineer, code quality is paramount.
            Code reviews ensure maintainable and reliable software.
            Testing strategies improve software reliability.
            """
            
            low_similarity_content = """
            Cooking Recipes and Kitchen Tips
            
            Baking requires precise measurements and timing.
            Fresh ingredients make the biggest difference in taste.
            Proper knife skills improve cooking efficiency.
            """
            
            pdf1_path = self.create_test_pdf(high_similarity_content, "high_sim.pdf")
            pdf2_path = self.create_test_pdf(low_similarity_content, "low_sim.pdf")
            
            persona = "Senior Software Engineer"
            job = "Looking for software development best practices"
            
            files = [
                ('files', ('high_sim.pdf', open(pdf1_path, 'rb'), 'application/pdf')),
                ('files', ('low_sim.pdf', open(pdf2_path, 'rb'), 'application/pdf'))
            ]
            data = {'persona': persona, 'job': job}
            
            response = self.session.post(f"{API_URL}/analyze", files=files, data=data)
            
            # Close files and clean up
            for _, (_, file_obj, _) in files:
                file_obj.close()
            os.unlink(pdf1_path)
            os.unlink(pdf2_path)
            
            if response.status_code == 200:
                result = response.json()
                results = result['results']
                
                # Check if similarity scores make sense
                software_scores = []
                cooking_scores = []
                
                for res in results:
                    if any(word in res['text'].lower() for word in ['software', 'code', 'engineer', 'development']):
                        software_scores.append(res['score'])
                    elif any(word in res['text'].lower() for word in ['cooking', 'baking', 'kitchen', 'recipe']):
                        cooking_scores.append(res['score'])
                
                if software_scores and cooking_scores:
                    avg_software_score = sum(software_scores) / len(software_scores)
                    avg_cooking_score = sum(cooking_scores) / len(cooking_scores)
                    
                    if avg_software_score > avg_cooking_score:
                        self.log_test("Embedding and Similarity Scoring", True, 
                                    f"Similarity scoring working correctly. Software: {avg_software_score:.3f}, Cooking: {avg_cooking_score:.3f}")
                        return True
                    else:
                        self.log_test("Embedding and Similarity Scoring", False, 
                                    f"Similarity scores don't match expected relevance. Software: {avg_software_score:.3f}, Cooking: {avg_cooking_score:.3f}")
                        return False
                else:
                    self.log_test("Embedding and Similarity Scoring", True, 
                                "Embedding generation working, but content classification unclear")
                    return True
            else:
                self.log_test("Embedding and Similarity Scoring", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Embedding and Similarity Scoring", False, f"Error: {str(e)}")
            return False

    def test_file_validation(self):
        """Test file validation and error handling"""
        try:
            # Test with non-PDF file
            txt_content = "This is a text file, not a PDF"
            txt_path = "/tmp/test.txt"
            with open(txt_path, 'w') as f:
                f.write(txt_content)
            
            files = [('files', ('test.txt', open(txt_path, 'rb'), 'text/plain'))]
            data = {'persona': 'Test', 'job': 'Test'}
            
            response = self.session.post(f"{API_URL}/analyze", files=files, data=data)
            
            # Close file and clean up
            files[0][1][1].close()
            os.unlink(txt_path)
            
            if response.status_code == 400:
                self.log_test("File Type Validation", True, "Correctly rejected non-PDF file")
            else:
                self.log_test("File Type Validation", False, f"Should reject non-PDF files, got HTTP {response.status_code}")
                return False
            
            # Test with missing parameters
            response = self.session.post(f"{API_URL}/analyze", data={'persona': 'Test'})
            if response.status_code == 422:  # FastAPI validation error
                self.log_test("Parameter Validation", True, "Correctly rejected missing parameters")
            else:
                self.log_test("Parameter Validation", False, f"Should reject missing parameters, got HTTP {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("File Validation", False, f"Error: {str(e)}")
            return False

    def test_results_storage_and_retrieval(self):
        """Test MongoDB storage and retrieval of results"""
        try:
            # Test GET /api/analyses
            response = self.session.get(f"{API_URL}/analyses")
            
            if response.status_code == 200:
                analyses = response.json()
                if isinstance(analyses, list):
                    self.log_test("Results Retrieval - All Analyses", True, 
                                f"Retrieved {len(analyses)} stored analyses")
                    
                    # Test specific analysis retrieval if we have an ID
                    if hasattr(self, 'analysis_id') and analyses:
                        response = self.session.get(f"{API_URL}/analyses/{self.analysis_id}")
                        if response.status_code == 200:
                            analysis = response.json()
                            if 'id' in analysis and analysis['id'] == self.analysis_id:
                                self.log_test("Results Retrieval - Specific Analysis", True, 
                                            "Successfully retrieved specific analysis")
                                return True
                            else:
                                self.log_test("Results Retrieval - Specific Analysis", False, 
                                            "Retrieved analysis doesn't match requested ID")
                                return False
                        else:
                            self.log_test("Results Retrieval - Specific Analysis", False, 
                                        f"HTTP {response.status_code}")
                            return False
                    else:
                        return True  # No specific ID to test, but general retrieval works
                else:
                    self.log_test("Results Retrieval - All Analyses", False, 
                                "Response is not a list")
                    return False
            else:
                self.log_test("Results Retrieval - All Analyses", False, 
                            f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Results Storage and Retrieval", False, f"Error: {str(e)}")
            return False

    def test_multi_file_limits(self):
        """Test multi-file upload limits"""
        try:
            # Create multiple small PDFs
            pdf_paths = []
            files = []
            
            for i in range(12):  # Create 12 files (more than the 10 limit)
                content = f"Test document {i+1}\nThis is test content for document number {i+1}."
                pdf_path = self.create_test_pdf(content, f"test_{i+1}.pdf")
                pdf_paths.append(pdf_path)
                files.append(('files', (f'test_{i+1}.pdf', open(pdf_path, 'rb'), 'application/pdf')))
            
            data = {'persona': 'Test', 'job': 'Testing file limits'}
            
            response = self.session.post(f"{API_URL}/analyze", files=files, data=data)
            
            # Close files and clean up
            for _, (_, file_obj, _) in files:
                file_obj.close()
            for pdf_path in pdf_paths:
                os.unlink(pdf_path)
            
            if response.status_code == 400:
                self.log_test("Multi-file Limit Validation", True, 
                            "Correctly rejected more than 10 files")
                return True
            else:
                self.log_test("Multi-file Limit Validation", False, 
                            f"Should reject >10 files, got HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Multi-file Limit Validation", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 60)
        print("DOCUMENT INTELLIGENCE BACKEND TESTING")
        print("=" * 60)
        print()
        
        tests = [
            ("API Health Check", self.test_api_health_check),
            ("Status Endpoints", self.test_status_endpoints),
            ("PDF Text Extraction", self.test_pdf_text_extraction),
            ("Embedding and Similarity", self.test_embedding_and_similarity),
            ("Document Analysis Basic", self.test_document_analysis_basic),
            ("File Validation", self.test_file_validation),
            ("Multi-file Limits", self.test_multi_file_limits),
            ("Results Storage and Retrieval", self.test_results_storage_and_retrieval),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"Running: {test_name}")
            print("-" * 40)
            success = test_func()
            if success:
                passed += 1
            print()
        
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        # Print detailed results
        print("DETAILED RESULTS:")
        print("-" * 30)
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["message"]:
                print(f"   {result['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = DocumentIntelligenceTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Backend is working correctly.")
    else:
        print("\n⚠️  SOME TESTS FAILED. Check the details above.")
    
    exit(0 if success else 1)