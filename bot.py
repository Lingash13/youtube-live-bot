import os
import discord
from discord.ext import tasks
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ===============================
# ENV VARIABLES (Railway Settings)
# ===============================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# ===============================
# DISCORD SETUP
# ===============================

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# ===============================
# YOUTUBE API SETUP
# ===============================

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

last_status = None  # Track live status


# ===============================
# BACKGROUND LIVE CHECK (LOW QUOTA)
# ===============================

@tasks.loop(minutes=10)
async def check_live_stream():
    global last_status

    try:
        request = youtube.search().list(
            part="snippet",
            channelId=CHANNEL_ID,
            eventType="live",
            type="video"
        )

        response = request.execute()

        channel = client.get_channel(DISCORD_CHANNEL_ID)

        if not channel:
            print("❌ Discord channel not found.")
            return

        # ===============================
        # IF LIVE STREAM FOUND
        # ===============================
        if response.get("items"):
            video = response["items"][0]
            video_id = video["id"]["videoId"]
            title = video["snippet"]["title"]
            thumbnail = video["snippet"]["thumbnails"]["high"]["url"]
            url = f"https://www.youtube.com/watch?v={video_id}"

            if last_status != "live":
                last_status = "live"

                embed = discord.Embed(
                    title="🔥 LIVE STREAM STARTED 🔴",
                    description=f"🚀 **{title}**\n\nClick below to watch now!",
                    color=discord.Color.red()
                )

                embed.set_image(url=thumbnail)
                embed.add_field(name="📡 Status", value="🟢 ONLINE", inline=True)
                embed.add_field(name="🎮 Stream Mode", value="Live Gameplay", inline=True)
                embed.add_field(name="🔥 Watch Now", value=f"[Click Here]({url})", inline=False)
                embed.set_footer(text="LK Gaming Theni | Powered by LL Studio")

                await channel.send(embed=embed)
                print("✅ Live stream notification sent.")

        # ===============================
        # IF STREAM ENDED
        # ===============================
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
                print("🔔 Live ended notification sent.")

    except HttpError as e:
        print("YouTube API Error:", e)
    except Exception as e:
        print("General Error:", e)


# ===============================
# BOT READY EVENT
# ===============================

@client.event
async def on_ready():
    print(f"🤖 Logged in as {client.user}")
    check_live_stream.start()


# ===============================
# RUN BOT
# ===============================

client.run(DISCORD_TOKEN)
