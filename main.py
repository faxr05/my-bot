import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from yt_dlp import YoutubeDL

# Bot tokeningizni bura yozing
TOKEN = "8434672153:AAGrIoiaSMBmgQKGdWvAsznDHYnJXsgtZxE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Render uchun vaqtincha papka
if not os.path.exists("downloads"):
    os.makedirs("downloads")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Salom! YouTube yoki Instagram linkini yuboring.")

@dp.message(F.text.contains("http"))
async def handle_link(message: types.Message):
    url = message.text
    kb = InlineKeyboardBuilder()
    kb.button(text="🎬 Video", callback_data=f"vid|{url}")
    kb.button(text="🎵 Audio (MP3)", callback_data=f"aud|{url}")
    kb.adjust(1)
    await message.answer("Nima yuklamoqchisiz?", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("vid") | F.data.startswith("aud"))
async def download_content(callback: types.CallbackQuery):
    action, url = callback.data.split("|")
    await callback.message.edit_text("Yuklanmoqda... Iltimos kuting.")
    
    file_path = f"downloads/{callback.from_user.id}.%(ext)s"
    ydl_opts = {'outtmpl': file_path, 'noplaylist': True}

    if action == "vid":
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    else:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if action == "aud": filename = filename.rsplit('.', 1)[0] + ".mp3"

        file = types.FSInputFile(filename)
        if action == "vid":
            await callback.message.answer_video(file)
        else:
            await callback.message.answer_audio(file)
        
        os.remove(filename)
        await callback.message.delete()
    except Exception as e:
        await callback.message.answer(f"Xatolik yuz berdi. Linkni tekshiring.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
