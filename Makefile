# Voice AI Local Development Makefile

.PHONY: help setup install run demo test clean deploy health

# Default target
help:
	@echo "🤖 Voice AI Local Development"
	@echo "=============================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup     - Complete project setup"
	@echo "  make install   - Install dependencies"
	@echo "  make env       - Create .env file"
	@echo ""
	@echo "Development:"
	@echo "  make run       - Start server in demo mode"
	@echo "  make demo      - Run interactive demo"
	@echo "  make test      - Run tests"
	@echo "  make health    - Check server health"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean     - Clean up files"
	@echo "  make format    - Format code"
	@echo "  make lint      - Lint code"
	@echo ""
	@echo "Production:"
	@echo "  make prod      - Run in production mode"
	@echo "  make deploy    - Deploy to server"

# Complete setup
setup: install env models
	@echo "✅ Setup complete! Run 'make run' to start."

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	@echo "✅ Dependencies installed"

# Create environment file
env:
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file..."; \
		cp .env.example .env; \
		echo "✅ .env created from template"; \
		echo "💡 Edit .env to configure for production"; \
	else \
		echo "✅ .env already exists"; \
	fi

# Download AI models
models:
	@echo "🧠 Downloading AI models..."
	@. venv/bin/activate && python -c "import whisper; whisper.load_model('base'); print('✅ Whisper ready')" 2>/dev/null || echo "⚠️  Whisper download skipped"
	@. venv/bin/activate && python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; AutoTokenizer.from_pretrained('microsoft/DialoGPT-medium'); AutoModelForCausalLM.from_pretrained('microsoft/DialoGPT-medium'); print('✅ LLM ready')" 2>/dev/null || echo "⚠️  LLM download skipped"

# Run in demo mode
run:
	@echo "🚀 Starting Voice AI in demo mode..."
	@echo "🌐 Open: http://localhost:8000"
	. venv/bin/activate && DEMO_MODE=true python src/voice_ai.py

# Run in production mode
prod:
	@echo "🚀 Starting Voice AI in production mode..."
	@echo "⚠️  Make sure Plivo credentials are configured in .env"
	. venv/bin/activate && DEMO_MODE=false python src/voice_ai.py

# Interactive demo
demo:
	@echo "🎭 Starting interactive demo..."
	. venv/bin/activate && python examples/demo_conversation.py

# Run tests
test:
	@echo "🧪 Running tests..."
	. venv/bin/activate && python -m pytest tests/ -v

# Check server health
health:
	@echo "🏥 Checking server health..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "❌ Server not responding"

# Format code
format:
	@echo "🎨 Formatting code..."
	. venv/bin/activate && black src/ tests/ examples/ --line-length 88

# Lint code
lint:
	@echo "🔍 Linting code..."
	. venv/bin/activate && flake8 src/ tests/ examples/ --max-line-length 88

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ htmlcov/ 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Quick start (for first time users)
quickstart:
	@echo "🚀 Quick Start Setup"
	@echo "===================="
	@echo "1. Installing dependencies..."
	@make install
	@echo ""
	@echo "2. Creating environment..."
	@make env
	@echo ""
	@echo "3. Downloading models (this may take a few minutes)..."
	@make models
	@echo ""
	@echo "🎉 Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  make run    - Start the server"
	@echo "  make demo   - Try interactive demo"
	@echo "  make test   - Run tests"

# Development server with auto-reload
dev:
	@echo "🔥 Starting development server with auto-reload..."
	. venv/bin/activate && DEMO_MODE=true uvicorn src.voice_ai:app --reload --host 0.0.0.0 --port 8000

# Check Python and system requirements
check:
	@echo "🔍 Checking system requirements..."
	@python3 --version | grep -E "3\.(9|10|11|12)" || (echo "❌ Python 3.9+ required" && exit 1)
	@which brew >/dev/null || (echo "⚠️  Homebrew not found (recommended for macOS)")
	@which git >/dev/null || (echo "❌ Git required" && exit 1)
	@echo "✅ System requirements OK"

# Show project status
status:
	@echo "📊 Project Status"
	@echo "================="
	@echo "Python version: $(shell python3 --version 2>/dev/null || echo 'Not found')"
	@echo "Virtual env: $(shell test -d venv && echo 'Created' || echo 'Missing')"
	@echo "Dependencies: $(shell test -f venv/bin/pip && echo 'Installed' || echo 'Missing')"
	@echo "Environment: $(shell test -f .env && echo 'Configured' || echo 'Missing')"
	@echo "Server status: $(shell curl -s http://localhost:8000/health >/dev/null 2>&1 && echo 'Running' || echo 'Stopped')"

# Install system dependencies (macOS)
install-deps-mac:
	@echo "🍎 Installing macOS system dependencies..."
	@which brew >/dev/null || /bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
	brew install python@3.11 git ffmpeg portaudio
	@echo "✅ System dependencies installed"

# Install system dependencies (Ubuntu/Debian)
install-deps-linux:
	@echo "🐧 Installing Linux system dependencies..."
	sudo apt update
	sudo apt install -y python3 python3-pip python3-venv git ffmpeg portaudio19-dev
	@echo "✅ System dependencies installed"

# Deploy to production server
deploy:
	@echo "🚀 Deploying to production..."
	@echo "⚠️  This requires SSH access to your server"
	@echo "📝 Edit this target in Makefile for your server details"
	# rsync -av --exclude='.git' --exclude='venv' --exclude='*.log' . user@server:/path/to/voice-ai/
	# ssh user@server 'cd /path/to/voice-ai && make setup && sudo systemctl restart voice-ai'

# Show logs
logs:
	@echo "📋 Recent logs..."
	@tail -n 50 logs/voice_ai.log 2>/dev/null || echo "No logs found"

# Create directories
dirs:
	@mkdir -p logs src tests examples docs configs
	@echo "✅ Directories created"

# Full development setup
dev-setup: check install-deps-mac install env models
	@echo "🎉 Development setup complete!"
	@make status