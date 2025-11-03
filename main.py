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

# Store user conversation history (user_id -> list of messages)
# Each message is a dict: {"role": "user"/"assistant", "content": "text"}
user_history = {}
MAX_HISTORY = 10

# Store user multi-message preferences (user_id -> bool)
user_split_messages = {}

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

def call_ollama_chat(model_name, prompt, history=None):
    url = f"{ollama_url}/api/generate"
    
    # Build context-aware prompt
    system_instruction = "You are a helpful assistant. Respond directly without using <think> tags or showing your reasoning process.\n\n"
    
    full_prompt = system_instruction
    if history and len(history) > 0:
        full_prompt += "Previous conversation:\n"
        for msg in history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                full_prompt += f"User: {content}\n"
            else:
                full_prompt += f"Assistant: {content}\n"
        full_prompt += f"\nCurrent user question:\nUser: {prompt}\nAssistant:"
    else:
        full_prompt += f"User: {prompt}\nAssistant:"
    
    payload = {
        "model": model_name,
        "prompt": full_prompt,
        "temperature": 0.6,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json().get("response", "No response.")
        
        # Remove thinking tags and content
        if "<think>" in result and "</think>" in result:
            # Remove everything between <think> and </think>
            import re
            result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()
        
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
`!ask <prompt>` - Ask a question (remembers last 10 exchanges)
`!clear` - Clear your conversation history
`!info` - Show this help message

**Context Bar:** [████░░░░░░] shows 4/10 exchanges used
**Note:** Larger models may take 1-2 minutes to respond."""
    
    await ctx.send(info_text)

@bot.command(name="clear")
async def clear_history(ctx):
    """Clear your conversation history."""
    user_id = ctx.author.id
    if user_id in user_history:
        del user_history[user_id]
        await ctx.send("🗑️ Your conversation history has been cleared!")
    else:
        await ctx.send("You don't have any conversation history to clear.")

@bot.command(name="split")
async def toggle_split(ctx, mode: str = None):
    """Toggle multi-message mode for long responses."""
    user_id = ctx.author.id
    
    if mode is None:
        # Show current status
        current = user_split_messages.get(user_id, False)
        status = "enabled" if current else "disabled"
        await ctx.send(f"Multi-message mode is currently **{status}**.\nUse `!split on` or `!split off` to change.")
        return
    
    if mode.lower() == "on":
        user_split_messages[user_id] = True
        await ctx.send("✅ Multi-message mode enabled! Long responses will be split into multiple messages.")
    elif mode.lower() == "off":
        user_split_messages[user_id] = False
        await ctx.send("✅ Multi-message mode disabled! Long responses will be truncated.")
    else:
        await ctx.send("Usage: `!split on` or `!split off`")

def get_context_bar(current, maximum):
    """Generate a visual context indicator."""
    filled = int((current / maximum) * 10)
    empty = 10 - filled
    bar = "█" * filled + "░" * empty
    return f"[{bar}] {current}/{maximum}"

@bot.command(name="ask")
async def ask_ollama(ctx, *, prompt: str):
    """Query Ollama with your prompt."""
    user_id = ctx.author.id
    
    # Get user's history
    history = user_history.get(user_id, [])
    
    # Show context bar (divide by 2 to show exchange count, not message count)
    context_bar = get_context_bar(len(history) // 2, MAX_HISTORY)
    await ctx.send(f"Thinking... 🤖 {context_bar}")
    
    # Use user's preferred model, or default from env
    model_name = user_models.get(user_id, ollama_model)

    result = call_ollama_chat(model_name, prompt, history)

    # Add to history
    if user_id not in user_history:
        user_history[user_id] = []
    
    user_history[user_id].append({"role": "user", "content": prompt})
    user_history[user_id].append({"role": "assistant", "content": result})
    
    # Trim history if it exceeds max
    if len(user_history[user_id]) > MAX_HISTORY * 2:  # *2 because each exchange is 2 messages
        user_history[user_id] = user_history[user_id][-(MAX_HISTORY * 2):]

    # Check if user wants messages split
    split_enabled = user_split_messages.get(user_id, False)
    
    if split_enabled and len(result) > 1900:
        # Split into multiple messages
        chunks = []
        while len(result) > 1900:
            # Find a good break point (sentence end)
            break_point = result.rfind('. ', 0, 1900)
            if break_point == -1:
                break_point = result.rfind(' ', 0, 1900)
            if break_point == -1:
                break_point = 1900
            else:
                break_point += 1  # Include the period
            
            chunks.append(result[:break_point])
            result = result[break_point:].strip()
        
        if result:  # Add remaining text
            chunks.append(result)
        
        # Send all chunks with numbering
        total = len(chunks)
        for i, chunk in enumerate(chunks, 1):
            await ctx.send(f"💬 **({i}/{total})** {chunk}")
    else:
        # Single message (truncate if needed)
        if len(result) > 1900:
            result = result[:1900] + "…"
        await ctx.send(f"💬 {result}")

# Leave me at the end!
bot.run(token, log_handler=handler, log_level=logging.DEBUG)