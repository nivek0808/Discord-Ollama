import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
ollama_model = os.getenv('OLLAMA_MODEL', 'gpt-oss')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Store user model preferences (user_id -> model_name)
user_models = {}

# === Ollama Interaction ===
def get_available_models():
    """Fetch list of available models from Ollama."""
    url = f"{ollama_url}/api/tags"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        models = response.json().get("models", [])
        return models
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []

def call_ollama_chat(model_name, prompt):
    url = f"{ollama_url}/api/generate"
    payload = {
        "model": model_name,
        "prompt": f"/no_think\n{prompt}",
        "temperature": 0.6,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json().get("response", "No response.")
        if "</think>" in result:
            result = result.split("</think>", 1)[1].strip()
        return result
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # Check if it's a vision model
            if "vl" in model_name.lower() or "vision" in model_name.lower():
                return "⚠️ This is a vision model that requires images. Text-only queries are not supported."
            return f"Server error: The model may not support this type of request."
        return f"Error contacting Ollama: {e}"
    except Exception as e:
        print(f"Ollama Error: {e}")
        return f"Error contacting Ollama: {e}"

# === Bot Events & Commands ===

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

# Welcome Message
@bot.event
async def on_member_join(member):
    await member.send(f"Welcome {member.name}")

# Text-Specific Moderator
# Feature removed temporarily

# Response Command
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

# Ollama Interaction
@bot.command(name="models")
async def list_models(ctx):
    """List all available Ollama models."""
    await ctx.send("Fetching available models... 🔍")
    
    models = get_available_models()
    
    if not models:
        await ctx.send("❌ Could not fetch models from Ollama server.")
        return
    
    # Format the model list
    model_list = "**Available Models:**\n\n"
    for model in models:
        name = model.get("name", "unknown")
        size_bytes = model.get("size", 0)
        size_gb = size_bytes / (1024**3)  # Convert to GB
        
        # Check if it's a vision model
        is_vision = "vl" in name.lower() or "vision" in name.lower()
        vision_tag = " 🖼️ (Vision)" if is_vision else ""
        
        model_list += f"• `{name}` ({size_gb:.1f} GB){vision_tag}\n"
    
    # Add current model indicator
    model_list += f"\n**Current model:** `{ollama_model}`"
    
    if len(model_list) > 1990:
        model_list = model_list[:1990] + "…"
    
    await ctx.send(model_list)

@bot.command(name="setmodel")
async def set_model(ctx, model_name: str):
    """Set your preferred Ollama model."""
    # Fetch available models to validate
    models = get_available_models()
    model_names = [m.get("name", "") for m in models]
    
    if model_name not in model_names:
        await ctx.send(f"❌ Model `{model_name}` not found. Use `!models` to see available models.")
        return
    
    # Store user's preference
    user_models[ctx.author.id] = model_name
    await ctx.send(f"✅ Your model is now set to `{model_name}`")

@bot.command(name="info")
async def info(ctx):
    """Show available commands and usage."""
    info_text = """**Bot Commands:**

`!hello` - Get a greeting
`!models` - List all available Ollama models
`!setmodel <name>` - Set your preferred model
`!ask <prompt>` - Ask a question using your model
`!info` - Show this help message

**Note:** Larger models may take 1-2 minutes to respond."""
    
    await ctx.send(info_text)

@bot.command(name="ask")
async def ask_ollama(ctx, *, prompt: str):
    """Query Ollama with your prompt."""
    await ctx.send("Thinking... 🤖")
    
    # Use user's preferred model, or default from env
    model_name = user_models.get(ctx.author.id, ollama_model)

    result = call_ollama_chat(model_name, prompt)

    if len(result) > 1990:
        result = result[:1990] + "…"

    await ctx.send(f"💬 {result}")

# Leave me at the end!
bot.run(token, log_handler=handler, log_level=logging.DEBUG)