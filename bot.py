import discord
import asyncio
import os
import requests
import re

TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
PING_ROLE_ID = os.getenv("PING_ROLE_ID")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

live_video_id = None
scheduled_video_id = None


# ------------------------------------------------
# 🔴 LIVE DETECTION (Accurate)
# ------------------------------------------------
def get_live_video(channel_id):
    try:
        url = f"https://www.youtube.com/channel/{channel_id}/videos"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }

        r = requests.get(url, headers=headers, timeout=10)
        html = r.text

        # Extract ONLY videoId with LIVE badge
        live_blocks = re.findall(
            r'"videoId":"(.*?)".*?"badgeRenderer":\{"label":"LIVE"',
            html
        )

        if live_blocks:
            return True, live_blocks[0]

        return False, None

    except Exception as e:
        print("Live check error:", e)
        return False, None


# ------------------------------------------------
# 🟡 SCHEDULED DETECTION (Accurate)
# ------------------------------------------------
def get_scheduled_live(channel_id):
    try:
        url = f"https://www.youtube.com/channel/{channel_id}/streams"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }

        r = requests.get(url, headers=headers, timeout=10)
        html = r.text

        # Extract ONLY upcoming event videoId
        upcoming_blocks = re.findall(
            r'"videoId":"(.*?)".*?"upcomingEventData"',
            html
        )

        if upcoming_blocks:
            return True, upcoming_blocks[0]

        return False, None

    except Exception as e:
        print("Scheduled check error:", e)
        return False, None


# ------------------------------------------------
# MAIN LOOP
# ------------------------------------------------
async def check_status():
    global live_video_id
    global scheduled_video_id

    await client.wait_until_ready()

    while not client.is_closed():
        try:
            print("Checking YouTube status...")

            channel = await client.fetch_channel(DISCORD_CHANNEL_ID)

            # -----------------------------
            # 🟡 CHECK SCHEDULED
            # -----------------------------
            is_scheduled, sched_id = get_scheduled_live(YOUTUBE_CHANNEL_ID)

            if is_scheduled and scheduled_video_id != sched_id:
                scheduled_video_id = sched_id
                link = f"https://youtube.com/watch?v={sched_id}"

                embed = discord.Embed(
                    title="🟡 🔔 LIVE STREAM SCHEDULED 🔔 🟡",
                    description="⏰ Stream will begin soon!\n🔥 Get ready for an epic session!",
                    color=0xFFA500,
                    url=link
                )

                embed.set_author(name="LK GAMING THENI")

                embed.add_field(name="🛰 Status", value="🟡 SCHEDULED", inline=False)
                embed.add_field(name="🔔 Reminder", value=f"[Set Reminder Here]({link})", inline=False)

                embed.set_image(
                    url=f"https://img.youtube.com/vi/{sched_id}/maxresdefault.jpg"
                )

                embed.set_thumbnail(
                    url=f"https://img.youtube.com/vi/{sched_id}/hqdefault.jpg"
                )

                embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                embed.timestamp = discord.utils.utcnow()

                if PING_ROLE_ID:
                    await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                else:
                    await channel.send(embed=embed)

                print("Scheduled notification sent")

            # -----------------------------
            # 🔴 CHECK LIVE
            # -----------------------------
            is_live, current_id = get_live_video(YOUTUBE_CHANNEL_ID)

            if is_live and live_video_id != current_id:
                live_video_id = current_id
                link = f"https://youtube.com/watch?v={current_id}"

                embed = discord.Embed(
                    title="🔥 🔴 LIVE STREAM STARTED 🔴 🔥",
                    description="🚀 The battle has begun!\n💥 Join now and dominate the stream!",
                    color=0xFF0000,
                    url=link
                )

                embed.set_author(name="LK GAMING THENI")

                embed.add_field(name="⚔ Stream Mode", value="Live Gameplay", inline=False)
                embed.add_field(name="🛰 Status", value="🟢 ONLINE", inline=False)
                embed.add_field(name="🔥 Join Now", value=f"[Click Here To Watch]({link})", inline=False)

                embed.set_image(
                    url=f"https://img.youtube.com/vi/{current_id}/maxresdefault.jpg"
                )

                embed.set_thumbnail(
                    url=f"https://img.youtube.com/vi/{current_id}/hqdefault.jpg"
                )

                embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                embed.timestamp = discord.utils.utcnow()

                if PING_ROLE_ID:
                    await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                else:
                    await channel.send(embed=embed)

                print("Live started notification sent")

            # -----------------------------
            # ⛔ LIVE ENDED
            # -----------------------------
            if not is_live and live_video_id:
                link = f"https://youtube.com/watch?v={live_video_id}"

                embed = discord.Embed(
                    title="⛔ 🔴 LIVE STREAM ENDED 🔴 ⛔",
                    description="🎮 The battle has ended!\n🙏 Thanks for watching and supporting!",
                    color=0x2F3136,
                    url=link
                )

                embed.set_author(name="LK GAMING THENI")

                embed.add_field(name="🛰 Status", value="🔴 OFFLINE", inline=False)
                embed.add_field(name="📺 Watch Replay", value=f"[Click Here To Watch]({link})", inline=False)

                embed.set_image(
                    url=f"https://img.youtube.com/vi/{live_video_id}/maxresdefault.jpg"
                )

                embed.set_thumbnail(
                    url=f"https://img.youtube.com/vi/{live_video_id}/hqdefault.jpg"
                )

                embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                embed.timestamp = discord.utils.utcnow()

                if PING_ROLE_ID:
                    await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                else:
                    await channel.send(embed=embed)

                print("Live ended notification sent")

                live_video_id = None
                scheduled_video_id = None

            print("Sleeping 30 seconds...\n")
            await asyncio.sleep(30)

        except Exception as e:
            print("ERROR:", e)
            await asyncio.sleep(30)


@client.event
async def on_ready():
    print(f"Bot Online: {client.user}")
    client.loop.create_task(check_status())


client.run(TOKEN)
