import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import aiohttp
import re
import json

# --- Configuration ---
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
ollama_model = os.getenv('OLLAMA_MODEL', 'gpt-oss')

DATA_FILE = 'bot_data.json'
MAX_CONTEXT_TOKENS = 4096  # Conservative limit for most models

# --- Logging and Intents ---
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# --- In-Memory Bot Storage ---
# Store user model preferences (user_id -> model_name)
user_models = {}

# Store user conversation history (user_id -> list of messages)
# Each message is a dict: {"role": "user"/"assistant", "content": "text"}
user_history = {}

# Store user multi-message preferences (user_id -> bool)
user_split_messages = {}

# Store user history preference (user_id -> bool)
# Default is False (History OFF)
user_history_enabled = {}

# --- Persistence Functions ---

def save_data():
    """Save bot state to a JSON file."""
    data = {
        "user_models": user_models,
        "user_history": user_history,
        "user_split_messages": user_split_messages,
        "user_history_enabled": user_history_enabled
    }
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")

def load_data():
    """Load bot state from a JSON file."""
    global user_models, user_history, user_split_messages, user_history_enabled
    if not os.path.exists(DATA_FILE):
        print("No data file found. Starting with empty state.")
        return

    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            # Convert string keys back to integers (JSON keys are always strings)
            user_models = {int(k): v for k, v in data.get("user_models", {}).items()}
            user_history = {int(k): v for k, v in data.get("user_history", {}).items()}
            user_split_messages = {int(k): v for k, v in data.get("user_split_messages", {}).items()}
            user_history_enabled = {int(k): v for k, v in data.get("user_history_enabled", {}).items()}
            print("Data loaded successfully.")
    except Exception as e:
        print(f"Error loading data: {e}")

def estimate_tokens(text):
    """Estimate token count (approx 3.5 chars per token)."""
    return len(text) / 3.5

# === Ollama Interaction ===

async def get_available_models():
    """Fetch list of available models from Ollama."""
    url = f"{ollama_url}/api/tags"
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                models = data.get("models", [])
                return models
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []

async def call_ollama_chat(model_name, prompt, history=None):
    """Call the Ollama /api/chat endpoint with conversation history."""
    url = f"{ollama_url}/api/chat"
    
    # Build the messages list
    system_instruction = {
        "role": "system",
        "content": "You are a helpful assistant. Respond directly without using <think> tags or showing your reasoning process."
    }
    
    messages = [system_instruction]
    
    if history:
        messages.extend(history)
        
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.6,
        "stream": False,
        "keep_alive": "15m"  # Keeps the model in memory for 15 mins
    }

    try:
        # Set a long timeout for the request itself
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as session:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                result_json = await response.json()
                
                # Parse the response from the /api/chat structure
                result = result_json.get("message", {}).get("content", "No response.")
        
        # Clean up any potential <think> tags if the model still adds them
        if "<think>" in result and "</think>" in result:
            result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()
        
        return result
    except aiohttp.ClientResponseError as e:
        if e.status == 500:
            if "vl" in model_name.lower() or "vision" in model_name.lower():
                return "⚠️ This is a vision model that requires images. Text-only queries are not supported."
            return f"Server error: The model may not support this type of request."
        return f"Error contacting Ollama: {e.message} (Status: {e.status})"
    except Exception as e:
        print(f"Ollama Error: {e}")
        return f"Error contacting Ollama: {e}"

# === Bot Events & Commands ===

@bot.event
async def on_ready():
    load_data()
    print(f"We are ready to go in, {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome {member.name}")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command(name="models")
async def list_models(ctx):
    """List all available Ollama models."""
    await ctx.send("Fetching available models... 🔍")
    
    models = await get_available_models()
    
    if not models:
        await ctx.send("❌ Could not fetch models from Ollama server.")
        return
    
    # Format the model list
    model_list = "**Available Models:**\n\n"
    for model in models:
        name = model.get("name", "unknown")
        size_bytes = model.get("size", 0)
        size_gb = size_bytes / (1024**3)
        is_vision = "vl" in name.lower() or "vision" in name.lower()
        vision_tag = " 🖼️ (Vision)" if is_vision else ""
        model_list += f"• `{name}` ({size_gb:.1f} GB){vision_tag}\n"
    
    model_list += f"\n**Current model:** `{ollama_model}`"
    
    if len(model_list) > 1990:
        model_list = model_list[:1990] + "…"
    
    await ctx.send(model_list)

@bot.command(name="setmodel")
async def set_model(ctx, model_name: str):
    """Set your preferred Ollama model."""
    models = await get_available_models()
    model_names = [m.get("name", "") for m in models]
    
    if model_name not in model_names:
        await ctx.send(f"❌ Model `{model_name}` not found. Use `!models` to see available models.")
        return
    
    user_models[ctx.author.id] = model_name
    save_data()
    await ctx.send(f"✅ Your model is now set to `{model_name}`")

@bot.command(name="info")
async def info(ctx):
    """Show available commands and usage."""
    info_text = """
**Bot Commands:**

`!hello` - Get a greeting
`!models` - List all available Ollama models
`!setmodel <name>` - Set your preferred model
`!ask <prompt>` - Ask a question
`!history [on/off]` - Enable/Disable conversation history (Default: OFF)
`!clear` - Clear your conversation history
`!split [on/off]` - Toggle long response splitting (Default: ON)
`!info` - Show this help message

**Context Bar:** [████░░░░░░] shows token usage
**Note:** Larger models may take 1-2 minutes to respond."""
    
    await ctx.send(info_text)

@bot.command(name="clear")
async def clear_history(ctx):
    """Clear your conversation history."""
    user_id = ctx.author.id
    if user_id in user_history:
        del user_history[user_id]
        save_data()
        await ctx.send("🗑️ Your conversation history has been cleared!")
    else:
        await ctx.send("You don't have any conversation history to clear.")

@bot.command(name="history")
async def toggle_history(ctx, mode: str = None):
    """Toggle conversation history tracking."""
    user_id = ctx.author.id
    
    if mode is None:
        current = user_history_enabled.get(user_id, False)
        status = "enabled" if current else "disabled"
        await ctx.send(f"Conversation history is currently **{status}**.\nUse `!history on` or `!history off` to change.")
        return

    if mode.lower() == "on":
        user_history_enabled[user_id] = True
        save_data()
        await ctx.send("✅ Conversation history enabled! I will remember context up to 4k tokens.")
    elif mode.lower() == "off":
        user_history_enabled[user_id] = False
        save_data()
        await ctx.send("✅ Conversation history disabled! Each question will be treated independently.")
    else:
        await ctx.send("Usage: `!history on` or `!history off`")

@bot.command(name="split")
async def toggle_split(ctx, mode: str = None):
    """Toggle multi-message mode for long responses."""
    user_id = ctx.author.id
    
    if mode is None:
        # Show current status (default is now True)
        current = user_split_messages.get(user_id, True) 
        status = "enabled" if current else "disabled"
        await ctx.send(f"Multi-message mode is currently **{status}**.\nUse `!split on` or `!split off` to change.")
        return
    
    if mode.lower() == "on":
        user_split_messages[user_id] = True
        save_data()
        await ctx.send("✅ Multi-message mode enabled! Long responses will be split into multiple messages.")
    elif mode.lower() == "off":
        user_split_messages[user_id] = False
        save_data()
        await ctx.send("✅ Multi-message mode disabled! Long responses will be truncated.")
    else:
        await ctx.send("Usage: `!split on` or `!split off`")

def get_context_bar(current_tokens, max_tokens):
    """Generate a visual context indicator based on tokens."""
    filled = int((current_tokens / max_tokens) * 10)
    filled = min(filled, 10) # Clamp to 10
    empty = 10 - filled
    bar = "█" * filled + "░" * empty
    return f"[{bar}] {int(current_tokens)}/{max_tokens} toks"

@bot.command(name="ask")
async def ask_ollama(ctx, *, prompt: str):
    """Query Ollama with your prompt."""
    user_id = ctx.author.id
    
    # Check if history is enabled for this user (Default: False)
    is_history_on = user_history_enabled.get(user_id, False)
    
    context_messages = []
    current_tokens = 0
    prompt_tokens = estimate_tokens(prompt)
    
    if is_history_on:
        full_history = user_history.get(user_id, [])
        
        # Smart Context: Select recent messages that fit in token budget
        # We process in reverse (newest first) to ensure we keep the latest context
        budget = MAX_CONTEXT_TOKENS - prompt_tokens - 500 # Reserve 500 for system prompt + buffer
        
        temp_context = []
        for msg in reversed(full_history):
            msg_tokens = estimate_tokens(msg['content'])
            if current_tokens + msg_tokens <= budget:
                temp_context.append(msg)
                current_tokens += msg_tokens
            else:
                break
        
        context_messages = list(reversed(temp_context))
        
        # Show context bar (History + Current Prompt)
        display_tokens = current_tokens + prompt_tokens
        context_bar = get_context_bar(display_tokens, MAX_CONTEXT_TOKENS)
        status_msg = f"Thinking... 🤖 {context_bar}"
    else:
        status_msg = "Thinking... 🤖 (History: OFF)"

    await ctx.send(status_msg)
    
    model_name = user_models.get(user_id, ollama_model)

    # Call Ollama with the selected context
    result = await call_ollama_chat(model_name, prompt, context_messages)

    # Only update history if enabled
    if is_history_on:
        if user_id not in user_history:
            user_history[user_id] = []
        
        user_history[user_id].append({"role": "user", "content": prompt})
        user_history[user_id].append({"role": "assistant", "content": result})
        
        # Pruning happens at read-time, so we can just append. 
        # But to keep JSON file size sane, we can still hard-limit the stored list
        # to something generous like 50 items.
        if len(user_history[user_id]) > 50:
             user_history[user_id] = user_history[user_id][-50:]
             
        save_data()

    # Check if user wants messages split (default is now True)
    split_enabled = user_split_messages.get(user_id, True) 
    
    if split_enabled and len(result) > 1900:
        # Split into multiple messages
        chunks = []
        while len(result) > 1900:
            # Find a good break point (sentence end or space)
            break_point = result.rfind('. ', 0, 1900)
            if break_point == -1:
                break_point = result.rfind(' ', 0, 1900)
            if break_point == -1: # If no good break point, just cut
                break_point = 1900
            else:
                break_point += 1 # Include the period/space
            
            chunks.append(result[:break_point])
            result = result[break_point:].strip()
        
        if result: # Add remaining text
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

# --- Run the Bot ---
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
