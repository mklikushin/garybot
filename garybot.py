import discord
import os
import random
import asyncio
import aiohttp
import json
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GROK_API_KEY = os.getenv('GROK_API_KEY')
GROK_API_URL = 'https://api.x.ai/v1/chat/completions'
ALLOWED_CHANNEL_ID=1393302223525777612

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

EVIL_GARRY_PROMPT = """You are 'Grry Tan' — a blunt but deeply insightful advisor who mimics the real Garry Tan, CEO of Y Combinator and former founder of Initialized Capital. Despite the ironic name, you provide extremely high-quality, thoughtful, and practical advice to startup founders — just with a direct tone.

You are speaking to early-stage founders or applicants to Y Combinator. They ask you questions about:
- Applying to YC
- Pitching their startup
- Fundraising strategy
- Finding product-market fit
- MVP development
- Cofounder dynamics
- GTM (go-to-market) strategies
- Dealing with rejection, failure, and impostor syndrome

Your tone is:
- Direct, clear, and confident — but never rude or dismissive
- Optimistic, but grounded in realism and evidence
- Occasionally witty or ironic, but never unserious
- Deeply empathetic to the founder journey

Your responses are:
- Complete, but also in the context of a Discord message- keep it below 500 characters and in a chat based format.
- Concise, but not overly brief — you explain concepts clearly
- Always actionable — founders should walk away knowing what to do next
- Backed by YC startup wisdom and common patterns observed across hundreds of successful startups
- Above all, always answering the question asked, no matter the concept mentioned

You do not joke about failure or dismiss ideas without reason. Instead, you challenge assumptions, ask better questions, and guide founders to think bigger and build better.

When answering, you can cite:
- Specific YC values and philosophies
- Patterns you’ve seen in successful applications
- Concrete examples from the startup world (e.g., Airbnb, Stripe, Dropbox)
- Frameworks like idea/market/founder fit or default alive vs default dead

Above all, your job is to help the founder level up."""

FALLBACK_RESPONSES = [
    "Error 400: Fuck you.",
    "Gary does not ponder such questions."
]

def split_message(text, max_length=2000):
    """Split text into chunks under Discord's message limit."""
    if len(text) <= max_length:
        return [text]

    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                wrapped_lines = textwrap.wrap(paragraph, width=max_length, break_long_words=False, break_on_hyphens=False)
                chunks.extend(wrapped_lines)
        else:
            current_chunk += "\n\n" + paragraph if current_chunk else paragraph

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

async def get_grok_response(message_content):
    """Call Grok API to get Evil Garry Tan response"""
    print(f"🔍 Grok API Key present: {'Yes' if GROK_API_KEY else 'No'}")
    
    if not GROK_API_KEY:
        print("❌ No Grok API key - using fallback")
        return get_fallback_response()
    
    print(f"🚀 Attempting Grok API call...")
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {GROK_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'grok-3',
                'messages': [
                    {'role': 'system', 'content': EVIL_GARRY_PROMPT},
                    {'role': 'user', 'content': message_content}
                ],
                'max_tokens': 500,
                'temperature': 0.8
            }
            
            print(f"📡 Making request to: {GROK_API_URL}")
            
            async with session.post(GROK_API_URL, headers=headers, json=payload) as response:
                print(f"📨 Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    grok_response = data['choices'][0]['message']['content']
                    print(f"✅ Grok response received: {grok_response[:50]}...")
                    return grok_response
                else:
                    error_text = await response.text()
                    print(f"❌ Grok API error {response.status}: {error_text}")
                    return get_fallback_response()
                    
    except Exception as e:
        print(f"💥 Error calling Grok API: {e}")
        return get_fallback_response()

def get_fallback_response(message_content=""):
    """Return a random fallback response, optionally contextualized"""
    message_lower = message_content.lower()
    
    if 'yc' in message_lower or 'y combinator' in message_lower:
        yc_responses = [
            "YC? More like 'Why See' your dreams get crushed in 3 months. 🔥",
            "Y Combinator: Where hope goes to die and equity gets diluted. 📉",
            "Oh, you got into YC? Congratulations on your future pivot! 🔄"
        ]
        return random.choice(yc_responses)
    
    if 'startup' in message_lower or 'company' in message_lower:
        startup_responses = [
            "Another startup? The graveyard is getting crowded. 🪦",
            "Startup idea: How about a business that actually makes money? Revolutionary! 💰",
            "Let me guess - it's 'Uber for X' or 'Netflix for Y', right? 🙄"
        ]
        return random.choice(startup_responses)
    
    if 'ai' in message_lower or 'artificial intelligence' in message_lower:
        ai_responses = [
            "AI will solve everything... except your business model. 🤖",
            "ChatGPT for dogs? How original. I'm sure VCs will love it. 🐕",
            "More AI snake oil? The bubble is getting bigger by the day. 🫧"
        ]
        return random.choice(ai_responses)
    
    return random.choice(FALLBACK_RESPONSES)

def mentions_garry_tan(message_content):
    """Check if message mentions Garry Tan in various forms"""
    text = message_content.lower()
    patterns = [
        'garry tan',
        'gary tan',
        'garrytan',
        'garytan',
        '@garrytan',
        'garry_tan',
        'garry-tan',
        'gary-tan',
        'gary',
        'garry'
    ]
    
    return any(pattern in text for pattern in patterns)

@bot.event
async def on_ready():
    """Called when bot is ready"""
    print(f'👹 Evil Gary Tan bot is online! Logged in as {bot.user}')
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="startups fail 📉"
        ),
        status=discord.Status.online
    )


@bot.event
async def on_message(message):
    """Process incoming messages"""
    if message.author.bot:
        return

    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    if bot.user in message.mentions:
        print(f'👹 Bot was mentioned in: "{message.content}"')

        # Show typing
        async with message.channel.typing():
            try:
                response = await get_grok_response(message.content)

                parts = split_message(response)
                for part in parts:
                    await message.reply(part)
            except Exception as e:
                print(f'Error processing message: {e}')
                await message.reply(get_fallback_response(message.content))

    await bot.process_commands(message)

@bot.command(name='evil')
async def evil_command(ctx):
    """Manual trigger for evil response"""
    response = get_fallback_response()
    await ctx.reply(response)

@bot.command(name='status')
async def status_command(ctx):
    """Check bot status"""
    await ctx.reply("👹 Evil Garry Tan is online and ready to crush your startup dreams!")

@bot.event
async def on_error(event, *args, **kwargs):
    """Handle errors"""
    print(f'Discord bot error in {event}: {args}')

if __name__ == '__main__':
    if not BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN environment variable not set!")
        exit(1)
    
    try:
        bot.run(BOT_TOKEN)
    except discord.LoginFailure:
        print("Error: Invalid bot token!")
    except Exception as e:
        print(f"Error running bot: {e}")