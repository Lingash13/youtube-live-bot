import discord
import asyncio
import os
import feedparser
import requests
import re
import json

TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
PING_ROLE_ID = os.getenv("PING_ROLE_ID")

RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_video_id = None
live_video_id = None


def get_live_status(video_url):
    try:
        r = requests.get(video_url, timeout=10)
        html = r.text

        match = re.search(r"ytInitialPlayerResponse\s*=\s*(\{.+?\});", html)
        if not match:
            return "upload", None

        data = json.loads(match.group(1))

        video_details = data.get("videoDetails", {})
        microformat = data.get("microformat", {})
        player_microformat = microformat.get("playerMicroformatRenderer", {})

        is_live_content = video_details.get("isLiveContent")

        if is_live_content:
            live_details = player_microformat.get("liveBroadcastDetails", {})

            if "endTimestamp" in live_details:
                return "ended", None

            if "startTimestamp" in live_details:
                return "live", live_details.get("startTimestamp")

            if "scheduledStartTimestamp" in live_details:
                return "scheduled", live_details.get("scheduledStartTimestamp")

        return "upload", None

    except:
        return "upload", None


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
                status, start_time = get_live_status(link)

                # NEW VIDEO
                if last_video_id != video_id:
                    last_video_id = video_id

                    # 🟡 SCHEDULED
                    if status == "scheduled":
                        embed = discord.Embed(
                            title="🟡 ⏳ LIVE STREAM SCHEDULED ⏳ 🟡",
                            description=(
                                f"🎮 **{title}**\n\n"
                                f"🚀 Get ready for the battle!\n"
                                f"🕒 Starts At: {start_time}"
                            ),
                            color=0xFFA500,
                            url=link
                        )

                        embed.set_author(
                            name="LK GAMING THENI",
                            icon_url=f"https://img.youtube.com/vi/{video_id}/default.jpg"
                        )

                        embed.set_thumbnail(
                            url=f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                        )

                        embed.set_image(
                            url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                        )

                        embed.add_field(name="⚔ Stream Mode", value="Live Gameplay", inline=False)
                        embed.add_field(name="📡 Status", value="🟡 SCHEDULED", inline=False)
                        embed.add_field(name="🔔 Reminder", value=f"[Set Reminder]({link})", inline=False)

                        embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                        embed.timestamp = discord.utils.utcnow()

                        await channel.send(embed=embed)
                        print("Scheduled sent")

                    # 🔴 LIVE START
                    elif status == "live":
                        live_video_id = video_id

                        embed = discord.Embed(
                            title="🔥 🔴 LIVE STREAM STARTED 🔴 🔥",
                            description=(
                                f"🎮 🔴 **{title}**\n\n"
                                f"🚀 The battle has begun!\n"
                                f"💥 Join now and dominate the stream!"
                            ),
                            color=0xFF0000,
                            url=link
                        )

                        embed.set_author(
                            name="LK GAMING THENI",
                            icon_url=f"https://img.youtube.com/vi/{video_id}/default.jpg"
                        )

                        embed.set_thumbnail(
                            url=f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                        )

                        embed.set_image(
                            url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                        )

                        embed.add_field(name="⚔ Stream Mode", value="Live Gameplay", inline=False)
                        embed.add_field(name="📡 Status", value="🟢 ONLINE", inline=False)
                        embed.add_field(name="🔥 Join Now", value=f"[Click Here To Watch]({link})", inline=False)

                        embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                        embed.timestamp = discord.utils.utcnow()

                        if PING_ROLE_ID:
                            await channel.send(f"<@&{PING_ROLE_ID}>", embed=embed)
                        else:
                            await channel.send(embed=embed)

                        print("Live started sent")

                    # 🎬 NORMAL UPLOAD
                    else:
                        embed = discord.Embed(
                            title="🎬 NEW GAMING VIDEO DROPPED!",
                            description=f"🔥 **{title}**",
                            color=0x0099FF,
                            url=link
                        )

                        embed.set_author(
                            name="LK GAMING THENI",
                            icon_url=f"https://img.youtube.com/vi/{video_id}/default.jpg"
                        )

                        embed.set_thumbnail(
                            url=f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                        )

                        embed.set_image(
                            url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                        )

                        embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                        embed.timestamp = discord.utils.utcnow()

                        await channel.send(embed=embed)
                        print("Upload sent")

                # 🔴 LIVE ENDED
                if live_video_id:
                    current_status, _ = get_live_status(f"https://youtube.com/watch?v={live_video_id}")

                    if current_status == "ended":
                        embed = discord.Embed(
                            title="⛔ 🔴 LIVE STREAM ENDED 🔴 ⛔",
                            description=(
                                "🎮 The battle has ended!\n\n"
                                "🙏 Thanks everyone for joining.\n"
                                "🔥 Stay tuned for next stream!"
                            ),
                            color=0x2F3136
                        )

                        embed.set_author(
                            name="LK GAMING THENI",
                            icon_url=f"https://img.youtube.com/vi/{live_video_id}/default.jpg"
                        )

                        embed.set_thumbnail(
                            url=f"https://img.youtube.com/vi/{live_video_id}/hqdefault.jpg"
                        )

                        embed.set_image(
                            url=f"https://img.youtube.com/vi/{live_video_id}/maxresdefault.jpg"
                        )

                        embed.add_field(name="⚔ Stream Mode", value="Live Gameplay", inline=False)
                        embed.add_field(name="📡 Status", value="🔴 OFFLINE", inline=False)
                        embed.add_field(
                            name="📺 Replay",
                            value=f"[Watch Replay](https://youtube.com/watch?v={live_video_id})",
                            inline=False
                        )

                        embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                        embed.timestamp = discord.utils.utcnow()

                        await channel.send(embed=embed)

                        live_video_id = None
                        print("Live ended sent")

            await asyncio.sleep(120)

        except Exception as e:
            print("ERROR:", e)
            await asyncio.sleep(120)


@client.event
async def on_ready():
    print(f"Bot Online: {client.user}")
    client.loop.create_task(check_youtube())


client.run(TOKEN)
