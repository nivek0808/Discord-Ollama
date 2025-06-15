import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# === Ollama Interaction ===
def call_ollama_chat(model_name, prompt):
    url = "http://192.168.1.190:30068/api/generate"
    payload = {
        "model": model_name,
        "prompt": f"/no_think\n{prompt}",
        "temperature": 0.6,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json().get("response", "No response.")
        if "</think>" in result:
            result = result.split("</think>", 1)[1].strip()
        return result
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
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} - You Better Stop That!")

    await bot.process_commands(message)

# Response Command
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

# Ollama Interaction
@bot.command(name="ask")
async def ask_ollama(ctx, *, prompt: str):
    """Query Ollama Qwen 0.6B with your prompt."""
    await ctx.send("Thinking... 🤖")
    model_name = "qwen3:0.6b"

    result = call_ollama_chat(model_name, prompt)

    if len(result) > 1990:
        result = result[:1990] + "…"

    await ctx.send(f"💬 {result}")

# Leave me at the end!
bot.run(token, log_handler=handler, log_level=logging.DEBUG)