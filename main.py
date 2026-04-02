from ollama import chat
from ollama import ChatResponse
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="c2!", intents=intents, help_command=None)
temperature = 600 # initial temp
max_tokens = 100 # initial max tokens
model = 'gemma3:270m' # initial model
paused = False

BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", 0))
OWNER_ID = int(os.getenv("OWNER_ID", 0))

# clanky!!!!! // also known as c²
def get_clanker_response(message):
  response: ChatResponse = chat(options={'temperature': temperature, 'num_predict': max_tokens}, model=model, messages=[
    {
      'role': 'user',
      'content': message,
    },
  ])
  return response.message.content

# temperature command
@bot.command()
async def set_temp(ctx, temp):
    global temperature
    print("setting temp to", temp)
    print("------------------------------")
    temperature = int(temp)
    await bot.change_presence(status=discord.Status.idle, activity=discord.CustomActivity(name=f"current temp: {temperature} | current max tokens: {max_tokens} | current model: {model}"))
    await ctx.send(f'set temp to {temperature}!')

@bot.command()
async def get_temp(ctx):
    await ctx.send(f'current temp is {temperature}!')

# max tokens command | admin only
@bot.command()
async def set_max_tokens(ctx, tokens):
    global max_tokens
    if ctx.author.id != OWNER_ID:
        await ctx.send("access denied!")
        return
    print("setting max tokens to", tokens)
    print("------------------------------")
    max_tokens = int(tokens)
    await bot.change_presence(status=discord.Status.idle, activity=discord.CustomActivity(name=f"current temp: {temperature} | current max tokens: {max_tokens} | current model: {model}"))
    await ctx.send(f'set max tokens to {max_tokens}!')

@bot.command()
async def get_max_tokens(ctx):
    await ctx.send(f'current max tokens is {max_tokens}!')

# model command | admin only
@bot.command()
async def set_model(ctx, *, model_name):
    global model
    if ctx.author.id != OWNER_ID:
        await ctx.send("access denied!")
        return
    print("setting model to", model_name)
    print("------------------------------")
    model = model_name
    await bot.change_presence(status=discord.Status.idle, activity=discord.CustomActivity(name=f"current temp: {temperature} | current max tokens: {max_tokens} | current model: {model}"))
    await ctx.send(f'set model to {model}!')

@bot.command()
async def get_model(ctx):
    await ctx.send(f'current model is {model}!')

# pause / resume command | admin only
@bot.command()
async def pause(ctx):
    global paused
    if ctx.author.id != OWNER_ID:
        await ctx.send("access denied!")
        return
    print("pausing bot")
    print("------------------------------")
    await bot.change_presence(status=discord.Status.dnd, activity=discord.CustomActivity(name="paused"))
    await ctx.send("paused!")
    paused = True

@bot.command()
async def resume(ctx):
    global paused
    if ctx.author.id != OWNER_ID:
        await ctx.send("access denied!")
        return
    print("resuming bot")
    print("------------------------------")
    await bot.change_presence(status=discord.Status.idle, activity=discord.CustomActivity(name=f"current temp: {temperature} | current max tokens: {max_tokens} | current model: {model}"))
    await ctx.send("resumed!")
    paused = False

# reset command | admin only
@bot.command()
async def reset(ctx):
    global temperature, max_tokens, model, paused
    if ctx.author.id != OWNER_ID:
        await ctx.send("access denied!")
        return
    print("resetting all settings to default")
    print("------------------------------")
    temperature = 600
    max_tokens = 100
    model = 'gemma3:270m'
    paused = False
    await bot.change_presence(status=discord.Status.idle, activity=discord.CustomActivity(name=f"current temp: {temperature} | current max tokens: {max_tokens} | current model: {model}"))
    await ctx.send("reset all settings to default!")

# stop command | admin only
@bot.command()
async def stop(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("access denied!")
        return
    print("stopping bot")
    print("------------------------------")
    await ctx.send("stopping...")
    await bot.close()

# help command
@bot.command()
async def help(ctx):
    help_message = """
**c² commands:**
`c2!set_temp <temp>` -- set temperature
`c2!get_temp` -- get the current temperature
`c2!get_max_tokens` -- get the current maximum tokens
`c2!get_model` -- get the current model
"""
    await ctx.send(help_message)

# admin help command
@bot.command()
async def ahelp(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("access denied!")
        return
    help_message = """**c² admin commands:**
`c2!set_max_tokens <tokens>` -- set maximum tokens
`c2!set_model <model_name>` -- set model
`c2!pause` -- pause the bot
`c2!resume` -- resume the bot
`c2!reset` -- reset all settings to default
`c2!stop` -- stop the bot
"""
    await ctx.send(help_message)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.CustomActivity(name=f"current temp: {temperature} | current max tokens: {max_tokens} | current model: {model}"))
    print("c² ready")
    print("------------------------------")

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author.id == bot.user.id:
        return
    if message.channel.id != TARGET_CHANNEL_ID:
        return
    if message.content.startswith("c2!"):
        return
    if paused:
        return
    content = message.content
    print("sending message:", content)
    print("current temperature:", temperature)
    response = get_clanker_response(content)
    print("response from model:", response)
    print("------------------------------")
    await message.reply(content=response)

bot.run(BOT_TOKEN)