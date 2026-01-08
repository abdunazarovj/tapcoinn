import asyncio
import time
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = "BU_YERGA_BOT_TOKENINGNI_QO'Y"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== DATABASE =====
db = sqlite3.connect("tapcoin.db")
sql = db.cursor()

sql.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    last_mine INTEGER DEFAULT 0
)
""")
db.commit()

MAX_BALANCE = 100
COOLDOWN = 1800  # 30 minut

# ===== START =====
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id

    sql.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    db.commit()

    sql.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    balance = sql.fetchone()[0]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🪙 TapCoin ochish",
                web_app=WebAppInfo(
                    url=f"https://tapcoinn.netlify.app/"
                )
            )
        ]
    ])

    await message.answer(
        "🪙 TapCoin ilovasiga xush kelibsiz!\n👇 Miningni boshlash uchun bosing",
        reply_markup=keyboard
    )

# ===== BALANCE =====
@dp.message(Command("balance"))
async def balance_cmd(message: types.Message):
    user_id = message.from_user.id
    sql.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    bal = sql.fetchone()[0]
    await message.answer(f"💰 Balansingiz: {bal} TapCoin")

# ===== TAP (WEBAPP'DAN KELADI) =====
@dp.message(lambda msg: msg.web_app_data)
async def tap(message: types.Message):
    user_id = message.from_user.id
    now = int(time.time())

    sql.execute("SELECT balance, last_mine FROM users WHERE user_id=?", (user_id,))
    balance, last_mine = sql.fetchone()

    if balance >= MAX_BALANCE and now - last_mine < COOLDOWN:
        await message.answer("⛔ Limit tugadi. 30 minut kuting")
        return

    if balance >= MAX_BALANCE:
        balance = 0

    sql.execute("""
        UPDATE users
        SET balance = balance + 1, last_mine = ?
        WHERE user_id=?
    """, (now, user_id))
    db.commit()

# ===== RUN =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
