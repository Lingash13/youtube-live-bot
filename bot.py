import discord
import asyncio
import os
import feedparser
import requests
import re
import json
from datetime import datetime

TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
PING_ROLE_ID = os.getenv("PING_ROLE_ID")

RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_video_id = None
live_video_id = None


def format_duration(start, end):
    try:
        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
        delta = end_dt - start_dt

        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"{hours}h {minutes}m {seconds}s"
    except:
        return "Unknown"


def get_live_details(video_url):
    try:
        r = requests.get(video_url, timeout=10)
        html = r.text

        match = re.search(r"ytInitialPlayerResponse\s*=\s*(\{.+?\});", html)
        if not match:
            return "upload", None, None

        data = json.loads(match.group(1))

        video_details = data.get("videoDetails", {})
        microformat = data.get("microformat", {})
        player_microformat = microformat.get("playerMicroformatRenderer", {})

        views = video_details.get("viewCount")
        is_live_content = video_details.get("isLiveContent")

        live_details = player_microformat.get("liveBroadcastDetails", {})

        if is_live_content:
            if "endTimestamp" in live_details:
                start = live_details.get("startTimestamp")
                end = live_details.get("endTimestamp")
                duration = format_duration(start, end) if start and end else "Unknown"
                return "ended", duration, views

            if "startTimestamp" in live_details:
                return "live", None, views

            if "scheduledStartTimestamp" in live_details:
                return "scheduled", live_details.get("scheduledStartTimestamp"), views

        return "upload", None, views

    except:
        return "upload", None, None


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
                status, extra_data, views = get_live_details(link)

                # NEW VIDEO
                if last_video_id != video_id:
                    last_video_id = video_id

                    # SCHEDULED
                    if status == "scheduled":
                        embed = discord.Embed(
                            title="🟡 ⏳ LIVE STREAM SCHEDULED ⏳ 🟡",
                            description=f"🎮 **{title}**\n\n🕒 Starts At: {extra_data}",
                            color=0xFFA500,
                            url=link
                        )

                        embed.set_image(
                            url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                        )

                        embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                        embed.timestamp = discord.utils.utcnow()

                        if PING_ROLE_ID:
                            await channel.send(
                                content=f"<@&{PING_ROLE_ID}>",
                                embed=embed
                            )
                        else:
                            await channel.send(embed=embed)

                    # LIVE START
                    elif status == "live":
                        live_video_id = video_id

                        embed = discord.Embed(
                            title="🔥 🔴 LIVE STREAM STARTED 🔴 🔥",
                            description=f"🎮 **{title}**\n\n🚀 The battle has begun!",
                            color=0xFF0000,
                            url=link
                        )

                        embed.set_image(
                            url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                        )

                        embed.add_field(
                            name="👁 Current Views",
                            value=views if views else "Unknown",
                            inline=True
                        )

                        embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                        embed.timestamp = discord.utils.utcnow()

                        if PING_ROLE_ID:
                            await channel.send(
                                content=f"<@&{PING_ROLE_ID}>",
                                embed=embed
                            )
                        else:
                            await channel.send(embed=embed)

                    # NORMAL UPLOAD
                    else:
                        embed = discord.Embed(
                            title="🎬 NEW VIDEO UPLOADED!",
                            description=f"🎮 **{title}**",
                            color=0x0099FF,
                            url=link
                        )

                        embed.set_image(
                            url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                        )

                        embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                        embed.timestamp = discord.utils.utcnow()

                        await channel.send(embed=embed)

                # LIVE ENDED
                if live_video_id:
                    current_status, duration, views = get_live_details(
                        f"https://youtube.com/watch?v={live_video_id}"
                    )

                    if current_status == "ended":
                        embed = discord.Embed(
                            title="⛔ 🔴 LIVE STREAM ENDED 🔴 ⛔",
                            description="🎮 Thanks for watching!",
                            color=0x2F3136
                        )

                        embed.set_image(
                            url=f"https://img.youtube.com/vi/{live_video_id}/maxresdefault.jpg"
                        )

                        embed.add_field(
                            name="⏱ Duration",
                            value=duration if duration else "Unknown",
                            inline=True
                        )

                        embed.add_field(
                            name="👁 Total Views",
                            value=views if views else "Unknown",
                            inline=True
                        )

                        embed.add_field(
                            name="📺 Replay",
                            value=f"https://youtube.com/watch?v={live_video_id}",
                            inline=False
                        )

                        embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                        embed.timestamp = discord.utils.utcnow()

                        if PING_ROLE_ID:
                            await channel.send(
                                content=f"<@&{PING_ROLE_ID}>",
                                embed=embed
                            )
                        else:
                            await channel.send(embed=embed)

                        live_video_id = None

            await asyncio.sleep(120)

        except Exception as e:
            print("ERROR:", e)
            await asyncio.sleep(120)


@client.event
async def on_ready():
    print(f"Bot Online: {client.user}")
    client.loop.create_task(check_youtube())


client.run(TOKEN)
