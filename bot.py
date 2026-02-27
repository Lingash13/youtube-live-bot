import discord
import asyncio
import os
import feedparser
import requests

TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

PING_ROLE_ID = os.getenv("PING_ROLE_ID")  # optional

RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_video_id = None
live_video_id = None


def is_live(video_url):
    try:
        r = requests.get(video_url)
        return "isLiveNow" in r.text
    except:
        return False


async def check_youtube():
    global last_video_id
    global live_video_id

    await client.wait_until_ready()

    while not client.is_closed():
        try:
            print("Checking RSS...")

            feed = feedparser.parse(RSS_URL)

            if feed.entries:
                latest = feed.entries[0]
                video_id = latest.yt_videoid
                title = latest.title
                link = latest.link

                channel = await client.fetch_channel(DISCORD_CHANNEL_ID)

                # NEW VIDEO DETECTED
                if last_video_id != video_id:
                    last_video_id = video_id

                    if is_live(link):
                        live_video_id = video_id

                        embed = discord.Embed(
                            title="🔴 LIVE NOW!",
                            description=title,
                            color=discord.Color.red(),
                            url=link
                        )

                        embed.set_image(
                            url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                        )

                        if PING_ROLE_ID:
                            await channel.send(f"<@&{PING_ROLE_ID}>", embed=embed)
                        else:
                            await channel.send(embed=embed)

                        print("Live notification sent")

                    else:
                        embed = discord.Embed(
                            title="🎬 New Upload!",
                            description=title,
                            color=discord.Color.blue(),
                            url=link
                        )

                        embed.set_image(
                            url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                        )

                        await channel.send(embed=embed)
                        print("Upload notification sent")

                # CHECK LIVE ENDED
                if live_video_id:
                    if not is_live(f"https://youtube.com/watch?v={live_video_id}"):
                        embed = discord.Embed(
                            title="⛔ LIVE ENDED",
                            description="The stream has ended.",
                            color=discord.Color.dark_gray()
                        )

                        await channel.send(embed=embed)
                        print("Live ended sent")

                        live_video_id = None

            await asyncio.sleep(900)  # 15 minutes

        except Exception as e:
            print("ERROR:", e)
            await asyncio.sleep(900)


@client.event
async def on_ready():
    print(f"Bot Online: {client.user}")
    client.loop.create_task(check_youtube())


client.run(TOKEN)
