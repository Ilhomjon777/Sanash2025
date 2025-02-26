import sqlite3
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio

TOKEN = "8123932765:AAG0v59JVqzaKBua6jeNutnu6ReLDp7P3Ec"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Ma'lumotlar bazasini yaratish
def create_db():
    with sqlite3.connect("inviters.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inviters (
                user_id INTEGER PRIMARY KEY,
                invited_count INTEGER DEFAULT 0
            )
        """)
        conn.commit()

# Odam qo‘shgan foydalanuvchini bazaga yozish
def update_inviter(user_id, count):
    with sqlite3.connect("inviters.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT invited_count FROM inviters WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        if result:
            cursor.execute("UPDATE inviters SET invited_count = invited_count + ? WHERE user_id=?", (count, user_id))
        else:
            cursor.execute("INSERT INTO inviters (user_id, invited_count) VALUES (?, ?)", (user_id, count))
        conn.commit()

# **Yangi odam guruhga qo‘shilganda kim qo‘shganini aniqlash**
@dp.message()
async def track_new_members(message: types.Message):
    if message.new_chat_members:
        inviter = message.from_user  # Odam qo‘shgan shaxs
        new_members = message.new_chat_members  # Yangi qo‘shilgan odamlar ro‘yxati
        count = len(new_members)  # Nechta odam qo‘shilganini aniqlaymiz

        if inviter.id:
            update_inviter(inviter.id, count)
            member_names = ", ".join([member.full_name for member in new_members])
            logging.info(f"{inviter.id} foydalanuvchi {member_names} ni guruhga qo‘shdi.")
            await message.reply(f"✅ {inviter.full_name} {count} ta odam qo‘shdi: {member_names}!")

# Eng ko‘p odam qo‘shganlarni chiqarish
@dp.message(Command("top_inviters"))
async def show_top_inviters(message: types.Message):
    with sqlite3.connect("inviters.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, invited_count FROM inviters ORDER BY invited_count DESC LIMIT 10")
        top_invites = cursor.fetchall()
    
    if not top_invites:
        await message.reply("Hozircha hech kim odam qo'shmagan.")
        return

    text = "🏆 Top 10 eng ko‘p odam qo‘shgan foydalanuvchilar:\n"
    for user_id, count in top_invites:
        text += f"🆔 {user_id}: {count} ta odam qo‘shgan\n"
    
    await message.reply(text)

# Botni ishga tushirish
async def main():
    create_db()
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
