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


# ------------------------------------------------
# 🔴 LIVE CHECK (Railway Stable - With Headers)
# ------------------------------------------------
def check_if_live(channel_id):
    try:
        url = f"https://www.youtube.com/channel/{channel_id}/live"

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9"
        }

        r = requests.get(
            url,
            headers=headers,
            allow_redirects=True,
            timeout=10
        )

        print("Requested URL:", url)
        print("Final URL:", r.url)

        if "/watch?v=" in r.url:
            video_id = r.url.split("v=")[1].split("&")[0]
            return True, video_id

        return False, None

    except Exception as e:
        print("Live check error:", e)
        return False, None


# ------------------------------------------------
# MAIN LOOP
# ------------------------------------------------
async def check_youtube():
    global last_video_id
    global live_video_id

    await client.wait_until_ready()

    while not client.is_closed():
        try:
            print("Checking YouTube status...")

            channel = await client.fetch_channel(DISCORD_CHANNEL_ID)

            # -----------------------------
            # 🔴 LIVE CHECK
            # -----------------------------
            is_live, current_live_id = check_if_live(YOUTUBE_CHANNEL_ID)

            print("Is Live:", is_live)
            print("Current Live ID:", current_live_id)

            # LIVE START
            if is_live and live_video_id != current_live_id:
                live_video_id = current_live_id
                link = f"https://youtube.com/watch?v={current_live_id}"

                embed = discord.Embed(
                    title="🔥 🔴 LIVE STREAM STARTED 🔴 🔥",
                    description="🚀 The battle has begun!\n💥 Join now and dominate the stream!",
                    color=0xFF0000,
                    url=link
                )

                embed.add_field(name="📡 Status", value="🟢 ONLINE", inline=False)
                embed.add_field(name="🔥 Join Now", value=f"[Click Here To Watch]({link})", inline=False)

                embed.set_image(
                    url=f"https://img.youtube.com/vi/{current_live_id}/maxresdefault.jpg"
                )

                embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                embed.timestamp = discord.utils.utcnow()

                if PING_ROLE_ID:
                    await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                else:
                    await channel.send(embed=embed)

                print("Live started notification sent")

            # LIVE ENDED
            if not is_live and live_video_id:
                embed = discord.Embed(
                    title="⛔ 🔴 LIVE STREAM ENDED 🔴 ⛔",
                    description="🎮 Thanks for watching!",
                    color=0x2F3136
                )

                embed.add_field(name="📡 Status", value="🔴 OFFLINE", inline=False)
                embed.add_field(
                    name="📺 Replay",
                    value=f"https://youtube.com/watch?v={live_video_id}",
                    inline=False
                )

                embed.set_image(
                    url=f"https://img.youtube.com/vi/{live_video_id}/maxresdefault.jpg"
                )

                embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                embed.timestamp = discord.utils.utcnow()

                if PING_ROLE_ID:
                    await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                else:
                    await channel.send(embed=embed)

                print("Live ended notification sent")
                live_video_id = None

            # -----------------------------
            # 🎬 UPLOAD CHECK (RSS)
            # -----------------------------
            feed = feedparser.parse(RSS_URL)

            if feed.entries:
                latest = feed.entries[0]
                video_id = latest.yt_videoid
                title = latest.title
                link = latest.link

                if last_video_id != video_id:
                    last_video_id = video_id

                    embed = discord.Embed(
                        title="🎬 🔥 NEW VIDEO DROPPED 🔥 🎬",
                        description=f"🎮 **{title}**",
                        color=0x0099FF,
                        url=link
                    )

                    embed.add_field(name="📡 Status", value="🎬 UPLOADED", inline=False)
                    embed.add_field(name="🔥 Watch Now", value=f"[Click Here To Watch]({link})", inline=False)

                    embed.set_image(
                        url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                    )

                    embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                    embed.timestamp = discord.utils.utcnow()

                    if PING_ROLE_ID:
                        await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                    else:
                        await channel.send(embed=embed)

                    print("Upload notification sent")

            print("Sleeping 30 seconds...")
            await asyncio.sleep(30)

        except Exception as e:
            print("ERROR:", e)
            await asyncio.sleep(30)


@client.event
async def on_ready():
    print(f"Bot Online: {client.user}")
    client.loop.create_task(check_youtube())


client.run(TOKEN)
