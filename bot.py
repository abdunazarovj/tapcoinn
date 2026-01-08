import asyncio
import time
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = "8507150924:AAHGqDPJwPNs__ttp4JSgzrTPPrpz3EracI"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ================= DATABASE =================
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

MAX_BALANCE = 100
COOLDOWN = 1800  # 30 minut

# ================= START =================
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id

    sql.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    db.commit()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🪙 TapCoin ochish",
                web_app=WebAppInfo(url="https://semizqurt.netlify.app/")
            )
        ]
    ])

    await message.answer(
        "🪙 TapCoin ilovasiga xush kelibsiz!\n👇 Bosib miningni boshlang",
        reply_markup=kb
    )

# ================= BALANCE =================
@dp.message(Command("balance"))
async def balance(message: types.Message):
    user_id = message.from_user.id
    sql.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    bal = sql.fetchone()[0]
    await message.answer(f"💰 Balansingiz: {bal} TapCoin")

# ================= DAILY =================
@dp.message(Command("daily"))
async def daily(message: types.Message):
    user_id = message.from_user.id
    now = int(time.time())

    sql.execute("SELECT last_daily FROM users WHERE user_id=?", (user_id,))
    last = sql.fetchone()[0]

    if now - last < 86400:
        await message.answer("❌ Bugun allaqachon oldingiz")
        return

    sql.execute("""
        UPDATE users 
        SET balance = balance + 10, last_daily = ?
        WHERE user_id=?
    """, (now, user_id))
    db.commit()

    await message.answer("🎁 +10 TapCoin qo‘shildi!")

# ================= WEBAPP TAP =================
@dp.message(lambda msg: msg.web_app_data)
async def tap(message: types.Message):
    user_id = message.from_user.id
    now = int(time.time())

    sql.execute("SELECT balance, last_mine FROM users WHERE user_id=?", (user_id,))
    balance, last_mine = sql.fetchone()

    if balance >= MAX_BALANCE and now - last_mine < COOLDOWN:
        await message.answer("⛔ Limit! 30 minut kuting")
        return

    if balance >= MAX_BALANCE:
        balance = 0

    sql.execute("""
        UPDATE users
        SET balance = balance + 1, last_mine = ?
        WHERE user_id=?
    """, (now, user_id))
    db.commit()

# ================= HELP =================
@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "/start - Ilovani ochish\n"
        "/balance - Balans\n"
        "/daily - Kunlik sovg‘a\n"
        "/help - Yordam"
    )

# ================= RUN =================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
