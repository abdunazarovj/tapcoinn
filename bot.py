import asyncio
import time
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = "8507150924:AAHGqDPJwPNs__ttp4JSgzrTPPrpz3EracI"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# SQLite DB
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

# /start → Launch WebApp
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    sql.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    db.commit()

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text="🚀 Launch TapCoin",
        web_app=WebAppInfo(
            url=f"https://tapcoinn.netlify.app?user_id={user_id}"
        )
    )]])

    await message.answer("TapCoin ilovasini ochish uchun bosing 👇", reply_markup=kb)


# WebApp’dan keladigan buyruqlar
@dp.message(lambda msg: msg.web_app_data)
async def webapp(message: types.Message):
    user_id = message.from_user.id
    data = message.web_app_data.data
    now = int(time.time())

    # TAP
    if data == "tap":
        sql.execute("SELECT balance, last_mine FROM users WHERE user_id=?", (user_id,))
        balance, last_mine = sql.fetchone()

        if balance >= MAX and now - last_mine < COOLDOWN:
            return

        if balance >= MAX:
            balance = 0

        sql.execute("UPDATE users SET balance = balance + 1, last_mine=? WHERE user_id=?", (now, user_id))
        db.commit()

    # DAILY
    if data == "daily":
        sql.execute("SELECT last_daily FROM users WHERE user_id=?", (user_id,))
        last_daily = sql.fetchone()[0]

        if now - last_daily < 86400:
            return

        sql.execute("UPDATE users SET balance = balance + 10, last_daily=? WHERE user_id=?", (now, user_id))
        db.commit()


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())