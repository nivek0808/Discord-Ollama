# 🤖 Discord-Ollama Bot

A powerful Discord bot integrated with Ollama, allowing users to chat with local LLMs directly from Discord. Features include dynamic model switching, conversation history, and user-specific preferences.

## 🚀 Features

*   **AI-Powered Chat:** Query local Ollama models directly from Discord.
*   **Context Awareness:** Optionally remembers the last 10 exchanges (Default: OFF).
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

## 🛠️ Installation & Setup

Follow these steps to get the bot running on your machine.

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
Add the following content (replace `your_discord_token`):
```env
# Discord Bot Token (Required)
DISCORD_TOKEN=your_discord_token_here

# Ollama Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3  # Default fallback model
```

### 4. Set Up Virtual Environment (using `uv`)
We recommend using `uv` for fast package management, but standard `pip` works too.

**Option A: Using `uv` (Recommended)**
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install .
```

**Option B: Using standard `pip`**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

---

## ▶️ Running the Bot

Once everything is set up, start the bot:

```bash
source .venv/bin/activate
python main.py
```

You should see:
> `We are ready to go in, <BotName>`

---

## 🤝 Contributing
Feel free to fork this project, submit PRs, or open issues if you find bugs!