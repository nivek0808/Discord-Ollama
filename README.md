# 🤖 Discord-Ollama Bot

A powerful Discord bot integrated with Ollama, allowing users to chat with local LLMs directly from Discord. Features include dynamic model switching, conversation history, and user-specific preferences.

## 🚀 Features

*   **AI-Powered Chat:** Query local Ollama models directly from Discord.
*   **Context Awareness:** Optionally remembers the last ~4000 tokens of conversation (Default: OFF).
*   **Multi-Model Support:** Users can switch between any available model on the server.
*   **Smart Formatting:** Automatically splits long AI responses into multiple Discord messages.
*   **User Preferences:** Remembers which model each user prefers.
*   **Async Performance:** Built with `aiohttp` for non-blocking, fast responses.

---

## 📋 Commands

| Command | Description |
| :--- | :--- |
| `!ask <prompt>` | Ask a question to your selected AI model. |
| `!models` | List all available models on the Ollama server (shows size & vision support). |
| `!setmodel <name>` | Set your preferred model (e.g., `!setmodel llama3`). |
| `!history [on/off]` | Toggle conversation history (Default: OFF). |
| `!clear` | Clear your conversation history with the bot. |
| `!split [on/off]` | Toggle automatic splitting of long messages (Default: ON). |
| `!hello` | Get a simple greeting to test connection. |
| `!info` | Display a help menu with all commands. |

---

## 🐳 Docker Deployment (Recommended)

You can easily deploy this bot using Docker or Dockge.

### 1. Requirements
*   A running instance of [Ollama](https://ollama.com/) (accessible via network).

### 2. Docker Compose
Create a `compose.yaml` file:

```yaml
version: '3.8'

services:
  discord-ollama:
    image: your-dockerhub-username/discord-ollama:latest # Or build locally
    container_name: discord-ollama
    restart: unless-stopped
    volumes:
      - ./bot_data.json:/app/bot_data.json # Persist user data
    environment:
      - DISCORD_TOKEN=your_token_here
      - OLLAMA_URL=http://host.docker.internal:11434 # Point to your Ollama instance
      - OLLAMA_MODEL=llama3
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

### 3. Build & Push (If hosting on DockerHub)
```bash
docker build -t your-username/discord-ollama .
docker push your-username/discord-ollama
```

---

## 🛠️ Manual Installation & Setup

### 1. Prerequisites
*   **Python 3.11+**
*   **Ollama** running locally or on a network server.
*   **Git**

### 2. Clone the Repository
```bash
git clone <your-repo-url>
cd Discord-Ollama
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```bash
touch .env
```
Add the following content:
```env
DISCORD_TOKEN=your_token_here
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### 4. Install Dependencies
```bash
# Using uv (Recommended)
uv venv && source .venv/bin/activate
uv pip install .

# Or using pip
python3 -m venv .venv && source .venv/bin/activate
pip install .
```

### 5. Run
```bash
python main.py
```
