import discord
import asyncio
import os
import feedparser
import requests

TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
PING_ROLE_ID = os.getenv("PING_ROLE_ID")

RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_video_id = None
live_video_id = None


def is_live(video_url):
    try:
        r = requests.get(video_url, timeout=10)
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

                # NEW VIDEO OR LIVE
                if last_video_id != video_id:
                    last_video_id = video_id

                    if is_live(link):
                        live_video_id = video_id

                        embed = discord.Embed(
                            title="🔥 🔴 LIVE STREAM STARTED 🔴 🔥",
                            description=(
                                f"🎮 **{title}**\n\n"
                                f"🚀 The battle has begun!\n"
                                f"💥 Join now and dominate the stream!"
                            ),
                            color=0xFF0000,
                            url=link
                        )

                        embed.set_author(
                            name="LK GAMING THENI",
                            icon_url=f"https://img.youtube.com/vi/{video_id}/default.jpg",
                            url=link
                        )

                        embed.set_image(
                            url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                        )

                        embed.set_thumbnail(
                            url=f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                        )

                        embed.add_field(
                            name="⚔ Stream Mode",
                            value="Live Gameplay",
                            inline=True
                        )

                        embed.add_field(
                            name="📡 Status",
                            value="🟢 ONLINE",
                            inline=True
                        )

                        embed.add_field(
                            name="🔥 Join Now",
                            value=f"[Click Here To Watch]({link})",
                            inline=False
                        )

                        embed.set_footer(
                            text="🎮 Developed by Lingash | Powered by LL Studio"
                        )

                        embed.timestamp = discord.utils.utcnow()

                        if PING_ROLE_ID:
                            await channel.send(f"<@&{PING_ROLE_ID}>", embed=embed)
                        else:
                            await channel.send(embed=embed)

                        print("Live notification sent")

                    else:
                        embed = discord.Embed(
                            title="🎬 NEW GAMING VIDEO DROPPED!",
                            description=(
                                f"🔥 **{title}**\n\n"
                                f"🎮 Ready for another epic video?\n"
                                f"👇 Watch now!"
                            ),
                            color=0x0099FF,
                            url=link
                        )

                        embed.set_author(
                            name="LK GAMING THENI",
                            icon_url=f"https://img.youtube.com/vi/{video_id}/default.jpg",
                            url=link
                        )

                        embed.set_image(
                            url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                        )

                        embed.add_field(
                            name="🎯 Category",
                            value="Gaming",
                            inline=True
                        )

                        embed.add_field(
                            name="📺 Platform",
                            value="YouTube",
                            inline=True
                        )

                        embed.set_footer(
                            text="🎮 Developed by Lingash | Powered by LL Studio"
                        )

                        embed.timestamp = discord.utils.utcnow()

                        await channel.send(embed=embed)
                        print("Upload notification sent")

                # LIVE ENDED CHECK
                if live_video_id:
                    if not is_live(f"https://youtube.com/watch?v={live_video_id}"):

                        embed = discord.Embed(
                            title="⛔ LIVE STREAM ENDED",
                            description="🎮 The battle has ended.\n\nThanks for watching!",
                            color=0x2F3136
                        )

                        embed.set_footer(
                            text="🎮 Developed by Lingash | Powered by LL Studio"
                        )

                        embed.timestamp = discord.utils.utcnow()

                        await channel.send(embed=embed)

                        print("Live ended sent")

                        live_video_id = None

            await asyncio.sleep(900)

        except Exception as e:
            print("ERROR:", e)
            await asyncio.sleep(900)


@client.event
async def on_ready():
    print(f"Bot Online: {client.user}")
    client.loop.create_task(check_youtube())


client.run(TOKEN)
