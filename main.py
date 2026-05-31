import telebot
from groq import Groq
from flask import Flask, request
import os
from datetime import datetime

# === KALITLAR ===
TELEGRAM_TOKEN = "8326889206:AAGtg2O0f4kYPpG7i2yh1CW-ydu2-n3ioPE"
GROQ_API_KEY = "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"
RENDER_URL = "https://edubot-zj5y.onrender.com"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

# === MA'LUMOTLAR ===
users = {}
results = {}
parents = {}

SINFLAR = ["1-sinf","2-sinf","3-sinf","4-sinf","5-sinf","6-sinf","7-sinf","8-sinf","9-sinf","10-sinf","11-sinf"]

FANLAR = [
    "Matematika", "Algebra", "Geometriya",
    "Fizika", "Kimyo", "Biologiya",
    "Ona tili", "Adabiyot", "Rus tili",
    "Ingliz tili", "Tarix", "Geografiya",
    "Informatika", "Chizmachilik", "Texnologiya",
    "Jismoniy tarbiya", "Musiqa", "Tasviriy san'at"
]

DARAJALAR = {900: "🥇 A'lochi", 700: "🥈 Yaxshi", 500: "🥉 Muvaffaqiyatli", 300: "📈 Rivojlanmoqda", 0: "💪 Harakat kerak"}

def daraja(ball):
    for chegara, nom in sorted(DARAJALAR.items(), reverse=True):
        if ball >= chegara:
            return nom
    return "💪 Harakat kerak"

def til(cid):
    return users.get(cid, {}).get("til", "uz")

def t(cid, uz, ru):
    return ru if til(cid) == "ru" else uz

def yangi_user(cid):
    if cid not in users:
        users[cid] = {"rol": None, "sinf": None, "fan": None, "til": "uz", "ball": 0, "savollar": 0, "testlar": 0}

def natija_saqlash(cid):
    sinf = users.get(cid, {}).get("sinf")
    fan = users.get(cid, {}).get("fan")
    ball = users.get(cid, {}).get("ball", 0)
    nom = users.get(cid, {}).get("nom", f"ID:{cid}")
    if not sinf or not fan:
        return
    if sinf not in results:
        results[sinf] = {}
    if fan not in results[sinf]:
        results[sinf][fan] = []
    # Yangilash yoki qo'shish
    topildi = False
    for o in results[sinf][fan]:
        if o["cid"] == cid:
            o["ball"] = ball
            o["sana"] = datetime.now().strftime("%d.%m.%Y %H:%M")
            o["nom"] = nom
            topildi = True
            break
    if not topildi:
        results[sinf][fan].append({"cid": cid, "ball": ball, "nom": nom, "sana": datetime.now().strftime("%d.%m.%Y %H:%M")})
    # Ota-onaga xabar
    for p_cid, b_cid in parents.items():
        if b_cid == cid:
            try:
                bot.send_message(p_cid, f"📊 Farzandingiz *{nom}*\n🎓 {sinf} — {fan}\n⭐ Ball: {ball}\n{daraja(ball)}", parse_mode="Markdown")
            except:
                pass

# =====================
# START
# =====================
@bot.message_handler(commands=['start'])
def start(msg):
    cid = msg.chat.id
    yangi_user(cid)
    m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("👨‍🎓 O'quvchi", "👨‍🏫 O'qituvchi", "👨‍👩‍👧 Ota-ona", "🌐 Til / Язык")
    bot.send_message(cid,
        "👋 *EduBot*ga xush kelibsiz!\n\n"
        "📱 O'zbekiston o'quvchilari uchun AI o'qituvchi\n\n"
        "Rolni tanlang:",
        reply_markup=m, parse_mode="Markdown")

@bot.message_handler(commands=['myid'])
def myid(msg):
    bot.send_message(msg.chat.id, f"🆔 Sizning ID: `{msg.chat.id}`", parse_mode="Markdown")

# =====================
# TIL TANLASH
# =====================
@bot.message_handler(func=lambda m: m.text == "🌐 Til / Язык")
def til_menu(msg):
    cid = msg.chat.id
    yangi_user(cid)
    m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row("🇺🇿 O'zbek tili", "🇷🇺 Русский язык")
    bot.send_message(cid, "Tilni tanlang / Выберите язык:", reply_markup=m)

@bot.message_handler(func=lambda m: m.text in ["🇺🇿 O'zbek tili", "🇷🇺 Русский язык"])
def til_tanla(msg):
    cid = msg.chat.id
    yangi_user(cid)
    users[cid]["til"] = "ru" if "Русский" in msg.text else "uz"
    bot.send_message(cid, "✅ O'zbek tili tanlandi!" if users[cid]["til"] == "uz" else "✅ Выбран русский язык!")
    start(msg)

# =====================
# ROL TANLASH
# =====================
@bot.message_handler(func=lambda m: m.text in ["👨‍🎓 O'quvchi", "👨‍🏫 O'qituvchi", "👨‍👩‍👧 Ota-ona"])
def rol_tanla(msg):
    cid = msg.chat.id
    yangi_user(cid)

    if "O'quvchi" in msg.text:
        users[cid]["rol"] = "oquvchi"
        m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        for s in SINFLAR:
            m.add(s)
        bot.send_message(cid, t(cid, "📚 Sinfingizni tanlang:", "📚 Выберите ваш класс:"), reply_markup=m)

    elif "O'qituvchi" in msg.text:
        users[cid]["rol"] = "oquvchi"
        m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        for s in SINFLAR:
            m.add(s)
        m.add("📊 Umumiy hisobot")
        bot.send_message(cid, "👨‍🏫 Qaysi sinfni kuzatmoqchisiz?\n\nYoki umumiy hisobotni ko'ring:", reply_markup=m)

    elif "Ota-ona" in msg.text:
        users[cid]["rol"] = "otaona"
        m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        m.add("📊 Farzand natijasi", "🔗 Farzandni ulash")
        bot.send_message(cid,
            "👨‍👩‍👧 *Ota-ona paneli*\n\n"
            "Farzandingizni ulash uchun:\n"
            "1. Farzandingiz botga `/myid` yuborgani kerak\n"
            "2. Siz o'sha ID ni yuboring\n\n"
            "Yoki natijalarni ko'ring:",
            reply_markup=m, parse_mode="Markdown")

# =====================
# OTA-ONA PANELI
# =====================
@bot.message_handler(func=lambda m: m.text == "🔗 Farzandni ulash")
def farzand_ulash(msg):
    cid = msg.chat.id
    users[cid]["kutish"] = "farzand_id"
    bot.send_message(cid, "Farzandingizning ID sini yuboring:\n(Farzandingiz /myid yuborgandan keyin chiqadi)")

@bot.message_handler(func=lambda m: m.text == "📊 Farzand natijasi")
def farzand_natija(msg):
    cid = msg.chat.id
    b_cid = parents.get(cid)
    if not b_cid:
        bot.send_message(cid, "❌ Hali farzandingiz ulanmagan.\n🔗 Farzandni ulash tugmasini bosing!")
        return
    ball = users.get(b_cid, {}).get("ball", 0)
    sinf = users.get(b_cid, {}).get("sinf", "?")
    fan = users.get(b_cid, {}).get("fan", "?")
    savollar = users.get(b_cid, {}).get("savollar", 0)
    testlar = users.get(b_cid, {}).get("testlar", 0)
    bot.send_message(cid,
        f"👶 *Farzandingizning natijasi:*\n\n"
        f"🎓 Sinf: {sinf}\n"
        f"📖 Fan: {fan}\n"
        f"⭐ Ball: {ball}\n"
        f"📝 Savollar: {savollar}\n"
        f"✅ Testlar: {testlar}\n"
        f"{daraja(ball)}",
        parse_mode="Markdown")

# =====================
# O'QITUVCHI HISOBOTI
# =====================
@bot.message_handler(func=lambda m: m.text == "📊 Umumiy hisobot")
def umumiy_hisobot(msg):
    cid = msg.chat.id
    if not results:
        bot.send_message(cid, "📊 Hali hech qanday ma'lumot yo'q.")
        return
    txt = "📊 *Umumiy hisobot:*\n\n"
    for sinf, fanlar in results.items():
        txt += f"🎓 *{sinf}:*\n"
        for fan, data in fanlar.items():
            if data:
                eng_yaxshi = max(data, key=lambda x: x["ball"])
                txt += f"  📖 {fan}: {len(data)} o'quvchi, eng yuqori: {eng_yaxshi['ball']} ball\n"
    bot.send_message(cid, txt, parse_mode="Markdown")

# =====================
# SINF TANLASH
# =====================
@bot.message_handler(func=lambda m: m.text in SINFLAR)
def sinf_tanla(msg):
    cid = msg.chat.id
    yangi_user(cid)
    users[cid]["sinf"] = msg.text

    if users[cid].get("rol") == "oquvchi":
        m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for f in FANLAR:
            m.add(f)
        bot.send_message(cid, t(cid, f"✅ {msg.text} tanlandi!\n\n📖 Fanni tanlang:", f"✅ {msg.text} выбран!\n\n📖 Выберите предмет:"), reply_markup=m)
    else:
        # O'qituvchi uchun sinf hisoboti
        sinf = msg.text
        if sinf not in results or not results[sinf]:
            bot.send_message(cid, f"📊 {sinf} uchun hali ma'lumot yo'q.")
            return
        txt = f"📊 *{sinf} hisoboti:*\n\n"
        for fan, data in results[sinf].items():
            if data:
                txt += f"📖 *{fan}:*\n"
                srt = sorted(data, key=lambda x: x["ball"], reverse=True)
                for i, o in enumerate(srt[:5], 1):
                    txt += f"  {i}. {o['nom']} — {o['ball']} ball {daraja(o['ball'])}\n"
        bot.send_message(cid, txt, parse_mode="Markdown")

# =====================
# FAN TANLASH
# =====================
@bot.message_handler(func=lambda m: m.text in FANLAR)
def fan_tanla(msg):
    cid = msg.chat.id
    yangi_user(cid)
    users[cid]["fan"] = msg.text
    sinf = users[cid].get("sinf", "")
    m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("📝 Test ishlash", "🏆 Reytingim", "📊 Statistika", "🔄 O'zgartirish")
    bot.send_message(cid,
        t(cid,
            f"🎯 *{sinf} — {msg.text}*\n\n✅ Tayyor!\n\nSavolingizni yuboring yoki test ishlang! 💬",
            f"🎯 *{sinf} — {msg.text}*\n\n✅ Готово!\n\nЗадайте вопрос или пройдите тест! 💬"),
        reply_markup=m, parse_mode="Markdown")

# =====================
# TEST
# =====================
@bot.message_handler(func=lambda m: m.text == "📝 Test ishlash")
def test_bosla(msg):
    cid = msg.chat.id
    sinf = users.get(cid, {}).get("sinf", "")
    fan = users.get(cid, {}).get("fan", "")
    if not sinf or not fan:
        start(msg)
        return
    bot.send_chat_action(cid, "typing")
    til_txt = "O'zbek tilida" if til(cid) == "uz" else "На русском языке"
    try:
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"Sen o'qituvchisan. {sinf} o'quvchisi uchun {fan} fanidan 1 ta test savol ber. {til_txt}. A, B, C, D javob variantlari bilan. Oxirida: 'To'g'ri javob: X' deb yoz."},
                {"role": "user", "content": "Test savol ber"}
            ],
            max_tokens=600)
        javob = r.choices[0].message.content
        bot.send_message(cid, f"📝 *Test:*\n\n{javob}", parse_mode="Markdown")
        users[cid]["ball"] = users[cid].get("ball", 0) + 10
        users[cid]["testlar"] = users[cid].get("testlar", 0) + 1
        natija_saqlash(cid)
    except Exception as e:
        bot.send_message(cid, "❌ Xatolik yuz berdi. Qayta urinib ko'ring!")

# =====================
# REYTING
# =====================
@bot.message_handler(func=lambda m: m.text == "🏆 Reytingim")
def reyting(msg):
    cid = msg.chat.id
    ball = users.get(cid, {}).get("ball", 0)
    sinf = users.get(cid, {}).get("sinf", "?")
    fan = users.get(cid, {}).get("fan", "?")
    savollar = users.get(cid, {}).get("savollar", 0)
    testlar = users.get(cid, {}).get("testlar", 0)

    # Sinf reytingi
    sinf_txt = ""
    if sinf in results:
        barcha = []
        for f_data in results[sinf].values():
            for o in f_data:
                mavjud = False
                for b in barcha:
                    if b["cid"] == o["cid"]:
                        b["ball"] += o["ball"]
                        mavjud = True
                        break
                if not mavjud:
                    barcha.append({"cid": o["cid"], "ball": o["ball"], "nom": o["nom"]})
        barcha.sort(key=lambda x: x["ball"], reverse=True)
        sinf_txt = f"\n🏫 *{sinf} reytingi:*\n"
        for i, o in enumerate(barcha[:5], 1):
            marker = "👉 " if o["cid"] == cid else ""
            sinf_txt += f"{marker}{i}. {o['nom']} — {o['ball']} ball\n"

    bot.send_message(cid,
        f"🏆 *Sizning natijangiz:*\n\n"
        f"🎓 {sinf} — {fan}\n"
        f"⭐ Ball: {ball}\n"
        f"📝 Savollar: {savollar}\n"
        f"✅ Testlar: {testlar}\n"
        f"{daraja(ball)}"
        f"{sinf_txt}",
        parse_mode="Markdown")

# =====================
# STATISTIKA
# =====================
@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def statistika(msg):
    cid = msg.chat.id
    ball = users.get(cid, {}).get("ball", 0)
    sinf = users.get(cid, {}).get("sinf", "?")
    fan = users.get(cid, {}).get("fan", "?")
    savollar = users.get(cid, {}).get("savollar", 0)
    testlar = users.get(cid, {}).get("testlar", 0)
    bot.send_message(cid,
        f"📊 *Statistika:*\n\n"
        f"🎓 Sinf: {sinf}\n"
        f"📖 Fan: {fan}\n"
        f"⭐ Umumiy ball: {ball}\n"
        f"📝 Berilgan savollar: {savollar}\n"
        f"✅ Ishlangan testlar: {testlar}\n"
        f"🏅 Daraja: {daraja(ball)}\n"
        f"📅 Sana: {datetime.now().strftime('%d.%m.%Y')}",
        parse_mode="Markdown")

# =====================
# O'ZGARTIRISH
# =====================
@bot.message_handler(func=lambda m: m.text == "🔄 O'zgartirish")
def ozgartirish(msg):
    start(msg)

# =====================
# ASOSIY JAVOB
# =====================
@bot.message_handler(func=lambda m: True)
def javob(msg):
    cid = msg.chat.id
    yangi_user(cid)

    # Ota-ona farzand ID kiritayaptimi
    if users[cid].get("kutish") == "farzand_id":
        try:
            b_id = int(msg.text.strip())
            parents[cid] = b_id
            users[cid]["kutish"] = None
            bot.send_message(cid, f"✅ Farzandingiz (ID: {b_id}) ulandi!\nEndi natijalar avtomatik yuboriladi.")
        except:
            bot.send_message(cid, "❌ Noto'g'ri ID. Farzandingiz /myid yuborganini tekshiring.")
        return

    sinf = users[cid].get("sinf", "")
    fan = users[cid].get("fan", "")

    if not sinf or not fan:
        start(msg)
        return

    bot.send_chat_action(cid, "typing")
    til_txt = "O'zbek tilida, to'liq va batafsil" if til(cid) == "uz" else "На русском языке, подробно и полно"

    try:
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": (
                    f"Sen EduBot — O'zbekiston maktab o'quvchilari uchun AI o'qituvchisan.\n"
                    f"O'quvchi: {sinf}, fan: {fan}.\n"
                    f"{til_txt} javob ber.\n\n"
                    f"MUHIM QOIDALAR:\n"
                    f"1. FAQAT {fan} faniga oid savollarga javob ber\n"
                    f"2. Agar savol {fan} ga oid bo'lmasa: 'Kechirasiz, men faqat {fan} fanidan yordam bera olaman' de\n"
                    f"3. Hech qachon noto'g'ri ma'lumot berma — bilmasang 'Bu mavzuni o'qituvchingizdan so'rang' de\n"
                    f"4. Faqat O'zbekiston maktab dasturiga mos ma'lumot ber\n"
                    f"5. To'liq va batafsil tushuntir, misollar va formulalar keltir\n"
                    f"6. Bosqichma-bosqich tushuntir\n"
                    f"7. O'quvchini doim rag'batlantirib tur"
                )},
                {"role": "user", "content": msg.text}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        bot.send_message(cid, r.choices[0].message.content)
        users[cid]["ball"] = users[cid].get("ball", 0) + 5
        users[cid]["savollar"] = users[cid].get("savollar", 0) + 1
        natija_saqlash(cid)
    except:
        bot.send_message(cid, t(cid, "❌ Xatolik yuz berdi. Qayta urinib ko'ring!", "❌ Произошла ошибка. Попробуйте ещё раз!"))

# =====================
# WEBHOOK
# =====================
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route('/')
def index():
    return "EduBot ishlayapti! 🚀", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{TELEGRAM_TOKEN}")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
