🤖 Discord-Ollama Bot
A Discord bot with dynamic Ollama AI integration, featuring user-specific model preferences and multi-model support.

🚀 Features
AI-Powered Responses - Query Ollama models directly from Discord
Multi-Model Support - Switch between different Ollama models
User Preferences - Each user can set their own preferred model
Model Discovery - List all available models on your Ollama server
User Welcome Messages - Greets new members via DM
Simple Commands - Clean, intuitive command interface
📋 Commands
!hello - Get a friendly greeting
!models - List all available Ollama models with sizes
!setmodel <name> - Set your preferred model
!ask <prompt> - Ask a question using your chosen model
!info - Display help and command usage
🧱 Requirements
Python 3.10+
A running instance of Ollama with models installed
Discord bot token
Required Python packages (see installation)
🔧 Installation
Clone the repository
bash
   git clone https://github.com/nivek0808/Discord-Ollama.git
   cd Discord-Ollama
Create and activate virtual environment
bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
Install dependencies
bash
   pip install -e .
   # Or with uv (faster):
   uv pip install -e .
Configure environment variables Create a .env file in the project root:
env
   DISCORD_TOKEN=your_discord_bot_token_here
   OLLAMA_URL=http://localhost:11434
   OLLAMA_MODEL=gpt-oss:latest
Run the bot
bash
   python main.py
⚙️ Configuration
Environment Variables
DISCORD_TOKEN - Your Discord bot token (required)
OLLAMA_URL - URL to your Ollama server (default: http://localhost:11434)
OLLAMA_MODEL - Default model to use (default: gpt-oss)
Ollama Setup
Ensure Ollama is running and has models installed:

bash
# Check available models
curl http://localhost:11434/api/tags

# Pull a model if needed
ollama pull gpt-oss
