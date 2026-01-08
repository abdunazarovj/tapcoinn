import asyncio
import time
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# ===================== TOKEN =====================
TOKEN = "8507150924:AAHGqDPJwPNs__ttp4JSgzrTPPrpz3EracI"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ===================== DATABASE =====================
db = sqlite3.connect("tapcoin.db")
sql = db.cursor()

sql.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    last_mine INTEGER DEFAULT 0,
    last_daily INTEGER DEFAULT 0
)
""")
db.commit()

# ===================== SETTINGS =====================
MAX = 100        # Coin maksimal miqdori
COOLDOWN = 1800  # Cooldown, sekund (30 daqiqa)

# ===================== /start COMMAND =====================
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id

    # Foydalanuvchini bazaga qo'shish (agar mavjud bo'lmasa)
    sql.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    db.commit()

    # Inline button → WebApp ochish
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="🚀 Launch TapCoin",
            web_app=WebAppInfo(
                url=f"https://tapcoinn.netlify.app/"  # Sizning Netlify WebApp manzilingiz
            )
        )
    ]])

    await message.answer("TapCoin ilovasini ochish uchun bosing 👇", reply_markup=kb)

# ===================== WebApp DATA =====================
@dp.message(lambda msg: msg.web_app_data)
async def webapp(message: types.Message):
    user_id = message.from_user.id
    data = message.web_app_data.data
    now = int(time.time())

    # Foydalanuvchi ma'lumotlarini olish
    sql.execute("SELECT balance, last_mine, last_daily FROM users WHERE user_id=?", (user_id,))
    row = sql.fetchone()
    if row:
        balance, last_mine, last_daily = row
    else:
        # Agar foydalanuvchi yo'q bo'lsa, yaratamiz
        balance = last_mine = last_daily = 0
        sql.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        db.commit()

    # ================= TAP =================
    if data == "tap":
        # Agar balance MAX ga yetgan bo'lsa va cooldown tugamagan bo'lsa, hech narsa qilmaymiz
        if balance >= MAX and now - last_mine < COOLDOWN:
            return
        # Agar balance MAX ga yetgan bo'lsa va cooldown tugagan bo'lsa, reset qilamiz
        if balance >= MAX:
            balance = 0

        # Balansni oshiramiz va last_mine yangilaymiz
        sql.execute("UPDATE users SET balance=?, last_mine=? WHERE user_id=?", (balance + 1, now, user_id))
        db.commit()

    # ================= DAILY =================
    if data == "daily":
        # Foydalanuvchi oxirgi daily olgan vaqtini tekshirish
        if now - last_daily < 86400:  # 24 soat = 86400 s
            return
        # Daily bonusni berish va last_daily yangilash
        sql.execute("UPDATE users SET balance=balance+10, last_daily=? WHERE user_id=?", (now, user_id))
        db.commit()

# ===================== MAIN =====================
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
