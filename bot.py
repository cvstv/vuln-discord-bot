import feedparser
import discord
import openai
import os
import asyncio

# ENV VARIABLES
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RSS_URL = os.getenv("RSS_URL", "https://www.bleepingcomputer.com/feed/")

# OpenAI Setup
openai.api_key = OPENAI_API_KEY

# Discord Client
intents = discord.Intents.default()
client = discord.Client(intents=intents)
seen_links = set()

async def summarize(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you want
            messages=[{
                "role": "user",
                "content": f"Summarize this vulnerability article in 5 lines or less:\n\n{text}"
            }]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"⚠️ Error generating summary: {e}"

async def check_feed():
    await client.wait_until_ready()
    channel = client.get_channel(DISCORD_CHANNEL_ID)

    while not client.is_closed():
        feed = feedparser.parse(RSS_URL)
        for entry in feed.entries:
            if entry.link not in seen_links:
                seen_links.add(entry.link)
                summary = await summarize(entry.summary)
                msg = f"📣 **New Vulnerability Post**\n🔗 {entry.link}\n🧠 **Summary:**\n{summary}"
                await channel.send(msg)
        await asyncio.sleep(600)  # Check every 10 minutes

@client.event
async def on_ready():
    print(f'Bot connected as {client.user}')
    client.loop.create_task(check_feed())

client.run(DISCORD_TOKEN)
