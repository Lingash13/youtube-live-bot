import discord
import asyncio
import os
import requests

TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
PING_ROLE_ID = os.getenv("PING_ROLE_ID")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

live_video_id = None
scheduled_video_id = None


# ------------------------------------------------
# 🔎 GET CHANNEL LIVE / SCHEDULED STATUS
# ------------------------------------------------
def get_channel_status():
    try:
        url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet"
            f"&channelId={CHANNEL_ID}"
            f"&eventType=live"
            f"&type=video"
            f"&key={YOUTUBE_API_KEY}"
        )

        live_response = requests.get(url).json()

        if live_response.get("items"):
            video_id = live_response["items"][0]["id"]["videoId"]
            return "live", video_id

        # Check scheduled
        url_upcoming = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet"
            f"&channelId={CHANNEL_ID}"
            f"&eventType=upcoming"
            f"&type=video"
            f"&key={YOUTUBE_API_KEY}"
        )

        upcoming_response = requests.get(url_upcoming).json()

        if upcoming_response.get("items"):
            video_id = upcoming_response["items"][0]["id"]["videoId"]
            return "scheduled", video_id

        return "offline", None

    except Exception as e:
        print("API Error:", e)
        return "offline", None


# ------------------------------------------------
# MAIN LOOP
# ------------------------------------------------
async def check_status():
    global live_video_id
    global scheduled_video_id

    await client.wait_until_ready()

    while not client.is_closed():
        try:
            print("Checking YouTube API status...")

            channel = await client.fetch_channel(DISCORD_CHANNEL_ID)

            status, video_id = get_channel_status()

            print("Status:", status)

            # -----------------------------
            # 🔴 LIVE START
            # -----------------------------
            if status == "live" and live_video_id != video_id:
                live_video_id = video_id
                scheduled_video_id = None

                link = f"https://youtube.com/watch?v={video_id}"

                embed = discord.Embed(
                    title="🔥 🔴 LIVE STREAM STARTED 🔴 🔥",
                    description="🚀 The battle has begun!\n💥 Join now and dominate the stream!",
                    color=0xFF0000,
                    url=link
                )

                embed.set_author(name="LK GAMING THENI")
                embed.add_field(name="🛰 Status", value="🟢 ONLINE", inline=False)
                embed.add_field(name="🔥 Join Now", value=f"[Click Here To Watch]({link})", inline=False)

                embed.set_image(url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg")
                embed.set_thumbnail(url=f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg")

                embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                embed.timestamp = discord.utils.utcnow()

                if PING_ROLE_ID:
                    await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                else:
                    await channel.send(embed=embed)

                print("Live notification sent")

            # -----------------------------
            # 🟡 SCHEDULED
            # -----------------------------
            elif status == "scheduled" and scheduled_video_id != video_id:
                scheduled_video_id = video_id

                link = f"https://youtube.com/watch?v={video_id}"

                embed = discord.Embed(
                    title="🟡 🔔 LIVE STREAM SCHEDULED 🔔 🟡",
                    description="⏰ Stream will begin soon!\n🔥 Get ready!",
                    color=0xFFA500,
                    url=link
                )

                embed.set_author(name="LK GAMING THENI")
                embed.add_field(name="🛰 Status", value="🟡 SCHEDULED", inline=False)
                embed.add_field(name="🔔 Reminder", value=f"[Set Reminder Here]({link})", inline=False)

                embed.set_image(url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg")
                embed.set_thumbnail(url=f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg")

                embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                embed.timestamp = discord.utils.utcnow()

                if PING_ROLE_ID:
                    await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                else:
                    await channel.send(embed=embed)

                print("Scheduled notification sent")

            # -----------------------------
            # ⛔ LIVE ENDED
            # -----------------------------
            elif status == "offline" and live_video_id:
                link = f"https://youtube.com/watch?v={live_video_id}"

                embed = discord.Embed(
                    title="⛔ 🔴 LIVE STREAM ENDED 🔴 ⛔",
                    description="🎮 Stream has ended.\n🙏 Thanks for watching!",
                    color=0x2F3136,
                    url=link
                )

                embed.set_author(name="LK GAMING THENI")
                embed.add_field(name="🛰 Status", value="🔴 OFFLINE", inline=False)
                embed.add_field(name="📺 Watch Replay", value=f"[Click Here To Watch]({link})", inline=False)

                embed.set_image(url=f"https://img.youtube.com/vi/{live_video_id}/maxresdefault.jpg")
                embed.set_thumbnail(url=f"https://img.youtube.com/vi/{live_video_id}/hqdefault.jpg")

                embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                embed.timestamp = discord.utils.utcnow()

                if PING_ROLE_ID:
                    await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                else:
                    await channel.send(embed=embed)

                print("Live ended notification sent")
                live_video_id = None

            print("Sleeping 60 seconds...\n")
            await asyncio.sleep(60)

        except Exception as e:
            print("ERROR:", e)
            await asyncio.sleep(60)


@client.event
async def on_ready():
    print(f"Bot Online: {client.user}")
    client.loop.create_task(check_status())


client.run(TOKEN)
