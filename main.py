import telebot
from groq import Groq
from flask import Flask, request

TELEGRAM_TOKEN = "8326889206:AAGtg2O0f4kYPpG7i2yh1CW-ydu2-n3ioPE"
GROQ_API_KEY = "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"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {"sinf": None, "fan": None}
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for s in ["5-sinf","6-sinf","7-sinf","8-sinf","9-sinf","10-sinf","11-sinf"]:
        markup.add(telebot.types.KeyboardButton(s))
    bot.send_message(message.chat.id,
        "👋 Assalomu alaykum! EduBot ga xush kelibsiz!\n\n📚 Sinfingizni tanlang:",
        reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["5-sinf","6-sinf","7-sinf","8-sinf","9-sinf","10-sinf","11-sinf"])
def sinf_tanlash(message):
    if message.chat.id not in user_data:
        user_data[message.chat.id] = {}
    user_data[message.chat.id]["sinf"] = message.text
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for f in ["Matematika","Fizika","Kimyo","Biologiya","Tarix","Adabiyot","Ingliz tili","Rus tili","Geografiya","Informatika"]:
        markup.add(telebot.types.KeyboardButton(f))
    bot.send_message(message.chat.id, f"✅ {message.text} tanlandi!\n\n📖 Fanni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["Matematika","Fizika","Kimyo","Biologiya","Tarix","Adabiyot","Ingliz tili","Rus tili","Geografiya","Informatika"])
def fan_tanlash(message):
    if message.chat.id not in user_data:
        user_data[message.chat.id] = {}
    user_data[message.chat.id]["fan"] = message.text
    sinf = user_data[message.chat.id].get("sinf", "")
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔄 O'zgartirish")
    bot.send_message(message.chat.id,
        f"🎯 {sinf} — {message.text}\n\nSavolingizni yuboring! 💬",
        reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔄 O'zgartirish")
def ozgartirish(message):
    start(message)

@bot.message_handler(func=lambda m: True)
def javob(message):
    chat_id = message.chat.id
    sinf = user_data.get(chat_id, {}).get("sinf", "")
    fan = user_data.get(chat_id, {}).get("fan", "")
    if not sinf or not fan:
        start(message)
        return
    bot.send_chat_action(chat_id, "typing")
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"Sen EduBot — O'zbekiston maktab o'quvchilari uchun AI o'qituvchisan. Foydalanuvchi: {sinf} o'quvchisi, fan: {fan}. O'zbek tilida, oddiy va qiziqarli tilda javob ber. Misollar keltir."},
                {"role": "user", "content": message.text}
            ],
            max_tokens=1000
        )
        bot.send_message(chat_id, response.choices[0].message.content)
    except:
        bot.send_message(chat_id, "❌ Xatolik yuz berdi. Qayta urinib ko'ring!")

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route('/')
def index():
    return "EduBot ishlayapti!", 200

if name == "main":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://edubot-zj5y.onrender.com/{TELEGRAM_TOKEN}")
    app.run(host='0.0.0.0', port=5000)
