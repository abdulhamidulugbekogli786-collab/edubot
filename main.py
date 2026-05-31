import telebot
from groq import Groq
from flask import Flask, request
import os
from datetime import datetime

TELEGRAM_TOKEN = "8326889206:AAGtg2O0f4kYPpG7i2yh1CW-ydu2-n3ioPE"
GROQ_API_KEY = "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"
RENDER_URL = "https://edubot-zj5y.onrender.com"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

users = {}
results = {}
parents = {}
test_javoblar = {}

SINFLAR = ["1-sinf","2-sinf","3-sinf","4-sinf","5-sinf","6-sinf","7-sinf","8-sinf","9-sinf","10-sinf","11-sinf"]
FANLAR = ["Matematika","Algebra","Geometriya","Fizika","Kimyo","Biologiya","Ona tili","Adabiyot","Rus tili","Ingliz tili","Tarix","Geografiya","Informatika","Chizmachilik","Texnologiya","Jismoniy tarbiya","Musiqa","Tasviriy san'at"]
DARAJALAR = {900:"🥇 A'lochi",700:"🥈 Yaxshi",500:"🥉 Muvaffaqiyatli",300:"📈 Rivojlanmoqda",0:"💪 Harakat kerak"}

def daraja(ball):
    for chegara, nom in sorted(DARAJALAR.items(), reverse=True):
        if ball >= chegara:
            return nom
    return "💪 Harakat kerak"

def til(cid): return users.get(cid,{}).get("til","uz")
def t(cid,uz,ru): return ru if til(cid)=="ru" else uz

def yangi_user(cid):
    if cid not in users:
        users[cid] = {"rol":None,"sinf":None,"fan":None,"til":"uz","ball":0,"savollar":0,"testlar":0,"kutish":None}

def natija_saqlash(cid):
    sinf = users.get(cid,{}).get("sinf")
    fan = users.get(cid,{}).get("fan")
    ball = users.get(cid,{}).get("ball",0)
    nom = users.get(cid,{}).get("nom", f"Foydalanuvchi {cid}")
    if not sinf or not fan: return
    if sinf not in results: results[sinf] = {}
    if fan not in results[sinf]: results[sinf][fan] = []
    topildi = False
    for o in results[sinf][fan]:
        if o["cid"] == cid:
            o["ball"] = ball
            o["nom"] = nom
            topildi = True
            break
    if not topildi:
        results[sinf][fan].append({"cid":cid,"ball":ball,"nom":nom,"sana":datetime.now().strftime("%d.%m.%Y")})
    for p_cid, b_cid in parents.items():
        if b_cid == cid:
            try:
                bot.send_message(p_cid, f"📊 Farzandingiz *{nom}*\n🎓 {sinf} — {fan}\n⭐ Ball: {ball}\n{daraja(ball)}", parse_mode="Markdown")
            except: pass

@bot.message_handler(commands=['start'])
def start(msg):
    cid = msg.chat.id
    yangi_user(cid)
    m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("👨‍🎓 O'quvchi","👨‍🏫 O'qituvchi","👨‍👩‍👧 Ota-ona","🌐 Til / Язык")
    bot.send_message(cid,
        "👋 *EduBot*ga xush kelibsiz!\n\n"
        "📱 O'zbekiston o'quvchilari uchun AI o'qituvchi\n\n"
        "Rolni tanlang:",
        reply_markup=m, parse_mode="Markdown")

@bot.message_handler(commands=['myid'])
def myid(msg):
    bot.send_message(msg.chat.id, f"🆔 Sizning ID: `{msg.chat.id}`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🌐 Til / Язык")
def til_menu(msg):
    cid = msg.chat.id
    yangi_user(cid)
    m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row("🇺🇿 O'zbek tili","🇷🇺 Русский язык")
    bot.send_message(cid, "Tilni tanlang / Выберите язык:", reply_markup=m)

@bot.message_handler(func=lambda m: m.text in ["🇺🇿 O'zbek tili","🇷🇺 Русский язык"])
def til_tanla(msg):
    cid = msg.chat.id
    yangi_user(cid)
    users[cid]["til"] = "ru" if "Русский" in msg.text else "uz"
    bot.send_message(cid, "✅ O'zbek tili tanlandi!" if users[cid]["til"]=="uz" else "✅ Выбран русский язык!")
    start(msg)

@bot.message_handler(func=lambda m: m.text in ["👨‍🎓 O'quvchi","👨‍🏫 O'qituvchi","👨‍👩‍👧 Ota-ona"])
def rol_tanla(msg):
    cid = msg.chat.id
    yangi_user(cid)
    if "O'quvchi" in msg.text:
        users[cid]["rol"] = "oquvchi"
        m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
        for s in SINFLAR: m.add(s)
        bot.send_message(cid, t(cid,"📚 Sinfingizni tanlang:","📚 Выберите ваш класс:"), reply_markup=m)
    elif "O'qituvchi" in msg.text:
        users[cid]["rol"] = "oquvchi"
        m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
        for s in SINFLAR: m.add(s)
        m.add("📊 Umumiy hisobot")
        bot.send_message(cid, "👨‍🏫 Qaysi sinfni kuzatmoqchisiz?", reply_markup=m)
    elif "Ota-ona" in msg.text:
        users[cid]["rol"] = "otaona"
        m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        m.row("📊 Farzand natijasi","🔗 Farzandni ulash")
        bot.send_message(cid,
            "👨‍👩‍👧 *Ota-ona paneli*\n\n"
            "Farzandingizni ulash:\n"
            "1. Farzandingiz botga /myid yuborgani kerak\n"
            "2. Siz o'sha ID ni yuboring",
            reply_markup=m, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔗 Farzandni ulash")
def farzand_ulash(msg):
    cid = msg.chat.id
    yangi_user(cid)
    users[cid]["kutish"] = "farzand_id"
    bot.send_message(cid, "Farzandingizning ID sini yuboring:")

@bot.message_handler(func=lambda m: m.text == "📊 Farzand natijasi")
def farzand_natija(msg):
    cid = msg.chat.id
    b_cid = parents.get(cid)
    if not b_cid:
        bot.send_message(cid, "❌ Farzandingiz hali ulanmagan.\n🔗 Farzandni ulash tugmasini bosing!")
        return
    ball = users.get(b_cid,{}).get("ball",0)
    sinf = users.get(b_cid,{}).get("sinf","?")
    fan = users.get(b_cid,{}).get("fan","?")
    savollar = users.get(b_cid,{}).get("savollar",0)
    testlar = users.get(b_cid,{}).get("testlar",0)
    bot.send_message(cid,
        f"👶 *Farzandingizning natijasi:*\n\n"
        f"🎓 Sinf: {sinf}\n📖 Fan: {fan}\n⭐ Ball: {ball}\n"
        f"📝 Savollar: {savollar}\n✅ Testlar: {testlar}\n{daraja(ball)}",
        parse_mode="Markdown")

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
                eng = max(data, key=lambda x: x["ball"])
                txt += f"  📖 {fan}: {len(data)} o'quvchi | Top: {eng['nom']} — {eng['ball']} ball\n"
    bot.send_message(cid, txt, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in SINFLAR)
def sinf_tanla(msg):
    cid = msg.chat.id
    yangi_user(cid)
    users[cid]["sinf"] = msg.text
    if users[cid].get("rol") == "oquvchi" and cid not in [k for k,v in users.items() if v.get("rol")=="oquvchi" and not v.get("fan")]:
        pass
    m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for f in FANLAR: m.add(f)
    bot.send_message(cid, t(cid,f"✅ {msg.text} tanlandi!\n\n📖 Fanni tanlang:",f"✅ {msg.text} выбран!\n\n📖 Выберите предмет:"), reply_markup=m)

@bot.message_handler(func=lambda m: m.text in FANLAR)
def fan_tanla(msg):
    cid = msg.chat.id
    yangi_user(cid)
    users[cid]["fan"] = msg.text
    sinf = users[cid].get("sinf","")
    m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add("📝 Test ishlash","🏆 Reytingim","📊 Statistika","🔄 O'zgartirish")
    bot.send_message(cid,
        t(cid,
            f"🎯 *{sinf} — {msg.text}*\n\n✅ Tayyor! Savolingizni yuboring yoki test ishlang! 💬",
            f"🎯 *{sinf} — {msg.text}*\n\n✅ Готово! Задайте вопрос или пройдите тест! 💬"),
        reply_markup=m, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📝 Test ishlash")
def test_bosla(msg):
    cid = msg.chat.id
    sinf = users.get(cid,{}).get("sinf","")
    fan = users.get(cid,{}).get("fan","")
    if not sinf or not fan:
        start(msg); return
    bot.send_chat_action(cid, "typing")
    til_txt = "O'zbek tilida" if til(cid)=="uz" else "На русском языке"
    try:
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":f"Sen o'qituvchisan. {sinf} o'quvchisi uchun {fan} fanidan 1 ta test savol ber. {til_txt}. Faqat savol va A, B, C, D javob variantlarini ber. To'g'ri javobni HECH QACHON ko'rsatma — yashirin tut. Oxirida faqat: 'Javobingizni yuboring! (A, B, C yoki D)' deb yoz."},
                {"role":"user","content":"Test savol ber"}
            ],
            max_tokens=500)
        javob = r.choices[0].message.content
        test_javoblar[cid] = {"savol": javob, "fan": fan, "sinf": sinf}
        users[cid]["kutish"] = "test_javob"
        bot.send_message(cid, f"📝 *Test:*\n\n{javob}", parse_mode="Markdown")
    except:
        bot.send_message(cid, "❌ Xatolik yuz berdi. Qayta urinib ko'ring!")

@bot.message_handler(func=lambda m: m.text == "🏆 Reytingim")
def reyting(msg):
    cid = msg.chat.id
    ball = users.get(cid,{}).get("ball",0)
    sinf = users.get(cid,{}).get("sinf","?")
    fan = users.get(cid,{}).get("fan","?")
    savollar = users.get(cid,{}).get("savollar",0)
    testlar = users.get(cid,{}).get("testlar",0)
    sinf_txt = ""
    if sinf in results:
        barcha = []
        for f_data in results[sinf].values():
            for o in f_data:
                mavjud = False
                for b in barcha:
                    if b["cid"]==o["cid"]:
                        b["ball"] += o["ball"]; mavjud=True; break
                if not mavjud:
                    barcha.append({"cid":o["cid"],"ball":o["ball"],"nom":o["nom"]})
        barcha.sort(key=lambda x: x["ball"], reverse=True)
        sinf_txt = f"\n🏫 *{sinf} reytingi (Top 5):*\n"
        for i,o in enumerate(barcha[:5],1):
            marker = "👉 " if o["cid"]==cid else ""
            sinf_txt += f"{marker}{i}. {o['nom']} — {o['ball']} ball\n"
    bot.send_message(cid,
        f"🏆 *Sizning natijangiz:*\n\n"
        f"🎓 {sinf} — {fan}\n⭐ Ball: {ball}\n"
        f"📝 Savollar: {savollar}\n✅ Testlar: {testlar}\n{daraja(ball)}{sinf_txt}",
        parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def statistika(msg):
    cid = msg.chat.id
    ball = users.get(cid,{}).get("ball",0)
    sinf = users.get(cid,{}).get("sinf","?")
    fan = users.get(cid,{}).get("fan","?")
    savollar = users.get(cid,{}).get("savollar",0)
    testlar = users.get(cid,{}).get("testlar",0)
    bot.send_message(cid,
        f"📊 *Statistika:*\n\n🎓 Sinf: {sinf}\n📖 Fan: {fan}\n"
        f"⭐ Ball: {ball}\n📝 Savollar: {savollar}\n✅ Testlar: {testlar}\n"
        f"🏅 {daraja(ball)}\n📅 {datetime.now().strftime('%d.%m.%Y')}",
        parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔄 O'zgartirish")
def ozgartirish(msg):
    start(msg)

@bot.message_handler(func=lambda m: True)
def javob(msg):
    cid = msg.chat.id
    yangi_user(cid)

    # Farzand ID kiritish
    if users[cid].get("kutish") == "farzand_id":
        try:
            b_id = int(msg.text.strip())
            parents[cid] = b_id
            users[cid]["kutish"] = None
            bot.send_message(cid, f"✅ Farzandingiz (ID: {b_id}) ulandi!")
        except:
            bot.send_message(cid, "❌ Noto'g'ri ID. /myid buyrug'ini tekshiring.")
        return

    # Test javobi tekshirish
    if users[cid].get("kutish") == "test_javob":
        javob_harf = msg.text.strip().upper()
        if javob_harf in ["A","B","C","D"]:
            users[cid]["kutish"] = None
            bot.send_chat_action(cid, "typing")
            savol_info = test_javoblar.get(cid, {})
            try:
                r = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role":"system","content":f"Sen o'qituvchisan. O'quvchi test savoliga {javob_harf} deb javob berdi. Quyidagi savol va variantlar bo'yicha javobni tekshir va to'g'ri javobni ayt. Agar to'g'ri bo'lsa rag'batlantirib 10 ball bergingizni ayt, noto'g'ri bo'lsa to'g'ri javobni tushuntir."},
                        {"role":"user","content":savol_info.get("savol","") + f"\n\nO'quvchi javobi: {javob_harf}"}
                    ],
                    max_tokens=500)
                natija = r.choices[0].message.content
                if "to'g'ri" in natija.lower() or "правильно" in natija.lower():
                    users[cid]["ball"] = users[cid].get("ball",0) + 10
                users[cid]["testlar"] = users[cid].get("testlar",0) + 1
                natija_saqlash(cid)
                bot.send_message(cid, natija)
            except:
                bot.send_message(cid, "❌ Xatolik. Qayta urinib ko'ring!")
        else:
            bot.send_message(cid, "❗ Faqat A, B, C yoki D harfini yuboring!")
        return

    sinf = users[cid].get("sinf","")
    fan = users[cid].get("fan","")
    if not sinf or not fan:
        start(msg); return

    bot.send_chat_action(cid, "typing")
    til_txt = "O'zbek tilida, to'liq va batafsil" if til(cid)=="uz" else "На русском языке, подробно и полно"
    try:
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":(
                    f"Sen EduBot — O'zbekiston maktab o'quvchilari uchun AI o'qituvchisan.\n"
                    f"O'quvchi: {sinf}, fan: {fan}.\n{til_txt} javob ber.\n\n"
                    f"QOIDALAR:\n"
                    f"1. FAQAT {fan} faniga oid savollarga javob ber\n"
                    f"2. Agar savol {fan} ga oid bo'lmasa: 'Kechirasiz, men faqat {fan} fanidan yordam bera olaman' de\n"
                    f"3. Hech qachon noto'g'ri ma'lumot berma\n"
                    f"4. O'zbekiston maktab dasturiga mos ma'lumot ber\n"
                    f"5. To'liq va batafsil tushuntir, misollar va formulalar keltir\n"
                    f"6. Bosqichma-bosqich tushuntir\n"
                    f"7. O'quvchini doim rag'batlantirib tur"
                )},
                {"role":"user","content":msg.text}
            ],
            max_tokens=2000,
            temperature=0.7)
        bot.send_message(cid, r.choices[0].message.content)
        users[cid]["ball"] = users[cid].get("ball",0) + 5
        users[cid]["savollar"] = users[cid].get("savollar",0) + 1
        natija_saqlash(cid)
    except:
        bot.send_message(cid, t(cid,"❌ Xatolik yuz berdi. Qayta urinib ko'ring!","❌ Произошла ошибка. Попробуйте ещё раз!"))

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
