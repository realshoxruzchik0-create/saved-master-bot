import os
import asyncio
import logging
import aiohttp
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

async def download_via_cobalt(url: str, output_path: str) -> bool:
    api_url = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "vCodec": "h264"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload, headers=headers) as resp:
                data = await resp.json()
                video_url = data.get("url")
                if video_url:
                    async with session.get(video_url) as video_resp:
                        if video_resp.status == 200:
                            with open(output_path, "wb") as f:
                                f.write(await video_resp.read())
                            return True
    except Exception as e:
        logging.error(f"Cobalt API Error: {e}")
    return False

@dp.message(F.text.startswith("http"))
async def download_video(message: types.Message):
    url = message.text.strip()
    status_msg = await message.answer("⏳ Video yuklanmoqda, kuting...")
    
    file_path = f"video_{message.from_user.id}.mp4"
    
    # 1-usul: Cobalt API orqali sinab ko'rish
    success = await download_via_cobalt(url, file_path)
    
    # 2-usul: Agar Cobalt bo'lmasa, zaxira yt-dlp ishlaydi
    if not success:
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': file_path,
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }

        def fetch():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        try:
            await asyncio.to_thread(fetch)
        except Exception as e:
            logging.error(f"yt-dlp error: {e}")

    if os.path.exists(file_path):
        try:
            video_file = types.FSInputFile(file_path)
            await message.answer_video(video=video_file, caption="✅ Video yuklab olindi!")
            await status_msg.delete()
        except Exception as e:
            await status_msg.edit_text("❌ Videoni Telegramga yuborishda xatolik bo'ldi.")
        finally:
            os.remove(file_path)
    else:
        await status_msg.edit_text("❌ Yuklab olishda xatolik yuz berdi. Linkni tekshirib qaytadan yuboring.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
