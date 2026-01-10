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

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎥 *Media Downloader Bot*\n\n"
        "Send a link from:\n"
        "YouTube | Instagram | Facebook | Twitter\n\n"
        "Select quality after sending link.",
        parse_mode="Markdown"
    )

# ---------- LINK HANDLER ----------
async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    context.user_data["url"] = url

    keyboard = [
        [InlineKeyboardButton("🎵 MP3 (320kbps)", callback_data="mp3")],
        [
            InlineKeyboardButton("📹 720p", callback_data="720"),
            InlineKeyboardButton("📹 1080p", callback_data="1080")
        ],
        [
            InlineKeyboardButton("📹 2K", callback_data="1440"),
            InlineKeyboardButton("📹 4K", callback_data="2160")
        ]
    ]

    await update.message.reply_text(
        "Choose download quality 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------- DOWNLOAD HANDLER ----------
async def download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    quality = query.data

    await query.edit_message_text("⏳ Downloading... Please wait")

    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        "quiet": True,
        "merge_output_format": "mp4",
        "cookiefile": "cookies.txt"   # ✅ COOKIES ADDED HERE
    }

    try:
        if quality == "mp3":
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320"
                }]
            })
        else:
            ydl_opts["format"] = f"bestvideo[height<={quality}]+bestaudio/best"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        if quality == "mp3":
            file_path = file_path.rsplit(".", 1)[0] + ".mp3"
            await query.message.reply_audio(open(file_path, "rb"))
        else:
            await query.message.reply_video(open(file_path, "rb"))

        os.remove(file_path)

    except Exception as e:
        await query.message.reply_text(f"❌ Error:\n{e}")

# ---------- MAIN ----------
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, link_handler))
app.add_handler(CallbackQueryHandler(download_callback))

print("🤖 Bot running...")
app.run_polling()