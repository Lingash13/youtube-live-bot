import os
import discord
from discord.ext import tasks
from googleapiclient.discovery import build

# ===============================
# ENV VARIABLES
# ===============================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# ===============================
# DISCORD SETUP
# ===============================

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# ===============================
# YOUTUBE SETUP
# ===============================

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

last_status = None
last_video_id = None

# ===============================
# LIVE CHECK LOOP
# ===============================

@tasks.loop(minutes=10)
async def check_live_stream():
    global last_status, last_video_id

    try:
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            print("❌ Discord channel not found")
            return

        # Get uploads playlist
        channel_response = youtube.channels().list(
            part="contentDetails",
            id=CHANNEL_ID
        ).execute()

        uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Get latest uploaded video
        playlist_response = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=1
        ).execute()

        latest_video = playlist_response["items"][0]
        video_id = latest_video["snippet"]["resourceId"]["videoId"]

        # Get video details
        video_response = youtube.videos().list(
            part="snippet,liveStreamingDetails",
            id=video_id
        ).execute()

        video_data = video_response["items"][0]
        live_details = video_data.get("liveStreamingDetails")

        # ===============================
        # STREAM IS LIVE
        # ===============================
        if live_details and "actualStartTime" in live_details and "actualEndTime" not in live_details:

            if last_status != "live":
                last_status = "live"
                last_video_id = video_id

                title = video_data["snippet"]["title"]
                thumbnail = video_data["snippet"]["thumbnails"]["high"]["url"]
                url = f"https://www.youtube.com/watch?v={video_id}"

                embed = discord.Embed(
                    title="🔥 🔴 LIVE STREAM STARTED 🔴 🔥",
                    description=(
                        f"🎮 **{title}**\n\n"
                        "🚀 The battle has begun!\n"
                        "💥 Join now and enjoy the stream!\n"
                    ),
                    color=discord.Color.red()
                )

                embed.set_image(url=thumbnail)
                embed.add_field(
                    name="📺 Watch Now",
                    value=f"[Click Here To Watch]({url})",
                    inline=False
                )

                embed.set_footer(text="Developed By Lingash, Powered by EazBy Studio")

                await channel.send(embed=embed)
                print("✅ Live started embed sent")

        # ===============================
        # STREAM ENDED
        # ===============================
        else:
            if last_status == "live" and last_video_id == video_id:
                last_status = "ended"

                title = video_data["snippet"]["title"]
                thumbnail = video_data["snippet"]["thumbnails"]["high"]["url"]
                url = f"https://www.youtube.com/watch?v={video_id}"

                embed = discord.Embed(
                    title="📴 🔴 LIVE STREAM ENDED 🔴",
                    description=(
                        f"🎮 **{title}**\n\n"
                        "🛑 The stream has officially ended.\n"
                        "💬 Thanks for joining!\n\n"
                        "🎥 Watch the replay below!"
                    ),
                    color=discord.Color.dark_red()
                )

                embed.set_image(url=thumbnail)
                embed.add_field(
                    name="🎥 Watch Replay",
                    value=f"[Click Here To Watch]({url})",
                    inline=False
                )

                embed.set_footer(text="Developed By Lingash, Powered by EazBy Studio")

                await channel.send(embed=embed)
                print("🔔 Live ended embed sent")

    except Exception as e:
        print("❌ Error:", e)


# ===============================
# BOT READY
# ===============================

@client.event
async def on_ready():
    print(f"🤖 Logged in as {client.user}")
    check_live_stream.start()


# ===============================
# RUN BOT
# ===============================

client.run(DISCORD_TOKEN)
