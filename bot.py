import discord
import asyncio
import os
import feedparser

TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
PING_ROLE_ID = os.getenv("PING_ROLE_ID")

RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_video_id = None
live_video_id = None


async def check_youtube():
    global last_video_id
    global live_video_id

    await client.wait_until_ready()

    while not client.is_closed():
        try:
            print("Checking RSS...")

            channel = await client.fetch_channel(DISCORD_CHANNEL_ID)

            feed = feedparser.parse(RSS_URL)

            if not feed.entries:
                print("No entries found")
                await asyncio.sleep(30)
                continue

            latest = feed.entries[0]
            video_id = latest.yt_videoid
            title = latest.title
            link = latest.link

            # 🔴 Detect type
            broadcast_type = latest.get("yt_livebroadcastcontent", "none")

            print("Video ID:", video_id)
            print("Broadcast Type:", broadcast_type)

            # ----------------------
            # 🔴 LIVE START
            # ----------------------
            if broadcast_type == "live":

                if live_video_id != video_id:
                    live_video_id = video_id

                    embed = discord.Embed(
                        title="🔥 🔴 LIVE STREAM STARTED 🔴 🔥",
                        description=f"🎮 **{title}**\n\n🚀 Join now and dominate the stream!",
                        color=0xFF0000,
                        url=link
                    )

                    embed.add_field(name="📡 Status", value="🟢 ONLINE", inline=False)
                    embed.add_field(name="🔥 Join Now", value=f"[Click Here To Watch]({link})", inline=False)

                    embed.set_image(
                        url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                    )

                    embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                    embed.timestamp = discord.utils.utcnow()

                    if PING_ROLE_ID:
                        await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                    else:
                        await channel.send(embed=embed)

                    print("Live started sent")

            # ----------------------
            # 🟡 SCHEDULED
            # ----------------------
            elif broadcast_type == "upcoming":

                if last_video_id != video_id:
                    last_video_id = video_id

                    embed = discord.Embed(
                        title="🟡 🔔 LIVE STREAM SCHEDULED 🔔 🟡",
                        description=f"🎮 **{title}**",
                        color=0xFFA500,
                        url=link
                    )

                    embed.add_field(name="📡 Status", value="🟡 SCHEDULED", inline=False)
                    embed.add_field(name="🔔 Reminder", value=f"[Set Reminder]({link})", inline=False)

                    embed.set_image(
                        url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                    )

                    embed.set_footer(text="🎮 Developed by Lingash | Powered by LL Studio")
                    embed.timestamp = discord.utils.utcnow()

                    if PING_ROLE_ID:
                        await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                    else:
                        await channel.send(embed=embed)

                    print("Scheduled live sent")

            # ----------------------
            # 🎬 NORMAL UPLOAD
            # ----------------------
            else:

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

                    print("Upload sent")

            # ----------------------
            # 🔴 LIVE END CHECK
            # ----------------------
            if live_video_id and broadcast_type != "live":
                print("Live ended detected")

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

                live_video_id = None

            print("Sleeping 30 seconds...\n")
            await asyncio.sleep(30)

        except Exception as e:
            print("ERROR:", e)
            await asyncio.sleep(30)


@client.event
async def on_ready():
    print(f"Bot Online: {client.user}")
    client.loop.create_task(check_youtube())


client.run(TOKEN)
