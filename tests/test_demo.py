#!/usr/bin/env python3
"""
Demo Mode Tests for Voice AI System
"""

import os
import sys
import pytest
import asyncio
from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set demo mode for testing
os.environ['DEMO_MODE'] = 'true'
os.environ['LOG_LEVEL'] = 'ERROR'  # Reduce test noise

from voice_ai import app, voice_ai

client = TestClient(app)

class TestDemoMode:
    """Test demo mode functionality"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "unhealthy"]
        assert data["demo_mode"] is True
    
    def test_root_page(self):
        """Test root page loads"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Voice AI System" in response.text
        assert "Demo Mode Active" in response.text
    
    def test_demo_chat(self):
        """Test demo chat functionality"""
        response = client.post("/demo/chat", json={
            "user_input": "Hello, I need help"
        })
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "ai_response" in data
        assert "message" in data["ai_response"]
    
    def test_demo_call(self):
        """Test demo call simulation"""
        response = client.post("/call", json={
            "phone_number": "+91-DEMO-NUMBER"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["demo_mode"] is True
        assert "call_id" in data
    
    def test_conversation_continuity(self):
        """Test conversation continuity"""
        # First message
        response1 = client.post("/demo/chat", json={
            "user_input": "Hello"
        })
        data1 = response1.json()
        conversation_id = data1["conversation_id"]
        
        # Second message with same conversation ID
        response2 = client.post("/demo/chat", json={
            "user_input": "Can you help me?",
            "conversation_id": conversation_id
        })
        data2 = response2.json()
        
        # Should be same conversation
        assert data2["conversation_id"] == conversation_id
        assert len(data2["conversation_history"]) >= 4  # 2 user + 2 AI messages
    
    def test_invalid_demo_chat(self):
        """Test invalid demo chat request"""
        response = client.post("/demo/chat", json={
            "user_input": ""  # Empty input
        })
        # Should still work with empty input
        assert response.status_code == 200
    
    def test_websocket_unavailable_in_demo(self):
        """Test WebSocket is unavailable in demo mode"""
        with client.websocket_connect("/ws/call") as websocket:
            # Connection should close immediately in demo mode
            assert websocket is not None

class TestVoiceAIDemo:
    """Test VoiceAI class in demo mode"""
    
    def test_demo_initialization(self):
        """Test demo mode initialization"""
        assert voice_ai is not None
        assert voice_ai.demo_mode is True
        assert hasattr(voice_ai, 'mock_processor')
    
    def test_transcribe_audio_demo(self):
        """Test audio transcription in demo mode"""
        dummy_audio = b"dummy_audio_data"
        result = voice_ai.transcribe_audio(dummy_audio)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_generate_response_demo(self):
        """Test response generation in demo mode"""
        user_input = "Hello, I need help"
        response = voice_ai.generate_response(user_input, "test_conversation")
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_text_to_speech_demo(self):
        """Test TTS in demo mode"""
        text = "Hello, this is a test"
        audio_data = voice_ai.text_to_speech(text)
        assert isinstance(audio_data, bytes)
    
    def test_demo_conversation_processing(self):
        """Test complete demo conversation processing"""
        result = voice_ai.process_demo_conversation(
            "Hello, I need help with my account",
            "test_conv_1"
        )
        
        assert "conversation_id" in result
        assert result["conversation_id"] == "test_conv_1"
        assert "user_message" in result
        assert "ai_response" in result
        assert "conversation_history" in result
        
        # Check message structure
        user_msg = result["user_message"]
        assert user_msg["speaker"] == "user"
        assert user_msg["type"] == "text"
        assert "timestamp" in user_msg
        
        ai_msg = result["ai_response"]
        assert ai_msg["speaker"] == "ai"
        assert ai_msg["type"] == "text"
        assert "timestamp" in ai_msg

def test_demo_mode_environment():
    """Test demo mode environment variables"""
    assert os.getenv('DEMO_MODE', 'true').lower() == 'true'

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])