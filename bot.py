
import os
import asyncio
import sqlite3

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from yt_dlp import YoutubeDL


TOKEN = os.getenv("BOT_TOKEN", "9237449351:AAFquO0Oihz0zzFr7OQwRMlSmwfhIVNDU80")

bot = Bot(token=TOKEN)
dp = Dispatcher()

ADMIN_ID = 1061676621


# إنشاء قاعدة البيانات
def init_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT
        )
    """)

    conn.commit()
    conn.close()


# حفظ بيانات المستخدم
def save_user(user):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
        username = excluded.username,
        first_name = excluded.first_name
    """, (
        user.id,
        user.username,
        user.first_name
    ))

    conn.commit()
    conn.close()


# حساب عدد المستخدمين
def get_users_count():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    conn.close()
    return count


init_db()


# لوحة تحكم المدير
@dp.message(Command("admin"))
async def admin_handler(message: types.Message):

    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ غير مسموح لك بالدخول")
        return

    users = get_users_count()

    await message.answer(
        "⚙️ لوحة تحكم المدير\n\n"
        f"👥 عدد المستخدمين: {users}\n"
        "━━━━━━━━━━━━\n"
        "مرحباً بك في لوحة الإدارة!"
    )


# زر البداية
def get_start_button():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📋 القائمة الرئيسية (الخيارات)")
    builder.adjust(1)

    return builder.as_markup(resize_keyboard=True)


# قائمة المنصات
def get_options_menu():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🎵 تحميل فيديو تيك توك",
        callback_data="opt_tiktok"
    )

    builder.button(
        text="📸 تحميل فيديو انستغرام",
        callback_data="opt_insta"
    )

    builder.button(
        text="📘 تحميل فيديو فيسبوك",
        callback_data="opt_facebook"
    )

    builder.adjust(1)

    return builder.as_markup()


# أمر البدء
@dp.message(Command("start"))
@dp.message(F.text == "🚀 ابدأ (Start)")
async def start_handler(message: types.Message):

    save_user(message.from_user)

    user_name = message.from_user.first_name or "صديقي"

    await message.answer(
        f"أهلاً بك يا **{user_name}** في بوتك الخاص للتحميل 🌟\n"
        "اضغط على الزر أدناه لفتح قائمة الخيارات:",
        reply_markup=get_start_button(),
        parse_mode="Markdown"
    )


# إظهار القائمة الرئيسية
@dp.message(F.text == "📋 القائمة الرئيسية (الخيارات)")
async def show_options_menu(message: types.Message):

    await message.answer(
        "اختر المنصة التي تريد التحميل منها:",
        reply_markup=get_options_menu()
    )


# معالجة اختيار المنصة
@dp.callback_query(F.data.startswith("opt_"))
async def process_menu_option(callback: types.CallbackQuery):

    action = callback.data.split("_")[1]

    if action == "tiktok":
        await callback.message.answer(
            "حسناً، أرسل الآن رابط فيديو تيك توك 🎬"
        )

    elif action == "insta":
        await callback.message.answer(
            "حسناً، أرسل الآن رابط فيديو انستغرام 📸"
        )

    elif action == "facebook":
        await callback.message.answer(
            "حسناً، أرسل الآن رابط فيديو فيسبوك 📘"
        )

    await callback.answer()


# معالجة الروابط
@dp.message(F.text)
async def handle_text_messages(message: types.Message):

    text = message.text.strip()

    if text == "📋 القائمة الرئيسية (الخيارات)":
        return

    if text.startswith("http"):

        await message.answer(
            "⏳ جاري المعالجة والتحميل، يرجى الانتظار..."
        )

        filename = None

        try:
            ydl_opts = {
                "format": "best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "max_filesize": 50 * 1024 * 1024,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                filename = ydl.prepare_filename(info)

            await message.answer_video(
                types.FSInputFile(filename),
                caption="تم التحميل بنجاح بواسطة بوتك الخاص! ✨"
            )

        except Exception as e:
            await message.answer(
                f"حدث خطأ أثناء التحميل:\n{str(e)}"
            )

        finally:
            if filename and os.path.exists(filename):
                os.remove(filename)

    else:
        await message.answer(
            "عذراً، أرسل رابطاً صالحاً للتحميل أو استخدم القائمة الرئيسية 📋"
        )


# تشغيل البوت
async def main():

    os.makedirs("downloads", exist_ok=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
