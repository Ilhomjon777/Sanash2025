import sqlite3
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatMemberUpdated
from aiogram.utils import executor

TOKEN = "7985405287:AAEYzkZzdtfOobjqlCYnRyTvVcJZY3RavCE"  # BotFather-dan olingan tokenni shu yerga qo'ying

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Ma'lumotlar bazasini yaratamiz
conn = sqlite3.connect("inviters.db")
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
    cursor.execute("SELECT invited_count FROM inviters WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        cursor.execute("UPDATE inviters SET invited_count = invited_count + 1 WHERE user_id=?", (user_id,))
    else:
        cursor.execute("INSERT INTO inviters (user_id, invited_count) VALUES (?, ?)", (user_id, 1))
    conn.commit()

# Guruhga kim yangi odam qo'shganini tekshiramiz
@dp.chat_member_handler()
async def track_new_members(update: ChatMemberUpdated):
    if update.new_chat_member.status == "member" and update.from_user.id != update.new_chat_member.user.id:
        update_inviter(update.from_user.id)

# Top inviterlarni chiqarish
@dp.message_handler(commands=["top_inviters"])
async def show_top_inviters(message: types.Message):
    cursor.execute("SELECT user_id, invited_count FROM inviters ORDER BY invited_count DESC LIMIT 10")
    top_invites = cursor.fetchall()
    
    if not top_invites:
        await message.reply("Hozircha hech kim odam qo'shmagan.")
        return

    text = "Top 10 eng ko‘p odam qo‘shgan foydalanuvchilar:\n"
    for user_id, count in top_invites:
        text += f"🆔 {user_id}: {count} ta odam qo‘shgan\n"
    
    await message.reply(text)

# Botni ishga tushirish
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
