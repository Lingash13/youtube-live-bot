import discord
import asyncio
import os
import requests

TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
PING_ROLE_ID = os.getenv("PING_ROLE_ID")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

live_video_id = None


def get_live_video(channel_id):
    try:
        url = f"https://www.youtube.com/channel/{channel_id}/live"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }

        r = requests.get(url, headers=headers, timeout=10)

        html = r.text

        if "isLiveNow\":true" in html:
            start = html.find("/watch?v=")
            if start != -1:
                video_id = html[start+9:start+20]
                return True, video_id

        return False, None

    except Exception as e:
        print("Live check error:", e)
        return False, None


async def check_live():
    global live_video_id

    await client.wait_until_ready()

    while not client.is_closed():
        try:
            print("Checking live status...")

            channel = await client.fetch_channel(DISCORD_CHANNEL_ID)

            is_live, current_id = get_live_video(YOUTUBE_CHANNEL_ID)

            print("Is Live:", is_live)

            # LIVE START
            if is_live and live_video_id != current_id:
                live_video_id = current_id
                link = f"https://youtube.com/watch?v={current_id}"

                embed = discord.Embed(
                    title="🔥 🔴 LIVE STREAM STARTED 🔴 🔥",
                    description="🚀 Join now and dominate the stream!",
                    color=0xFF0000,
                    url=link
                )

                embed.add_field(name="📡 Status", value="🟢 ONLINE", inline=False)
                embed.add_field(name="🔥 Watch Now", value=f"[Click Here To Watch]({link})", inline=False)

                embed.set_image(
                    url=f"https://img.youtube.com/vi/{current_id}/maxresdefault.jpg"
                )

                embed.set_footer(text="🎮 LK GAMING THENI | Powered by LL Studio")
                embed.timestamp = discord.utils.utcnow()

                if PING_ROLE_ID:
                    await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                else:
                    await channel.send(embed=embed)

                print("Live notification sent")

            # LIVE END
            if not is_live and live_video_id:
                embed = discord.Embed(
                    title="⛔ 🔴 LIVE STREAM ENDED 🔴 ⛔",
                    description="🎮 Thanks for watching!",
                    color=0x2F3136
                )

                embed.add_field(name="📡 Status", value="🔴 OFFLINE", inline=False)

                embed.set_footer(text="🎮 LK GAMING THENI | Powered by LL Studio")
                embed.timestamp = discord.utils.utcnow()

                if PING_ROLE_ID:
                    await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                else:
                    await channel.send(embed=embed)

                print("Live ended notification sent")
                live_video_id = None

            print("Sleeping 30 seconds...\n")
            await asyncio.sleep(30)

        except Exception as e:
            print("ERROR:", e)
            await asyncio.sleep(30)


@client.event
async def on_ready():
    print(f"Bot Online: {client.user}")
    client.loop.create_task(check_live())


client.run(TOKEN)
