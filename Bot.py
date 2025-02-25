import sqlite3
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ChatMemberUpdated
from aiogram.filters import Command
import asyncio

TOKEN = "7985405287:AAEYzkZzdtfOobjqlCYnRyTvVcJZY3RavCE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Ma'lumotlar bazasini yaratamiz
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

# Foydalanuvchini bazaga qo'shish yoki yangilash
def update_inviter(user_id):
    with sqlite3.connect("inviters.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT invited_count FROM inviters WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        if result:
            cursor.execute("UPDATE inviters SET invited_count = invited_count + 1 WHERE user_id=?", (user_id,))
        else:
            cursor.execute("INSERT INTO inviters (user_id, invited_count) VALUES (?, ?)", (user_id, 1))
        conn.commit()

# Guruhga kim yangi odam qo‘shganini tekshiramiz
@dp.chat_member(ChatMemberUpdated)
async def track_new_members(update: ChatMemberUpdated):
    if update.new_chat_member.status == "member" and update.invite_link is None:
        inviter_id = update.from_user.id
        if inviter_id != update.new_chat_member.user.id:  # O'zini qo'shmaganligiga ishonch hosil qilamiz
            update_inviter(inviter_id)

# Top inviterlarni chiqarish
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
    create_db()  # Bazani yaratamiz
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
