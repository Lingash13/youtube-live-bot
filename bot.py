import os
import discord
import asyncio
from discord.ext import tasks
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

last_status = None
last_video_id = None


async def check_youtube_status():
    global last_status, last_video_id

    request = youtube.search().list(
        part="snippet",
        channelId=CHANNEL_ID,
        eventType="live",
        type="video"
    )
    response = request.execute()

    channel = client.get_channel(DISCORD_CHANNEL_ID)

    # 🔴 LIVE DETECTED
    if response["items"]:
        video = response["items"][0]
        video_id = video["id"]["videoId"]
        title = video["snippet"]["title"]
        thumbnail = video["snippet"]["thumbnails"]["high"]["url"]
        url = f"https://www.youtube.com/watch?v={video_id}"

        if last_status != "live":
            last_status = "live"
            last_video_id = video_id

            embed = discord.Embed(
                title="🔥 LIVE STREAM STARTED 🔴",
                description=f"🚀 **{title}**\n\nClick below to watch now!",
                color=discord.Color.red()
            )
            embed.set_image(url=thumbnail)
            embed.add_field(name="🎮 Stream Mode", value="Live Gameplay", inline=True)
            embed.add_field(name="📡 Status", value="🟢 ONLINE", inline=True)
            embed.add_field(name="🔥 Join Now", value=f"[Click Here To Watch]({url})", inline=False)
            embed.set_footer(text="LK Gaming Theni | Powered by LL Studio")

            await channel.send(embed=embed)

    else:
        if last_status == "live":
            last_status = "ended"

            embed = discord.Embed(
                title="📴 LIVE STREAM ENDED",
                description="Thanks for watching ❤️\nSee you in the next stream!",
                color=discord.Color.greyple()
            )
            embed.set_footer(text="LK Gaming Theni")

            await channel.send(embed=embed)


async def check_scheduled_stream():
    request = youtube.search().list(
        part="snippet",
        channelId=CHANNEL_ID,
        eventType="upcoming",
        type="video"
    )
    response = request.execute()

    channel = client.get_channel(DISCORD_CHANNEL_ID)

    if response["items"]:
        video = response["items"][0]
        title = video["snippet"]["title"]
        thumbnail = video["snippet"]["thumbnails"]["high"]["url"]
        video_id = video["id"]["videoId"]
        url = f"https://www.youtube.com/watch?v={video_id}"

        embed = discord.Embed(
            title="🗓 UPCOMING LIVE STREAM",
            description=f"🎉 **{title}**\n\nStay tuned 🔔",
            color=discord.Color.blue()
        )
        embed.set_image(url=thumbnail)
        embed.add_field(name="⏳ Status", value="Scheduled", inline=True)
        embed.add_field(name="🔔 Reminder", value="Don't miss it!", inline=True)
        embed.add_field(name="▶ Watch Link", value=f"[View Stream]({url})", inline=False)
        embed.set_footer(text="LK Gaming Theni | Road To 15K 🔥")

        await channel.send(embed=embed)


@tasks.loop(minutes=2)
async def background_task():
    await check_scheduled_stream()
    await check_youtube_status()


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    background_task.start()


client.run(DISCORD_TOKEN)
