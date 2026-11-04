import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from yt_dlp import YoutubeDL

TOKEN = "9237449351:AAFquO0Oihz0zzFr7OQwRMlSmwfhIVNDU80"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# إعدادات ثابتة لتجاوز حماية يوتيوب
BASE_YDL_OPTS = {
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
    }
}

# زر أساسي واحد يظهر للمستخدم في البداية
def get_start_button():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📋 القائمة الرئيسية (الخيارات)")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

# قائمة الخيارات التفاعلية
def get_options_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎵 تحميل فيديو تيك توك", callback_data="opt_tiktok")
    builder.button(text="📸 تحميل فيديو انستغرام", callback_data="opt_insta")
    builder.button(text="📺 تحميل فيديو يوتيوب", callback_data="opt_yt")
    builder.button(text="🔍 البحث على يوتيوب", callback_data="opt_search")
    builder.adjust(1)
    return builder.as_markup()

# أمر البدء مع جلب اسم المستخدم الحقيقي
@dp.message(Command("start"))
@dp.message(F.text == "🚀 ابدأ (Start)")
async def start_handler(message: types.Message):
    user_name = message.from_user.first_name or "صديقي"
    await message.answer(
        f"أهلاً بك يا **{user_name}** في بوتك الخاص للتحميل والتصفح 🌟\n"
        f"اضغط على الزر أدناه لفتح قائمة الخيارات:",
        reply_markup=get_start_button(),
        parse_mode="Markdown"
    )

# عند الضغط على زر إظهار القائمة الرئيسية
@dp.message(F.text == "📋 القائمة الرئيسية (الخيارات)")
async def show_options_menu(message: types.Message):
    await message.answer(
        "اختر ما تحب القيام به من القائمة أدناه:",
        reply_markup=get_options_menu()
    )

# معالجة الضغط على خيارات القائمة الداخلية
@dp.callback_query(F.data.startswith("opt_"))
async def process_menu_option(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    
    if action == "tiktok":
        await callback.message.answer("حسناً، أرسل الآن رابط فيديو **تيك توك** وسأقوم بتحميله لك فوراً 🎬")
    elif action == "insta":
        await callback.message.answer("حسناً، أرسل الآن رابط فيديو **انستغرام** وسأقوم بتحميله لك فوراً 📸")
    elif action == "yt":
        await callback.message.answer("حسناً، أرسل الآن رابط فيديو **يوتيوب** وسأعرض خيارات التحميل 🎧")
    elif action == "search":
        await callback.message.answer("اكتب الآن الكلمة أو العنوان الذي تريد البحث عنه في يوتيوب 🔍:")
        
    await callback.answer()

# معالجة النصوص الواردة (روابط أو كلمات بحث)
@dp.message(F.text)
async def handle_text_messages(message: types.Message):
    text = message.text.strip()
    
    if text == "📋 القائمة الرئيسية (الخيارات)":
        return
        
    if text.startswith("http"):
        builder = InlineKeyboardBuilder()
        builder.button(text="🎬 تحميل فيديو", callback_data=f"vid|{text}")
        builder.button(text="🎵 تحميل صوت MP3", callback_data=f"mp3|{text}")
        builder.button(text="🖼️ تحميل الغلاف", callback_data=f"img|{text}")
        builder.adjust(1)
        await message.answer("اختر صيغة التحميل المناسبة لهذا الرابط:", reply_markup=builder.as_markup())
    else:
        await message.answer(f"🔍 جاري البحث عن: `{text}` في يوتيوب، يرجى الانتظار...")
        try:
            ydl_opts = {**BASE_YDL_OPTS, 'extract_flat': True, 'max_downloads': 5}
            search_query = f"ytsearch5:{text}"
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=False)
                entries = info.get('entries', [])
            
            if not entries:
                await message.answer("عذراً، لم أجد نتائج مطابقة لبحثك.")
                return
            
            builder = InlineKeyboardBuilder()
            for entry in entries:
                title = entry.get('title', 'فيديو بدون عنوان')[:45] + "..."
                video_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                builder.button(text=f"🎥 {title}", callback_data=f"vid|{video_url}")
            
            builder.adjust(1)
            await message.answer("إليك نتائج البحث، اختر الفيديو الذي ترغب بتحميله:", reply_markup=builder.as_markup())
            
        except Exception as e:
            await message.answer(f"حدث خطأ أثناء البحث: {str(e)}")

# معالجة عمليات التحميل
@dp.callback_query(F.data.startswith(("vid|", "mp3|", "img|")))
async def process_download(callback: types.CallbackQuery):
    action, url = callback.data.split("|", 1)
    await callback.message.edit_text("⏳ جاري المعالجة والتحميل من السحابة، يرجى الانتظار...")
    
    try:
        if action == "vid":
            ydl_opts = {
                **BASE_YDL_OPTS,
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
                **BASE_YDL_OPTS,
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
            ydl_opts = {**BASE_YDL_OPTS, 'skip_download': True}
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
