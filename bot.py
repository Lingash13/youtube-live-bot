import discord
import asyncio
import os
from googleapiclient.discovery import build

# -------- ENV VARIABLES -------- #
TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# -------- DISCORD CLIENT -------- #
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# -------- YOUTUBE API -------- #
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# -------- MEMORY TRACKING -------- #
current_live_id = None
announced_upcoming = None


# -------- MAIN CHECK FUNCTION -------- #
async def check_live():
    global current_live_id
    global announced_upcoming

    await client.wait_until_ready()

    while not client.is_closed():
        try:
            channel = client.get_channel(DISCORD_CHANNEL_ID)

            # ---------------- LIVE CHECK ---------------- #
            live_request = youtube.search().list(
                part="snippet",
                channelId=YOUTUBE_CHANNEL_ID,
                type="video",
                eventType="live"
            )
            live_response = live_request.execute()

            if live_response["items"]:
                video = live_response["items"][0]
                video_id = video["id"]["videoId"]

                if current_live_id != video_id:
                    current_live_id = video_id

                    url = f"https://youtube.com/watch?v={video_id}"

                    embed = discord.Embed(
                        title="🔴 LIVE NOW!",
                        description=video["snippet"]["title"],
                        color=discord.Color.red(),
                        url=url
                    )

                    embed.set_image(
                        url=video["snippet"]["thumbnails"]["high"]["url"]
                    )

                    await channel.send(embed=embed)

            else:
                # If previously live but not anymore → Live Ended
                if current_live_id is not None:
                    ended_url = f"https://youtube.com/watch?v={current_live_id}"

                    embed = discord.Embed(
                        title="⛔ LIVE ENDED",
                        description="The live stream has ended.",
                        color=discord.Color.dark_gray(),
                        url=ended_url
                    )

                    await channel.send(embed=embed)

                    current_live_id = None

            # ---------------- UPCOMING CHECK ---------------- #
            upcoming_request = youtube.search().list(
                part="snippet",
                channelId=YOUTUBE_CHANNEL_ID,
                type="video",
                eventType="upcoming"
            )
            upcoming_response = upcoming_request.execute()

            if upcoming_response["items"]:
                video = upcoming_response["items"][0]
                video_id = video["id"]["videoId"]

                if announced_upcoming != video_id:
                    announced_upcoming = video_id

                    url = f"https://youtube.com/watch?v={video_id}"

                    embed = discord.Embed(
                        title="📅 Scheduled Live!",
                        description=video["snippet"]["title"],
                        color=discord.Color.blue(),
                        url=url
                    )

                    embed.set_image(
                        url=video["snippet"]["thumbnails"]["high"]["url"]
                    )

                    await channel.send(embed=embed)

            await asyncio.sleep(120)

        except Exception as e:
            print("Error:", e)
            await asyncio.sleep(120)


# -------- BOT READY EVENT -------- #
@client.event
async def on_ready():
    print(f"Bot Online: {client.user}")
    client.loop.create_task(check_live())


# -------- RUN BOT -------- #
client.run(TOKEN)
