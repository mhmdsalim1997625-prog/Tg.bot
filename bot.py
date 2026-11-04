import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from yt_dlp import YoutubeDL

TOKEN = "9237449351:AAFquO0Oihz0zzFr7OQwRMlSmwfhIVNDU80"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# دالة لإنشاء القائمة الرئيسية الثابتة (لوحة المفاتيح تحت الرسائل)
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🚀 ابدأ (Start)")
    builder.button(text="🎵 تحميل فيديو تيك توك")
    builder.button(text="📸 تحميل فيديو انستغرام")
    builder.button(text="📺 تحميل فيديو يوتيوب")
    builder.button(text="🔍 البحث على يوتيوب")
    builder.adjust(1, 2, 2) # ترتيب الأزرار بشكل جذاب (زر بالأعلى ثم زوج من الأزرار تحتها)
    return builder.as_markup(resize_keyboard=True)

# أمر البدء وعرض القائمة
@dp.message(Command("start"))
@dp.message(F.text == "🚀 ابدأ (Start)")
async def start_handler(message: types.Message):
    await message.answer(
        f"أهلاً بك يا أبو براء في بوتك الخاص للتحميل والتصفح!\n"
        f"اختر ما تحب من القائمة أدناه:",
        reply_markup=get_main_menu()
    )

# الخيار الثاني: طلب رابط تيك توك
@dp.message(F.text == "🎵 تحميل فيديو تيك توك")
async def tiktok_prompt(message: types.Message):
    await message.answer("حسناً، أرسل الآن رابط فيديو **تيك توك** وسأقوم بتحميله لك فوراً 🎬")

# الخيار الثالث: طلب رابط انستغرام
@dp.message(F.text == "📸 تحميل فيديو انستغرام")
async def instagram_prompt(message: types.Message):
    await message.answer("حسناً، أرسل الآن رابط فيديو **انستغرام** وسأقوم بتحميله لك فوراً 📸")

# الخيار الرابع: طلب رابط يوتيوب
@dp.message(F.text == "📺 تحميل فيديو يوتيوب")
async def youtube_prompt(message: types.Message):
    await message.answer("حسناً، أرسل الآن رابط فيديو **يوتيوب** وسأقوم بعرض خيارات التحميل (فيديو أو صوت MP3) 🎧")

# الخيار الخامس: البحث على يوتيوب
@dp.message(F.text == "🔍 البحث على يوتيوب")
async def search_youtube_prompt(message: types.Message):
    # نضع علامة تميز أن الرسالة القادمة هي بحث
    await message.answer("اكتب الآن الكلمة أو العنوان الذي تريد البحث عنه في يوتيوب 🔍:")

# معالجة النصوص الواردة (إما روابط أو كلمات بحث أو روابط تحميل مباشرة)
@dp.message(F.text)
async def handle_text_messages(message: types.Message):
    text = message.text.strip()
    
    # إذا كان النص رابطاً
    if text.startswith("http"):
        builder = InlineKeyboardBuilder()
        builder.button(text="🎬 تحميل فيديو", callback_data=f"vid|{text}")
        builder.button(text="🎵 تحميل صوت MP3", callback_data=f"mp3|{text}")
        builder.button(text="🖼️ تحميل الغلاف", callback_data=f"img|{text}")
        builder.adjust(1)
        await message.answer("اختر صيغة التحميل المناسبة لهذا الرابط:", reply_markup=builder.as_markup())
    
    # إذا لم يكن رابطاً، نعتبره عملية بحث في يوتيوب
    else:
        await message.answer(f"🔍 جاري البحث عن: `{text}` في يوتيوب، يرجى الانتظار...")
        try:
            ydl_opts = {
                'extract_flat': True,
                'max_downloads': 5, # جلب أول 5 نتائج بحث
            }
            search_query = f"ytsearch5:{text}"
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=False)
                entries = info.get('entries', [])
            
            if not entries:
                await message.answer("عذراً، لم أجد نتائج مطابقة لبحثك.")
                return
            
            # بناء قائمة أزرار بالنتائج
            builder = InlineKeyboardBuilder()
            for entry in entries:
                title = entry.get('title', 'فيديو بدون عنوان')[:45] + "..."
                video_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                builder.button(text=f"🎥 {title}", callback_data=f"vid|{video_url}")
            
            builder.adjust(1)
            await message.answer("إليك نتائج البحث، اختر الفيديو الذي ترغب بتحميله:", reply_markup=builder.as_markup())
            
        except Exception as e:
            await message.answer(f"حدث خطأ أثناء البحث: {str(e)}")

# معالجة أزرار التحميل (فيديو أو صوت أو صورة)
@dp.callback_query(F.data.startswith(("vid|", "mp3|", "img|")))
async def process_download(callback: types.CallbackQuery):
    action, url = callback.data.split("|", 1)
    await callback.message.edit_text("⏳ جاري المعالجة والتحميل من السحابة، يرجى الانتظار...")
    
    try:
        if action == "vid":
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'downloads/%(id)s.%(ext)s',
                'max_filesize': 50 * 1024 * 1024,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            await callback.message.answer_video(types.FSInputFile(filename), caption="تم التحميل بنجاح بواسطة بوتك الخاص! ✨")
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
            
            await callback.message.answer_audio(types.FSInputFile(filename), caption="تم تحويل وتحميل الصوت بنجاح! 🎵")
            os.remove(filename)
            
        elif action == "img":
            ydl_opts = {'skip_download': True}
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                thumbnail_url = info.get('thumbnail')
            
            if thumbnail_url:
                await callback.message.answer_photo(thumbnail_url, caption="هذه هي الصورة المصغرة للرابط 🖼️")
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
