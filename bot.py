import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
import yt_dlp

TOKEN = "8994223471:AAEMX4XbjPkTKs7BIMUdbeBxWEuGBO3MgWk"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Xush kelibsiz! Menga YouTube yoki Instagram havolasini yuboring, men videoni yuklab beraman.")

@dp.message(F.text.startswith("http"))
async def download_video(message: types.Message):
    url = message.text.strip()
    status_msg = await message.answer("⏳ Video yuklanmoqda, kuting...")
    
    file_path = f"video_{message.from_user.id}.mp4"
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': file_path,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'source_address': '0.0.0.0',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    }

    def fetch():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    try:
        await asyncio.to_thread(fetch)
        
        if os.path.exists(file_path):
            video_file = types.FSInputFile(file_path)
            await message.answer_video(video=video_file, caption="✅ Video yuklab olindi!")
            os.remove(file_path)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Videoni saqlab bo'lmadi.")
    except Exception as e:
        logging.error(f"Error downloading video: {e}")
        await status_msg.edit_text("❌ Yuklab olishda xatolik yuz berdi. Linkni tekshirib qaytadan yuboring.")
        if os.path.exists(file_path):
            os.remove(file_path)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
