import discord
import asyncio
import os
from googleapiclient.discovery import build

TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

last_video = None


async def check_live():
    global last_video
    await client.wait_until_ready()

    while not client.is_closed():
        request = youtube.search().list(
            part="snippet",
            channelId=YOUTUBE_CHANNEL_ID,
            eventType="live",
            type="video"
        )
        response = request.execute()

        if response["items"]:
            video = response["items"][0]
            video_id = video["id"]["videoId"]

            if video_id != last_video:
                last_video = video_id

                channel = client.get_channel(DISCORD_CHANNEL_ID)
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

        await asyncio.sleep(120)


@client.event
async def on_ready():
    print(f"Bot Online: {client.user}")
    client.loop.create_task(check_live())


client.run(TOKEN)
