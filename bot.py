import asyncio
import time
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = "8507150924:AAHGqDPJwPNs__ttp4JSgzrTPPrpz3EracI"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ===== DATABASE =====
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

MAX = 100
COOLDOWN = 1800

# ===== /start =====
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    sql.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    db.commit()

    kb = InlineKeyboardMarkup(inline_keyboard=[[ 
        InlineKeyboardButton(
            text="🚀 Launch TapCoin",
            web_app=WebAppInfo(url="https://tapcoinn.netlify.app")
        )
    ]])
    await message.answer("TapCoin ilovasini ochish uchun bosing 👇", reply_markup=kb)

# ===== WebApp data =====
@dp.message(lambda msg: msg.web_app_data)
async def webapp(message: types.Message):
    user_id = message.from_user.id
    data = message.web_app_data.data
    now = int(time.time())

    sql.execute("SELECT balance, last_mine, last_daily FROM users WHERE user_id=?", (user_id,))
    row = sql.fetchone()
    if row:
        balance, last_mine, last_daily = row
    else:
        balance = last_mine = last_daily = 0
        sql.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        db.commit()

    # TAP
    if data == "tap":
        if now - last_mine < COOLDOWN:
            return
        if balance >= MAX:
            balance = 0
        balance += 1
        last_mine = now
        sql.execute("UPDATE users SET balance=?, last_mine=? WHERE user_id=?",
                    (balance, last_mine, user_id))
        db.commit()
        await message.answer(f"{balance},{last_mine},{last_daily}")

    # DAILY
    elif data == "daily":
        if now - last_daily < 86400:
            return
        balance += 10
        last_daily = now
        sql.execute("UPDATE users SET balance=?, last_daily=? WHERE user_id=?",
                    (balance, last_daily, user_id))
        db.commit()
        await message.answer(f"{balance},{last_mine},{last_daily}")

    # GET BALANCE
    elif data == "get_balance":
        await message.answer(f"{balance},{last_mine},{last_daily}")

# ===== MAIN =====
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
