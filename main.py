import asyncio
import openai
from pyrogram import Client, filters

# Telegram API ma'lumotlaringiz
API_ID = 36997528
API_HASH = "3c38f0248860a0823ad0cf9d1b21e4bf"
PHONE_NUMBER = "+79038547102"

# OpenAI API kalitingiz
openai.api_key = "Sk-proj-hWOOvY4GLohaUoOuXP7ijf3ThdoVzB5_4MEexKptPwWweoO8vbzCHf5kJkGZdIQV2sEo4ccn4nT3BlbkFJRzH4GIlJUgHvywbaHbKI9_VQD2PTtZfKswCrTrflvM7_2Y9hXx4xZaBivxXHR9FNDYYKbtZNEA"

# Javob berishni kutish vaqti (soniyalarda): 90 soniya
WAIT_TIME = 90 

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER)

pending_tasks = {}

SYSTEM_PROMPT = """
Siz — Xadyatillo Shuhratjonovning Telegram bot-yordamchisiz.
Hozir Xadyatillo band bo'lishi yoki xabarga darhol javob bera olmayotgan bo'lishi mumkin (ehtimol studiyada musiqa ustida ishlayapti, trek prodyuserligi yoki audio ustida ishlamoqda).

Javob berish qoidalari:
1. Samimiy, professional va do'stona tilda o'zbekcha javob bering.
2. Agar foydalanuvchi musiqa, beat, sound design yoki audio haqida so'rasa, Xadyatillo bu sohada professional musiqachi va prodyuser ekanligini bildiring.
3. Javobingizda Xadyatillo tez orada xabarni ko'rib o'zi ham javob berishini qisqa va samimiy tushuntiring.
4. Javoblar juda qisqa va londa bo'lsin.
"""

def ask_gpt(user_name, prompt_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Foydalanuvchi ismi: {user_name}\nXabari: {prompt_text}"}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"GPT Xatolik: {e}")
        return None

async def delayed_reply(chat_id, user_name, message):
    await asyncio.sleep(WAIT_TIME)
    ai_response = ask_gpt(user_name, message.text)
    if ai_response:
        await message.reply_text(ai_response)
        print(f"[{user_name}] ga AI avto-javob yubordi.")
    pending_tasks.pop(chat_id, None)

@app.on_message(filters.private & ~filters.me & ~filters.bot)
async def handle_incoming_message(client, message):
    chat_id = message.chat.id
    sender_name = message.from_user.first_name or "Foydalanuvchi"

    if chat_id in pending_tasks:
        pending_tasks[chat_id].cancel()

    task = asyncio.create_task(delayed_reply(chat_id, sender_name, message))
    pending_tasks[chat_id] = task
    print(f"Xabar keldi ({sender_name}). {WAIT_TIME} soniya kutilmoqda...")

@app.on_message(filters.private & filters.me)
async def handle_own_message(client, message):
    chat_id = message.chat.id
    if chat_id in pending_tasks:
        pending_tasks[chat_id].cancel()
        del pending_tasks[chat_id]
        print(f"O'zingiz javob berdingiz. AI javobi bekor qilindi.")

if __name__ == "__main__":
    print("Userbot kuzatuv va avto-javob rejimida ishga tushdi...")
    app.run()
