import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("8348615649:AAFY799SOdeKpLwtDTgHKyVdgU3HSxgjbtY")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎥 *Media Downloader Bot*\n\n"
        "Send a video link from:\n"
        "YouTube | Instagram | Facebook | Twitter",
        parse_mode="Markdown"
    )

# ---------------- LINK HANDLER ----------------
async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    context.user_data.clear()
    context.user_data["url"] = url

    keyboard = [
        [InlineKeyboardButton("🎬 Video", callback_data="menu_video")],
        [InlineKeyboardButton("🎵 Audio", callback_data="menu_audio")]
    ]

    await update.message.reply_text(
        "Choose what you want 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- MENU HANDLER ----------------
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu_audio":
        keyboard = [
            [InlineKeyboardButton("🎧 MP3 128kbps", callback_data="mp3_128")],
            [InlineKeyboardButton("🎧 MP3 192kbps", callback_data="mp3_192")],
            [InlineKeyboardButton("🎧 MP3 320kbps", callback_data="mp3_320")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
        ]
        await query.edit_message_text("🎵 Select audio quality:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "menu_video":
        url = context.user_data["url"]

        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        qualities = sorted({f["height"] for f in info["formats"] if f.get("height")})

        buttons = []
        for q in qualities:
            emoji = "🎬"
            if q >= 2160:
                emoji = "🔥"
            elif q >= 1440:
                emoji = "✨"
            elif q >= 1080:
                emoji = "⭐"
            buttons.append([InlineKeyboardButton(f"{emoji} {q}p", callback_data=f"video_{q}")])

        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_main")])

        await query.edit_message_text(
            "🎬 Select video quality:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif query.data == "back_main":
        keyboard = [
            [InlineKeyboardButton("🎬 Video", callback_data="menu_video")],
            [InlineKeyboardButton("🎵 Audio", callback_data="menu_audio")]
        ]
        await query.edit_message_text("Choose what you want 👇", reply_markup=InlineKeyboardMarkup(keyboard))

# ---------------- DOWNLOAD HANDLER ----------------
async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data["url"]
    data = query.data

    await query.edit_message_text("⏳ Downloading... Please wait")

    ydl_opts = {
    "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
    "quiet": True,
    "merge_output_format": "mp4",
    "cookiefile": "cookies.txt"

    }

     try:
        # 🎵 AUDIO
        if data.startswith("mp3"):
            bitrate = data.split("_")[1]
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": bitrate
                }]
            })

        # 🎬 VIDEO
        elif data.startswith("video"):
            height = data.split("_")[1]
            ydl_opts["format"] = f"bv*[height<={height}]+ba/b"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        if data.startswith("mp3"):
            file_path = file_path.rsplit(".", 1)[0] + ".mp3"
            await query.message.reply_audio(open(file_path, "rb"))
        else:
            await query.message.reply_video(open(file_path, "rb"))

        os.remove(file_path)

    except Exception as e:
        await query.message.reply_text(f"❌ Error:\n{e}")
# ---------------- MAIN ----------------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, link_handler))
app.add_handler(CallbackQueryHandler(menu_handler, pattern="menu_|back_"))
app.add_handler(CallbackQueryHandler(download_handler, pattern="video_|mp3_"))

print("🤖 Bot running...")
app.run_polling()
