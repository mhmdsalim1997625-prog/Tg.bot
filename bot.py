import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from yt_dlp import YoutubeDL

TOKEN = "9237449351:AAFquO0Oihz0zzFr7OQwRMlSmwfhIVNDU80"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# أمر البدء
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("أهلاً بك يا أبو براء! أرسل أي رابط (يوتيوب، تيك توك، إلخ) وسأعرض لك خيارات التحميل المناسبة.")

# استقبال الرابط وعرض أزرار الاختيار (القائمة التفاعلية)
@dp.message(F.text.startswith("http"))
async def ask_download_format(message: types.Message):
    url = message.text.strip()
    
    # بناء أزرار خيارات التحميل
    builder = InlineKeyboardBuilder()
    builder.button(text="🎬 تحميل فيديو", callback_data=f"vid|{url}")
    builder.button(text="🎵 تحميل صوت MP3", callback_data=f"mp3|{url}")
    builder.button(text="🖼️ تحميل صورة مصغرة", callback_data=f"img|{url}")
    builder.adjust(1) # ترتيب الأزرار تحت بعضها
    
    await message.answer("اختر صيغة التحميل المناسبة:", reply_markup=builder.as_markup())

# معالجة ضغط الأزرار والبدء بالتحميل حسب رغبة المستخدم
@dp.callback_query(F.data.startswith(("vid|", "mp3|", "img|")))
async def process_download(callback: types.CallbackQuery):
    action, url = callback.data.split("|", 1)
    await callback.message.edit_text("جاري المعالجة والتحميل، يرجى الانتظار قليلاً...")
    
    try:
        if action == "vid":
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'downloads/%(id)s.%(ext)s',
                'max_filesize': 50 * 1024 * 1024, # حد أقصى 50 ميغا لتناسب تيليجرام
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            await callback.message.answer_video(types.FSInputFile(filename), caption="تم تحميل الفيديو بنجاح بواسطة بوتك الخاص!")
            os.remove(filename)
            
        elif action == "mp3":
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': 'downloads/%(id)s.%(ext)s',
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
            
            await callback.message.answer_audio(types.FSInputFile(filename), caption="تم تحويل وتحميل الصوت بنجاح بواسطة بوتك الخاص!")
            os.remove(filename)
            
        elif action == "img":
            ydl_opts = {'skip_download': True}
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                thumbnail_url = info.get('thumbnail')
            
            if thumbnail_url:
                await callback.message.answer_photo(thumbnail_url, caption="هذه هي صورة الغلاف/الصورة المصغرة للرابط.")
            else:
                await callback.message.answer("عذراً، لا توجد صورة متاحة لهذا الرابط.")
                
    except Exception as e:
        await callback.message.answer(f"حدث خطأ أثناء التحميل: {str(e)}")

async def main():
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

