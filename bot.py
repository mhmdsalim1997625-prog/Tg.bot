import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from yt_dlp import YoutubeDL

TOKEN = "9237449351:AAFquO0Oihz0zzFr7OQwRMlSmwfhIVNDU80"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("أهلاً بك يا أبو براء! البوت جاهز الآن، أرسل أي رابط فيديو لتحميله.")

@dp.message()
async def download_video(message: types.Message):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.answer("يرجى إرسال رابط صالح يبدأ بـ http أو https.")
        return

    processing_msg = await message.answer("جاري سحب وتحميل الفيديو، انتظر قليلاً...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'max_filesize': 50 * 1024 * 1024, # حدود حجم الملف لتليجرام
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        video_file = types.FSInputFile(filename)
        await message.answer_video(video_file, caption="تم التحميل بنجاح بواسطة بوتك الخاص!")
        
        os.remove(filename)
        await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)

    except Exception as e:
        await message.edit_text("عذراً، حدث خطأ أثناء التحميل. تأكد من صحة الرابط أو جرب رابطاً آخر.")

async def main():
    print("البوت يعمل الآن بكامل الميزات...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
