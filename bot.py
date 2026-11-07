import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from yt_dlp import YoutubeDL

TOKEN = "9237449351:AAFquO0Oihz0zzFr7OQwRMlSmwfhIVNDU80"

bot = Bot(token=TOKEN)
dp = Dispatcher()
ADMIN_ID = 1061676621
@dp.message(Command("admin"))
async def admin_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ غير مسموح لك بالدخول")
        return

    await message.answer(
        "👋 أهلاً بك في لوحة تحكم المدير!\n"
        "سيتم تجهيز الإحصائيات قريباً."
    )
# زر أساسي واحد يظهر للمستخدم في البداية
def get_start_button():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📋 القائمة الرئيسية (الخيارات)")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

# قائمة الخيارات التفاعلية (تيك توك، انستغرام، فيسبوك)
def get_options_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎵 تحميل فيديو تيك توك", callback_data="opt_tiktok")
    builder.button(text="📸 تحميل فيديو انستغرام", callback_data="opt_insta")
    builder.button(text="📘 تحميل فيديو فيسبوك", callback_data="opt_facebook")
    builder.adjust(1)
    return builder.as_markup()

# أمر البدء مع جلب اسم المستخدم الحقيقي
@dp.message(Command("start"))
@dp.message(F.text == "🚀 ابدأ (Start)")
async def start_handler(message: types.Message):
    user_name = message.from_user.first_name or "صديقي"
    await message.answer(
        f"أهلاً بك يا **{user_name}** في بوتك الخاص للتحميل 🌟\n"
        f"اضغط على الزر أدناه لفتح قائمة الخيارات:",
        reply_markup=get_start_button(),
        parse_mode="Markdown"
    )

# عند الضغط على زر إظهار القائمة الرئيسية
@dp.message(F.text == "📋 القائمة الرئيسية (الخيارات)")
async def show_options_menu(message: types.Message):
    await message.answer(
        "اختر المنصة التي تريد التحميل منها:",
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
    elif action == "facebook":
        await callback.message.answer("حسناً، أرسل الآن رابط فيديو **فيسبوك** وسأقوم بتحميله لك فوراً 📘")
        
    await callback.answer()

# معالجة النصوص الواردة (الروابط فقط)
@dp.message(F.text)
async def handle_text_messages(message: types.Message):
    text = message.text.strip()
    
    if text == "📋 القائمة الرئيسية (الخيارات)":
        return
        
    if text.startswith("http"):
        await message.answer("⏳ جاري المعالجة والتحميل من السحابة، يرجى الانتظار...")
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'downloads/%(id)s.%(ext)s',
                'max_filesize': 50 * 1024 * 1024,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                filename = ydl.prepare_filename(info)
            
            await message.answer_video(types.FSInputFile(filename), caption="تم التحميل بنجاح بواسطة بوتك الخاص! ✨")
            os.remove(filename)
            
        except Exception as e:
            await message.answer(f"حدث خطأ أثناء التحميل: تأكد من صحة الرابط أو أن الفيديو عام. ({str(e)})")
    else:
        await message.answer("عذراً، يرجى إرسال رابط صالح للتحميل أو استخدام القائمة الرئيسية للأزرار 📋")

async def main():
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
