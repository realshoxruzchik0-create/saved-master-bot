import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import yt_dlp

BOT_TOKEN = "8994223471:AAEMX4XbjPkTKs7BIMUdbeBxWEuGBO3MgWk"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_links = {}

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "Men **Saved Master Bot**man. YouTube va Instagram'dan video hamda musiqalarni yuklab beraman.\n\n"
        "Menga shunchaki media havolasini (linkini) yuboring!"
    )

@dp.message(F.text.startswith("http://") | F.text.startswith("https://"))
async def handle_link(message: types.Message):
    url = message.text.strip()
    user_id = message.from_user.id
    user_links[user_id] = url

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎵 Musiqasi (MP3)", callback_data="dl_audio"),
                InlineKeyboardButton(text="🎬 Videosini yuklash", callback_data="dl_video"),
            ]
        ]
    )

    await message.answer("Tanlang: Musiqasini yuklaysizmi yoki videosinimi?", reply_markup=keyboard)

@dp.callback_query(F.data.in_({"dl_video", "dl_audio"}))
async def process_download(call: CallbackQuery):
    user_id = call.from_user.id
    url = user_links.get(user_id)

    if not url:
        await call.message.edit_text("❌ Link topilmadi. Qaytadan link yuboring.")
        return

    is_audio = call.data == "dl_audio"
    status_msg = await call.message.edit_text("⏳ Yuklab olinmoqda, biroz kuting...")

    os.makedirs("downloads", exist_ok=True)

    ydl_opts = {
        'outtmpl': f'downloads/{user_id}_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    if is_audio:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        ydl_opts.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        })

    try:
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, download_media, url, ydl_opts, is_audio)

        await status_msg.edit_text("🚀 Telegram'ga yuklanmoqda...")

        if is_audio:
            audio_file = types.FSInputFile(file_path)
            await call.message.answer_audio(audio=audio_file, caption="✅ Musiqasi yuklab olindi! | @SavedMasterBot")
        else:
            video_file = types.FSInputFile(file_path)
            await call.message.answer_video(video=video_file, caption="✅ Video yuklab olindi! | @SavedMasterBot")

        await status_msg.delete()

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await status_msg.edit_text("❌ Yuklab olishda xatolik yuz berdi. Linkni tekshirib qaytadan yuboring.")
        print(f"Xatolik: {e}")

def download_media(url, opts, is_audio):
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if is_audio:
            base, _ = os.path.splitext(filename)
            return f"{base}.mp3"
        return filename

async def main():
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
