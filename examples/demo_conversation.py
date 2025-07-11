#!/usr/bin/env python3
"""
Demo Conversation Example
Test the Voice AI system locally without external dependencies
"""

import os
import sys
import json
import time
import requests
from typing import Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set demo mode
os.environ['DEMO_MODE'] = 'true'

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Voice AI API Endpoints...")
    print("=" * 50)
    
    # Test health check
    print("\n📋 Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data['status']}")
            print(f"🎭 Demo Mode: {data['demo_mode']}")
            print(f"🧩 Components: {data['components']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Server not running. Start with: python src/voice_ai.py")
        return False
    
    # Test demo chat
    print("\n💬 Testing Demo Chat...")
    test_messages = [
        "Hello, I need help with my account",
        "Can you tell me about your services?",
        "I want to cancel my subscription",
        "What are your business hours?",
        "Thank you for your help"
    ]
    
    conversation_id = None
    for i, message in enumerate(test_messages, 1):
        try:
            payload = {"user_input": message}
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            response = requests.post(f"{base_url}/demo/chat", json=payload)
            if response.status_code == 200:
                data = response.json()
                conversation_id = data["conversation_id"]
                
                print(f"\n{i}. 👤 User: {message}")
                print(f"   🤖 AI: {data['ai_response']['message']}")
            else:
                print(f"❌ Chat test {i} failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Chat test {i} error: {e}")
    
    # Test demo call
    print("\n📞 Testing Demo Call...")
    try:
        response = requests.post(f"{base_url}/call", json={
            "phone_number": "+91-DEMO-NUMBER"
        })
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Call initiated: {data['call_id']}")
            print(f"🎭 Demo mode: {data['demo_mode']}")
        else:
            print(f"❌ Call test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Call test error: {e}")
    
    print("\n🎉 Demo testing complete!")
    return True

def interactive_chat():
    """Interactive chat interface"""
    print("\n🎭 Interactive Demo Chat")
    print("=" * 30)
    print("Type 'quit' to exit, 'clear' to start new conversation")
    
    base_url = "http://localhost:8000"
    conversation_id = None
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() in ['clear', 'new', 'reset']:
                conversation_id = None
                print("🆕 Started new conversation")
                continue
            
            if not user_input:
                continue
            
            # Send to API
            payload = {"user_input": user_input}
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            response = requests.post(f"{base_url}/demo/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                conversation_id = data["conversation_id"]
                ai_message = data['ai_response']['message']
                print(f"🤖 AI: {ai_message}")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def performance_test():
    """Test API performance"""
    print("\n⚡ Performance Test")
    print("=" * 20)
    
    base_url = "http://localhost:8000"
    test_messages = [
        "Hello",
        "How are you?",
        "Can you help me?",
        "What services do you offer?",
        "Thank you"
    ]
    
    start_time = time.time()
    successful_requests = 0
    
    for i, message in enumerate(test_messages):
        try:
            request_start = time.time()
            response = requests.post(f"{base_url}/demo/chat", json={
                "user_input": message
            })
            request_time = time.time() - request_start
            
            if response.status_code == 200:
                successful_requests += 1
                print(f"✅ Request {i+1}: {request_time:.2f}s")
            else:
                print(f"❌ Request {i+1}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"❌ Request {i+1}: Error - {e}")
    
    total_time = time.time() - start_time
    
    print(f"\n📊 Performance Results:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Successful: {successful_requests}/{len(test_messages)}")
    print(f"   Average: {total_time/len(test_messages):.2f}s per request")

def check_server_status():
    """Check if server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main demo function"""
    print("🤖 Voice AI Demo Script")
    print("=" * 25)
    
    # Check server status
    if not check_server_status():
        print("❌ Server not running!")
        print("📝 Start the server first:")
        print("   cd voice-ai-local")
        print("   source venv/bin/activate")
        print("   python src/voice_ai.py")
        return
    
    print("✅ Server is running!")
    
    while True:
        print("\n🎯 Demo Options:")
        print("1. 🧪 Test API Endpoints")
        print("2. 💬 Interactive Chat")
        print("3. ⚡ Performance Test") 
        print("4. 🌐 Open Web Interface")
        print("5. ❌ Exit")
        
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                test_api_endpoints()
            elif choice == '2':
                interactive_chat()
            elif choice == '3':
                performance_test()
            elif choice == '4':
                print("🌐 Open: http://localhost:8000")
                import webbrowser
                webbrowser.open("http://localhost:8000")
            elif choice == '5':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please choose 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()