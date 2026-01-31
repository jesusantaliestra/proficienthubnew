"""
Test Speech Service - Whisper STT Integration
Tests for POST /api/speech/transcribe and GET /api/speech/supported-formats endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestSpeechServiceSupportedFormats:
    """Tests for GET /api/speech/supported-formats endpoint"""
    
    def test_get_supported_formats_success(self):
        """Test that supported formats endpoint returns correct data"""
        response = requests.get(f"{BASE_URL}/api/speech/supported-formats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "formats" in data
        assert "max_size_mb" in data
        assert "default_language" in data
        assert "supported_languages" in data
        
        # Verify formats list
        expected_formats = ["webm", "wav", "mp3", "mp4", "m4a", "mpeg", "ogg"]
        assert data["formats"] == expected_formats
        
        # Verify max size
        assert data["max_size_mb"] == 25
        
        # Verify default language
        assert data["default_language"] == "en"
        
        # Verify supported languages include common ones
        assert "en" in data["supported_languages"]
        assert "es" in data["supported_languages"]
        assert "fr" in data["supported_languages"]
        assert len(data["supported_languages"]) >= 20


class TestSpeechServiceTranscribe:
    """Tests for POST /api/speech/transcribe endpoint"""
    
    def test_transcribe_valid_wav_file(self):
        """Test transcription with valid WAV audio file"""
        # Use the test audio file
        test_audio_path = "/tmp/test_audio.wav"
        
        if not os.path.exists(test_audio_path):
            pytest.skip("Test audio file not found at /tmp/test_audio.wav")
        
        with open(test_audio_path, "rb") as audio_file:
            files = {"file": ("test_audio.wav", audio_file, "audio/wav")}
            data = {"language": "en"}
            
            response = requests.post(
                f"{BASE_URL}/api/speech/transcribe",
                files=files,
                data=data
            )
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify response structure
        assert "text" in result
        assert "language" in result
        assert isinstance(result["text"], str)
        assert result["language"] == "en"
        print(f"Transcribed text: {result['text']}")
    
    def test_transcribe_with_prompt_context(self):
        """Test transcription with custom prompt for context"""
        test_audio_path = "/tmp/test_audio.wav"
        
        if not os.path.exists(test_audio_path):
            pytest.skip("Test audio file not found at /tmp/test_audio.wav")
        
        with open(test_audio_path, "rb") as audio_file:
            files = {"file": ("test_audio.wav", audio_file, "audio/wav")}
            data = {
                "language": "en",
                "prompt": "Healthcare professional speaking to a patient about medication."
            }
            
            response = requests.post(
                f"{BASE_URL}/api/speech/transcribe",
                files=files,
                data=data
            )
        
        assert response.status_code == 200
        result = response.json()
        assert "text" in result
        print(f"Transcribed with prompt: {result['text']}")
    
    def test_transcribe_with_session_id(self):
        """Test transcription with session_id for logging"""
        test_audio_path = "/tmp/test_audio.wav"
        
        if not os.path.exists(test_audio_path):
            pytest.skip("Test audio file not found at /tmp/test_audio.wav")
        
        with open(test_audio_path, "rb") as audio_file:
            files = {"file": ("test_audio.wav", audio_file, "audio/wav")}
            data = {
                "language": "en",
                "session_id": "test-session-12345"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/speech/transcribe",
                files=files,
                data=data
            )
        
        assert response.status_code == 200
        result = response.json()
        assert "text" in result
        print(f"Transcribed with session_id: {result['text']}")


class TestSpeechServiceValidation:
    """Tests for input validation on transcribe endpoint"""
    
    def test_transcribe_empty_file_returns_400(self):
        """Test that empty audio file returns 400 error"""
        # Create an empty file
        empty_content = b""
        files = {"file": ("empty.wav", empty_content, "audio/wav")}
        data = {"language": "en"}
        
        response = requests.post(
            f"{BASE_URL}/api/speech/transcribe",
            files=files,
            data=data
        )
        
        assert response.status_code == 400
        error = response.json()
        assert "detail" in error
        assert "small" in error["detail"].lower() or "empty" in error["detail"].lower()
        print(f"Empty file error: {error['detail']}")
    
    def test_transcribe_too_small_file_returns_400(self):
        """Test that very small audio file returns 400 error"""
        # Create a file smaller than 100 bytes
        small_content = b"x" * 50
        files = {"file": ("small.wav", small_content, "audio/wav")}
        data = {"language": "en"}
        
        response = requests.post(
            f"{BASE_URL}/api/speech/transcribe",
            files=files,
            data=data
        )
        
        assert response.status_code == 400
        error = response.json()
        assert "detail" in error
        assert "small" in error["detail"].lower() or "empty" in error["detail"].lower()
        print(f"Small file error: {error['detail']}")
    
    def test_transcribe_unsupported_format_returns_400(self):
        """Test that unsupported audio format returns 400 error"""
        # Create a fake file with unsupported content type
        fake_content = b"fake audio content" * 10
        files = {"file": ("test.xyz", fake_content, "application/x-unknown")}
        data = {"language": "en"}
        
        response = requests.post(
            f"{BASE_URL}/api/speech/transcribe",
            files=files,
            data=data
        )
        
        assert response.status_code == 400
        error = response.json()
        assert "detail" in error
        assert "unsupported" in error["detail"].lower() or "format" in error["detail"].lower()
        print(f"Unsupported format error: {error['detail']}")
    
    def test_transcribe_no_file_returns_422(self):
        """Test that missing file returns 422 validation error"""
        data = {"language": "en"}
        
        response = requests.post(
            f"{BASE_URL}/api/speech/transcribe",
            data=data
        )
        
        # FastAPI returns 422 for missing required fields
        assert response.status_code == 422
        print("Missing file correctly returns 422")


class TestSpeechServiceLanguages:
    """Tests for different language support"""
    
    def test_transcribe_spanish_language(self):
        """Test transcription with Spanish language setting"""
        test_audio_path = "/tmp/test_audio.wav"
        
        if not os.path.exists(test_audio_path):
            pytest.skip("Test audio file not found at /tmp/test_audio.wav")
        
        with open(test_audio_path, "rb") as audio_file:
            files = {"file": ("test_audio.wav", audio_file, "audio/wav")}
            data = {"language": "es"}
            
            response = requests.post(
                f"{BASE_URL}/api/speech/transcribe",
                files=files,
                data=data
            )
        
        assert response.status_code == 200
        result = response.json()
        assert "text" in result
        assert result["language"] == "es"
        print(f"Spanish transcription: {result['text']}")
    
    def test_transcribe_default_language(self):
        """Test transcription without specifying language (should default to en)"""
        test_audio_path = "/tmp/test_audio.wav"
        
        if not os.path.exists(test_audio_path):
            pytest.skip("Test audio file not found at /tmp/test_audio.wav")
        
        with open(test_audio_path, "rb") as audio_file:
            files = {"file": ("test_audio.wav", audio_file, "audio/wav")}
            # No language specified
            
            response = requests.post(
                f"{BASE_URL}/api/speech/transcribe",
                files=files
            )
        
        assert response.status_code == 200
        result = response.json()
        assert "text" in result
        # Default should be English
        assert result["language"] == "en"
        print(f"Default language transcription: {result['text']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
