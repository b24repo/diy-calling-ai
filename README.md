# 🤖 Voice AI System

A complete Voice AI system for making intelligent phone calls to Indian numbers. Supports both **local testing (demo mode)** and **production deployment** with Plivo integration.

![Demo](https://img.shields.io/badge/Demo-Available-green)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-blue)
![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

## ✨ Features

- 🎭 **Demo Mode**: Test locally without external APIs
- 📞 **Production Calls**: Real phone calls via Plivo
- 🧠 **AI Conversations**: Natural language processing with LLM
- 🎤 **Speech Recognition**: Whisper-based speech-to-text
- 🔊 **Text-to-Speech**: Natural voice responses
- 🌐 **Web Interface**: Interactive demo chat
- 📊 **Real-time Monitoring**: Call logs and analytics
- 🔒 **Secure**: Environment-based configuration

## 🚀 Quick Start (Demo Mode)

Get started in 5 minutes without any external accounts:

```bash
# Clone the repository
git clone <your-repo-url>
cd voice-ai-local

# Set up Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Start in demo mode (default)
python src/voice_ai.py
```

Open [http://localhost:8000](http://localhost:8000) to access the demo interface!

## 🎭 Demo Mode Features

Demo mode allows you to test the entire system locally:

- ✅ **Interactive Chat Interface**: Web-based conversation testing
- ✅ **Mock Audio Processing**: Simulated speech recognition
- ✅ **AI Conversations**: Real or mock LLM responses
- ✅ **API Testing**: All endpoints work without external services
- ✅ **No External Dependencies**: Test without Plivo, OpenAI, etc.

### Demo Commands

```bash
# Health check
curl http://localhost:8000/health

# Demo conversation
curl -X POST http://localhost:8000/demo/chat \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Hello, I need help with my account"}'

# Simulate phone call
curl -X POST http://localhost:8000/call \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+91-DEMO-NUMBER"}'
```

## 📋 Prerequisites

### For Demo Mode (Local Testing)
- **Python 3.9+**
- **macOS/Linux** (Windows with WSL)
- **4GB+ RAM** (for AI models)

### For Production Mode
- All demo requirements plus:
- **Plivo Account** with Indian phone number
- **Public server** or ngrok for webhooks
- **Domain/SSL** (recommended)

## 🛠️ Installation

### 1. System Dependencies (macOS)

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install system packages
brew install python@3.11 git ffmpeg portaudio

# Install Xcode command line tools
xcode-select --install
```

### 2. Python Environment

```bash
# Clone repository
git clone <your-repo-url>
cd voice-ai-local

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (optional for demo)
nano .env
```

### 4. Download AI Models (Optional)

```bash
# Download models for better responses
python -c "
import whisper
import transformers
print('Downloading Whisper...')
whisper.load_model('base')
print('Downloading LLM...')
transformers.AutoTokenizer.from_pretrained('microsoft/DialoGPT-medium')
transformers.AutoModelForCausalLM.from_pretrained('microsoft/DialoGPT-medium')
print('Models ready!')
"
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DEMO_MODE` | Enable demo mode | `true` | No |
| `PLIVO_AUTH_ID` | Plivo authentication ID | - | Production |
| `PLIVO_AUTH_TOKEN` | Plivo authentication token | - | Production |
| `PLIVO_PHONE_NUMBER` | Your Plivo Indian number | - | Production |
| `SERVER_PORT` | Server port | `8000` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

### Demo Mode Settings

```bash
# Enable demo mode (default)
DEMO_MODE=true

# Enable real TTS in demo
DEMO_ENABLE_TTS=true

# Auto-respond in demo
DEMO_AUTO_RESPOND=true
```

### Production Mode Settings

```bash
# Disable demo mode
DEMO_MODE=false

# Plivo credentials
PLIVO_AUTH_ID=your_auth_id
PLIVO_AUTH_TOKEN=your_auth_token
PLIVO_PHONE_NUMBER=+91XXXXXXXXXX

# Public URL for webhooks
PUBLIC_URL=https://your-domain.com
```

## 🎯 Usage

### Demo Mode

1. **Start the server:**
   ```bash
   python src/voice_ai.py
   ```

2. **Open web interface:**
   - Go to [http://localhost:8000](http://localhost:8000)
   - Use the chat interface to test conversations

3. **Test API endpoints:**
   ```bash
   # Test conversation
   curl -X POST http://localhost:8000/demo/chat \
     -H "Content-Type: application/json" \
     -d '{"user_input": "Hi there!"}'
   ```

### Production Mode

1. **Set up Plivo account:**
   - Sign up at [plivo.com](https://plivo.com)
   - Complete KYC verification
   - Purchase Indian phone number
   - Get Auth ID and Token

2. **Configure environment:**
   ```bash
   # Update .env file
   DEMO_MODE=false
   PLIVO_AUTH_ID=your_auth_id
   PLIVO_AUTH_TOKEN=your_auth_token
   PLIVO_PHONE_NUMBER=+91XXXXXXXXXX
   ```

3. **Set up public access:**
   ```bash
   # Option 1: Use ngrok for testing
   brew install ngrok
   ngrok http 8000
   # Update PUBLIC_URL in .env with ngrok URL
   
   # Option 2: Deploy to cloud server
   # Set up proper domain and SSL
   ```

4. **Make production calls:**
   ```bash
   curl -X POST http://localhost:8000/call \
     -H "Content-Type: application/json" \
     -d '{"phone_number": "+919876543210"}'
   ```

## 🏗️ Project Structure

```
voice-ai-local/
├── src/
│   ├── voice_ai.py          # Main application
│   ├── models/              # AI models storage
│   └── utils/               # Utility functions
├── tests/
│   ├── test_demo.py         # Demo mode tests
│   └── test_production.py   # Production tests
├── docs/
│   ├── API.md               # API documentation
│   └── DEPLOYMENT.md        # Deployment guide
├── examples/
│   ├── demo_conversation.py # Demo examples
│   └── production_call.py   # Production examples
├── logs/                    # Log files
├── .env.example            # Environment template
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🧪 Testing

### Demo Tests

```bash
# Run demo mode tests
python -m pytest tests/test_demo.py -v

# Test conversation flow
python examples/demo_conversation.py

# Test all endpoints
python tests/test_endpoints.py
```

### Production Tests

```bash
# Test Plivo connection
python -c "
from src.voice_ai import VoiceAI
import os
os.environ['DEMO_MODE'] = 'false'
ai = VoiceAI()
print('Plivo connection: OK')
"

# Test production call (be careful!)
python examples/production_call.py
```

## 💰 Cost Analysis

### Demo Mode
- **Cost**: **FREE** ✅
- **Usage**: Unlimited local testing
- **Features**: Full AI conversation testing

### Production Mode (2-minute call)
- **Plivo Platform**: ₹0.40/minute
- **Server costs**: ~₹0.01/minute
- **Total**: **₹0.82** (~$0.01) per 2-minute call

### Comparison with Alternatives

| Solution | 2-min Cost | Local Testing | Setup Time |
|----------|------------|---------------|------------|
| **This Project** | ₹0.82 | ✅ Free | 5 minutes |
| UltraVox + Plivo | ₹15+ | ❌ | 1 hour |
| Vapi.ai | ₹30+ | ❌ | 2 hours |
| Custom from scratch | ₹0.80 | ❌ | 40+ hours |

## 🚀 Deployment

### Local Development
```bash
# Run with hot reload
python src/voice_ai.py
```

### Production Deployment

1. **Cloud Server Setup:**
   ```bash
   # Ubuntu/Debian server
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3 python3-pip nginx certbot -y
   
   # Clone and setup project
   git clone <your-repo>
   cd voice-ai-local
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Nginx Configuration:**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /ws/ {
           proxy_pass http://127.0.0.1:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

3. **SSL Certificate:**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

4. **Systemd Service:**
   ```bash
   # Create service file
   sudo nano /etc/systemd/system/voice-ai.service
   
   # Enable and start
   sudo systemctl enable voice-ai
   sudo systemctl start voice-ai
   ```

## 🔧 Troubleshooting

### Common Issues

#### "Models not loading"
```bash
# Clear model cache and redownload
rm -rf ~/.cache/huggingface/
rm -rf ~/.cache/whisper/
python -c "import whisper; whisper.load_model('base')"
```

#### "Port already in use"
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
export SERVER_PORT=8001
python src/voice_ai.py
```

#### "Audio not working on macOS"
```bash
# Install audio dependencies
brew install portaudio
pip install --force-reinstall pyaudio
```

#### "Plivo authentication failed"
```bash
# Test credentials
python -c "
from plivo import RestClient
client = RestClient('your_auth_id', 'your_auth_token')
print(client.accounts.get().name)
"
```

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG
python src/voice_ai.py
```

## 📚 API Documentation

### Health Check
```http
GET /health
```

### Demo Chat
```http
POST /demo/chat
Content-Type: application/json

{
  "user_input": "Hello, I need help",
  "conversation_id": "optional-id"
}
```

### Make Call
```http
POST /call
Content-Type: application/json

{
  "phone_number": "+91XXXXXXXXXX",
  "message": "Optional custom message"
}
```

### WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/call');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Create Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install black flake8 pytest

# Run formatting
black src/
flake8 src/

# Run tests
pytest tests/ -v
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Whisper** by OpenAI for speech recognition
- **Transformers** by Hugging Face for language models
- **Plivo** for telephony services
- **FastAPI** for web framework

## 📞 Support

- 📧 **Email**: your-email@example.com
- 💬 **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 **Docs**: [Full Documentation](https://your-docs-site.com)

## 🗺️ Roadmap

- [ ] **v1.1**: Multi-language support
- [ ] **v1.2**: Advanced conversation flows
- [ ] **v1.3**: CRM integrations
- [ ] **v1.4**: Call analytics dashboard
- [ ] **v1.5**: Mobile app support

---

⭐ **Star this repository** if you find it helpful!

🔔 **Watch for updates** and new features!