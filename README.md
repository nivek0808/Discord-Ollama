# 🤖 DiscordBot with Ollama Integration

This is a simple Discord bot built with `discord.py`, featuring:
- Basic moderation
- User welcome messages
- Simple command responses
- Integration with a local [Ollama](https://ollama.com) model for AI-powered responses

---

## 🚀 Features

- Greets new members with a DM
- Deletes messages containing banned words
- Responds to `!hello` with a friendly message
- Responds to `!ask <your prompt>` using the Qwen 0.6B model from Ollama (via local API)

---

## 🧱 Requirements

- Python 3.10+
- A running instance of [Ollama](https://ollama.com/) with the `qwen3:0.6b` model available
- A `.env` file containing your Discord bot token