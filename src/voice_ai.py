#!/usr/bin/env python3
"""
Voice AI System - Local Testing & Production Ready
Supports both demo mode (local testing) and production mode (with Plivo)
"""

import asyncio
import json
import base64
import logging
import os
import sys
import tempfile
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Union
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import torch
import numpy as np

# Try to import optional dependencies
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️  Whisper not available - using mock STT")

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  Transformers not available - using mock LLM")

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️  pyttsx3 not available - using mock TTS")

try:
    from plivo import RestClient
    PLIVO_AVAILABLE = True
except ImportError:
    PLIVO_AVAILABLE = False
    print("⚠️  Plivo not available - demo mode only")

# Load environment variables
load_dotenv()

# Setup logging
def setup_logging():
    log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO'))
    log_file = os.getenv('LOG_FILE', 'logs/voice_ai.log')
    
    # Create logs directory
    Path(log_file).parent.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)

# Request Models
class CallRequest(BaseModel):
    phone_number: str
    message: Optional[str] = None

class DemoRequest(BaseModel):
    user_input: str
    conversation_id: Optional[str] = None

class MockAudioProcessor:
    """Mock audio processor for demo mode"""
    
    def __init__(self):
        self.responses = [
            "I understand you'd like assistance. How can I help you today?",
            "Thank you for that information. Let me help you with that.",
            "I see. Could you provide more details about your request?",
            "That's a great question. Let me explain that for you.",
            "I'll be happy to assist you with that. What else would you like to know?",
            "Is there anything specific you'd like help with?",
            "Thank you for calling. How else can I assist you today?"
        ]
        self.response_index = 0
    
    def transcribe(self, audio_data: bytes) -> str:
        """Mock speech-to-text"""
        mock_inputs = [
            "Hello, I need help with my account",
            "Can you help me with billing questions?",
            "I want to know about your services",
            "How do I cancel my subscription?",
            "What are your business hours?",
            "Can I speak to a manager?",
            "Thank you for your help"
        ]
        return mock_inputs[self.response_index % len(mock_inputs)]
    
    def generate_response(self, user_input: str) -> str:
        """Mock LLM response generation"""
        response = self.responses[self.response_index % len(self.responses)]
        self.response_index += 1
        return response
    
    def text_to_speech(self, text: str) -> bytes:
        """Mock TTS - returns empty bytes"""
        return b"mock_audio_data"

class VoiceAI:
    """Main Voice AI class with demo and production modes"""
    
    def __init__(self):
        self.demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
        logger.info(f"🤖 Initializing Voice AI (Demo Mode: {self.demo_mode})")
        
        # Initialize components based on mode
        if self.demo_mode:
            self._init_demo_mode()
        else:
            self._init_production_mode()
        
        # Call management
        self.active_calls: Dict[str, dict] = {}
        self.demo_conversations: Dict[str, List[dict]] = {}
        
        logger.info("✅ Voice AI initialized successfully!")
    
    def _init_demo_mode(self):
        """Initialize demo mode components"""
        logger.info("🎭 Initializing Demo Mode")
        self.mock_processor = MockAudioProcessor()
        
        # Try to load real models if available
        if WHISPER_AVAILABLE and os.getenv('USE_LOCAL_MODELS', 'true').lower() == 'true':
            try:
                logger.info("📥 Loading Whisper model for demo...")
                self.whisper_model = whisper.load_model("base")
                logger.info("✅ Whisper loaded")
            except Exception as e:
                logger.warning(f"⚠️  Could not load Whisper: {e}")
                self.whisper_model = None
        else:
            self.whisper_model = None
        
        if TRANSFORMERS_AVAILABLE:
            try:
                logger.info("📥 Loading LLM for demo...")
                model_name = "microsoft/DialoGPT-medium"
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.llm_model = AutoModelForCausalLM.from_pretrained(model_name)
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                logger.info("✅ LLM loaded")
            except Exception as e:
                logger.warning(f"⚠️  Could not load LLM: {e}")
                self.tokenizer = None
                self.llm_model = None
        else:
            self.tokenizer = None
            self.llm_model = None
        
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
                logger.info("✅ TTS initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize TTS: {e}")
                self.tts_engine = None
        else:
            self.tts_engine = None
        
        self.plivo_client = None
    
    def _init_production_mode(self):
        """Initialize production mode components"""
        logger.info("🚀 Initializing Production Mode")
        
        if not PLIVO_AVAILABLE:
            raise ImportError("Plivo package required for production mode")
        
        # Initialize Plivo
        auth_id = os.getenv('PLIVO_AUTH_ID')
        auth_token = os.getenv('PLIVO_AUTH_TOKEN')
        
        if not auth_id or not auth_token:
            raise ValueError("PLIVO_AUTH_ID and PLIVO_AUTH_TOKEN required for production mode")
        
        self.plivo_client = RestClient(auth_id, auth_token)
        
        # Load AI models
        self._load_models()
    
    def _load_models(self):
        """Load AI models for production"""
        if WHISPER_AVAILABLE:
            model_name = os.getenv('WHISPER_MODEL', 'base')
            self.whisper_model = whisper.load_model(model_name)
        
        if TRANSFORMERS_AVAILABLE:
            model_name = os.getenv('LLM_MODEL', 'microsoft/DialoGPT-medium')
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.llm_model = AutoModelForCausalLM.from_pretrained(model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
        
        if TTS_AVAILABLE:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
    
    def transcribe_audio(self, audio_data: bytes) -> str:
        """Convert audio to text"""
        if self.demo_mode:
            return self.mock_processor.transcribe(audio_data)
        
        if self.whisper_model:
            try:
                # Convert bytes to numpy array for Whisper
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                result = self.whisper_model.transcribe(audio_np, language='en')
                return result["text"].strip()
            except Exception as e:
                logger.error(f"❌ Transcription error: {e}")
        
        return "Sorry, I didn't catch that."
    
    def generate_response(self, user_input: str, conversation_id: str = None) -> str:
        """Generate AI response"""
        if self.demo_mode:
            # Use mock processor or real LLM if available
            if self.llm_model and self.tokenizer:
                return self._generate_llm_response(user_input, conversation_id)
            else:
                return self.mock_processor.generate_response(user_input)
        
        return self._generate_llm_response(user_input, conversation_id)
    
    def _generate_llm_response(self, user_input: str, conversation_id: str = None) -> str:
        """Generate response using LLM"""
        try:
            # Get conversation history
            if conversation_id not in self.active_calls:
                self.active_calls[conversation_id] = {'history': []}
            
            call_data = self.active_calls[conversation_id]
            
            # System prompt
            system_prompt = """You are a helpful customer service representative.
            Be polite, professional, and concise. Keep responses under 40 words.
            If you don't know something, offer to connect them with a specialist."""
            
            # Add to history
            call_data['history'].append(f"Customer: {user_input}")
            
            # Create prompt with context
            recent_history = call_data['history'][-6:]  # Last 3 exchanges
            context = "\n".join(recent_history)
            prompt = f"{system_prompt}\n\nConversation:\n{context}\nAssistant:"
            
            # Generate response
            inputs = self.tokenizer.encode(prompt, return_tensors='pt', max_length=400, truncation=True)
            
            with torch.no_grad():
                outputs = self.llm_model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 50,
                    temperature=0.8,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id
                )
            
            response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            response = response.strip().replace("Assistant:", "")
            
            if not response or len(response) < 3:
                response = "I understand. How else can I help you?"
            
            # Add to history
            call_data['history'].append(f"Assistant: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Response generation error: {e}")
            return "I apologize for the technical difficulty. How can I assist you?"
    
    def text_to_speech(self, text: str) -> bytes:
        """Convert text to speech"""
        if self.demo_mode and not os.getenv('DEMO_ENABLE_TTS', 'true').lower() == 'true':
            return self.mock_processor.text_to_speech(text)
        
        if self.tts_engine:
            try:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                self.tts_engine.save_to_file(text, temp_path)
                self.tts_engine.runAndWait()
                
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                
                os.unlink(temp_path)
                return audio_data
                
            except Exception as e:
                logger.error(f"❌ TTS error: {e}")
        
        return b""
    
    def process_demo_conversation(self, user_input: str, conversation_id: str = None) -> dict:
        """Process conversation in demo mode"""
        if not conversation_id:
            conversation_id = f"demo_{int(time.time())}"
        
        if conversation_id not in self.demo_conversations:
            self.demo_conversations[conversation_id] = []
        
        # Add user input
        user_message = {
            "timestamp": datetime.now().isoformat(),
            "speaker": "user",
            "message": user_input,
            "type": "text"
        }
        self.demo_conversations[conversation_id].append(user_message)
        
        # Generate AI response
        ai_response = self.generate_response(user_input, conversation_id)
        
        # Add AI response
        ai_message = {
            "timestamp": datetime.now().isoformat(),
            "speaker": "ai",
            "message": ai_response,
            "type": "text"
        }
        self.demo_conversations[conversation_id].append(ai_message)
        
        logger.info(f"👤 User: {user_input}")
        logger.info(f"🤖 AI: {ai_response}")
        
        return {
            "conversation_id": conversation_id,
            "user_message": user_message,
            "ai_response": ai_message,
            "conversation_history": self.demo_conversations[conversation_id]
        }
    
    def make_outbound_call(self, phone_number: str) -> str:
        """Make outbound call (production mode only)"""
        if self.demo_mode:
            call_id = f"demo_call_{int(time.time())}"
            logger.info(f"📞 Demo call initiated to {phone_number} (Call ID: {call_id})")
            return call_id
        
        if not self.plivo_client:
            raise ValueError("Plivo not configured for production calls")
        
        try:
            public_url = os.getenv('PUBLIC_URL', 'http://localhost:8000')
            ws_url = f"{public_url.replace('http', 'ws')}/ws/call"
            
            answer_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Stream bidirectional="true" keepCallAlive="true" 
            streamTimeout="86400" contentType="audio/x-l16" 
            sampleRate="8000">{ws_url}</Stream>
</Response>"""
            
            call = self.plivo_client.calls.create(
                from_=os.getenv('PLIVO_PHONE_NUMBER'),
                to_=phone_number,
                answer_url='data:application/xml;charset=utf-8,' + answer_xml,
                answer_method='GET'
            )
            
            logger.info(f"📞 Call initiated to {phone_number}")
            return call.call_uuid
            
        except Exception as e:
            logger.error(f"❌ Call failed: {e}")
            raise

# Initialize FastAPI app
app = FastAPI(
    title="Voice AI System",
    description="Local testing & production ready voice AI",
    version="1.0.0"
)

# Initialize Voice AI
try:
    voice_ai = VoiceAI()
except Exception as e:
    logger.error(f"❌ Failed to initialize Voice AI: {e}")
    voice_ai = None

# Routes
@app.get("/")
async def root():
    """Main page with demo interface"""
    demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Voice AI System</title>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px; 
                margin: 40px auto; 
                padding: 20px;
                background: #f5f5f7;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }}
            .status {{
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                font-weight: 500;
            }}
            .demo {{ background: #e3f2fd; color: #1565c0; border-left: 4px solid #2196f3; }}
            .production {{ background: #e8f5e8; color: #2e7d32; border-left: 4px solid #4caf50; }}
            .error {{ background: #ffebee; color: #c62828; border-left: 4px solid #f44336; }}
            .demo-chat {{
                border: 1px solid #ddd;
                border-radius: 8px;
                height: 300px;
                overflow-y: auto;
                padding: 15px;
                margin: 15px 0;
                background: #fafafa;
            }}
            .message {{
                margin: 10px 0;
                padding: 8px 12px;
                border-radius: 8px;
                max-width: 80%;
            }}
            .user {{ 
                background: #2196f3; 
                color: white; 
                margin-left: auto; 
                text-align: right;
            }}
            .ai {{ 
                background: #f1f1f1; 
                color: #333; 
            }}
            input, button {{
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 16px;
            }}
            button {{
                background: #2196f3;
                color: white;
                border: none;
                cursor: pointer;
                transition: background 0.3s;
            }}
            button:hover {{ background: #1976d2; }}
            .input-group {{
                display: flex;
                gap: 10px;
                margin-top: 15px;
            }}
            .input-group input {{ flex: 1; }}
            h1 {{ color: #333; margin-bottom: 10px; }}
            h2 {{ color: #555; margin-top: 30px; }}
            code {{ 
                background: #f5f5f5; 
                padding: 2px 6px; 
                border-radius: 4px; 
                font-family: 'SF Mono', monospace;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Voice AI System</h1>
            
            <div class="status {'demo' if demo_mode else 'production'}">
                {'🎭 Demo Mode Active - Test locally without Plivo' if demo_mode else '🚀 Production Mode - Connected to Plivo'}
            </div>
            
            {'<h2>💬 Demo Chat Interface</h2><div id="chat" class="demo-chat"></div><div class="input-group"><input type="text" id="userInput" placeholder="Type your message..." onkeypress="handleKeyPress(event)"><button onclick="sendMessage()">Send</button></div>' if demo_mode else ''}
            
            <h2>📋 API Endpoints</h2>
            <ul>
                <li><strong>GET /health</strong> - System health check</li>
                {'<li><strong>POST /demo/chat</strong> - Demo conversation</li>' if demo_mode else ''}
                <li><strong>POST /call</strong> - {'Demo call simulation' if demo_mode else 'Make outbound call'}</li>
                <li><strong>WS /ws/call</strong> - WebSocket for audio streaming</li>
            </ul>
            
            <h2>🧪 Test Commands</h2>
            <p>Health check:</p>
            <code>curl http://localhost:8000/health</code>
            
            {'<p>Demo chat:</p><code>curl -X POST http://localhost:8000/demo/chat -H "Content-Type: application/json" -d \'{"user_input": "Hello, I need help"}\'</code>' if demo_mode else ''}
            
            <p>{'Demo call:' if demo_mode else 'Make call:'}</p>
            <code>curl -X POST http://localhost:8000/call -H "Content-Type: application/json" -d '{{"phone_number": "+91XXXXXXXXXX"}}'</code>
        </div>
        
        {'<script>let conversationId = null; function handleKeyPress(event) { if (event.key === "Enter") sendMessage(); } async function sendMessage() { const input = document.getElementById("userInput"); const message = input.value.trim(); if (!message) return; addMessage(message, "user"); input.value = ""; try { const response = await fetch("/demo/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ user_input: message, conversation_id: conversationId }) }); const data = await response.json(); conversationId = data.conversation_id; addMessage(data.ai_response.message, "ai"); } catch (error) { addMessage("Error: " + error.message, "ai"); } } function addMessage(text, sender) { const chat = document.getElementById("chat"); const message = document.createElement("div"); message.className = `message ${sender}`; message.textContent = text; chat.appendChild(message); chat.scrollTop = chat.scrollHeight; }</script>' if demo_mode else ''}
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if voice_ai else "unhealthy",
        "demo_mode": os.getenv('DEMO_MODE', 'true').lower() == 'true',
        "timestamp": datetime.now().isoformat(),
        "components": {
            "whisper": WHISPER_AVAILABLE,
            "transformers": TRANSFORMERS_AVAILABLE,
            "tts": TTS_AVAILABLE,
            "plivo": PLIVO_AVAILABLE and not os.getenv('DEMO_MODE', 'true').lower() == 'true'
        }
    }

@app.post("/demo/chat")
async def demo_chat(request: DemoRequest):
    """Demo chat endpoint for local testing"""
    if not voice_ai:
        raise HTTPException(status_code=500, detail="Voice AI not initialized")
    
    if not voice_ai.demo_mode:
        raise HTTPException(status_code=400, detail="Demo mode not enabled")
    
    try:
        result = voice_ai.process_demo_conversation(
            request.user_input, 
            request.conversation_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.post("/call")
async def make_call(request: CallRequest):
    """Make a call (demo or production)"""
    if not voice_ai:
        raise HTTPException(status_code=500, detail="Voice AI not initialized")
    
    try:
        call_id = voice_ai.make_outbound_call(request.phone_number)
        return {
            "success": True,
            "call_id": call_id,
            "demo_mode": voice_ai.demo_mode,
            "message": f"{'Demo call simulated' if voice_ai.demo_mode else 'Call initiated'}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Call failed: {str(e)}")

@app.websocket("/ws/call")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for production call audio streaming"""
    if not voice_ai or voice_ai.demo_mode:
        await websocket.close(code=1000, reason="WebSocket only available in production mode")
        return
    
    await websocket.accept()
    call_id = f"ws_call_{id(websocket)}"
    
    # Handle WebSocket communication here
    # (Implementation would be similar to previous examples)
    
    logger.info(f"📞 WebSocket call {call_id} connected")

if __name__ == "__main__":
    print("🚀 Starting Voice AI System...")
    print(f"🎭 Demo Mode: {os.getenv('DEMO_MODE', 'true')}")
    print("🌐 Open: http://localhost:8000")
    print("📖 Check README.md for setup instructions")
    
    uvicorn.run(
        "voice_ai:app",
        host="0.0.0.0",
        port=int(os.getenv('SERVER_PORT', 8000)),
        reload=True,
        log_level="info"
    )