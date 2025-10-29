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

⚙️ Configuration
Environment Variables
DISCORD_TOKEN - Your Discord bot token (required)
OLLAMA_URL - URL to your Ollama server (default: http://localhost:11434)
OLLAMA_MODEL - Default model to use (default: gpt-oss)
