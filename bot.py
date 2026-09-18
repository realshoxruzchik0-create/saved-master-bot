import telebot
from telebot import types

TOKEN = "8863718138:AAHYnNprSLerPYD6xYiN6qc6bJ6uJWKnXSI"
bot = telebot.TeleBot(TOKEN)

user_balances = {}
user_state = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = 0
        
    text = (
        'Salom, siz <b>NYC SMM XIZMAT</b> botdasiz '
        '<tg-emoji emoji-id="5370941588165893740">✅</tg-emoji>\n\n'
        '🚀 SMM xizmatlari va ijtimoiy tarmoqlar uchun qulay imkoniyatlarimizdan foydalanishingiz mumkin!\n\n'
        'Kerakli bo‘limni tanlang:'
    )
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    order_btn = types.KeyboardButton("📦 Buyurtma berish")
    account_btn = types.KeyboardButton("💳 Hisobim")
    topup_btn = types.KeyboardButton("➕ Hisobni to'ldirish")
    ref_btn = types.KeyboardButton("🔗 Referal havola")
    
    markup.add(order_btn, account_btn)
    markup.add(topup_btn, ref_btn)
    
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)

# 1-QADAM: "📦 Buyurtma berish" bo'limi (Platforma tanlash - logotip emojilari bilan)
@bot.message_handler(func=lambda message: message.text == "📦 Buyurtma berish")
def show_order_options(message):
    user_state[message.chat.id] = {"step": "waiting_for_platform"}
    menu_text = (
        '<tg-emoji emoji-id="5359741159566484212">📦</tg-emoji> <b>Kerakli xizmat turini tanlang:</b>\n\n'
        '<b>Instagram</b> <tg-emoji emoji-id="6136285626233786941">📸</tg-emoji>\n'
        '<b>TikTok</b> <tg-emoji emoji-id="5276297774730598588">🎵</tg-emoji>\n'
        '<b>YouTube</b> <tg-emoji emoji-id="6253477158979635095">▶️</tg-emoji>\n'
        '<b>Telegram</b> <tg-emoji emoji-id="5836877520384824406">✈️</tg-emoji>\n\n'
        '<i>(Iltimos, yuqoridagi platformalardan birining nomini yuboring, masalan: <b>Instagram</b>)</i>'
    )
    bot.send_message(message.chat.id, menu_text, parse_mode="HTML")

# 2-QADAM: Platformani qabul qilib, obunachi turlarini chiqarish
@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get("step") == "waiting_for_platform")
def process_platform(message):
    platform = message.text.strip().capitalize()
    platforms_list = ["Instagram", "Tiktok", "Youtube", "Telegram"]
    
    if platform not in platforms_list:
        bot.send_message(message.chat.id, "❌ Iltimos, faqat tugmalardagi platforma nomini yuboring (masalan: <code>Instagram</code>):", parse_mode="HTML")
        return
    
    user_state[message.chat.id] = {"step": "waiting_for_service", "platform": platform}
    
    services_text = (
        f'<b>{platform} uchun xizmat turi:</b>\n\n'
        '<tg-emoji emoji-id="5316727448644103237">👥</tg-emoji> <b>Vip Obunachi</b> <tg-emoji emoji-id="5316727448644103237">👥</tg-emoji>\n'
        '<tg-emoji emoji-id="5316727448644103237">👥</tg-emoji> <b>Odiy Obunachi</b> <tg-emoji emoji-id="5316727448644103237">👥</tg-emoji>\n'
        '<tg-emoji emoji-id="5316727448644103237">👥</tg-emoji> <b>Arzon Obunachi</b> <tg-emoji emoji-id="5316727448644103237">👥</tg-emoji>\n\n'
        '<i>(Yuqoridagilardan birini yozing, masalan: <b>Vip Obunachi</b>)</i>'
    )
    bot.send_message(message.chat.id, services_text, parse_mode="HTML")

# 3-QADAM: Obunachi turini qabul qilib, miqdor so'rash
@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get("step") == "waiting_for_service")
def process_service(message):
    service_text = message.text.strip().title()
    valid_services = ["Vip Obunachi", "Odiy Obunachi", "Arzon Obunachi"]
    
    if service_text not in valid_services:
        bot.send_message(message.chat.id, "❌ Iltimos, ro'yxatdagilardan birini to'g'ri yuboring (masalan: <code>Vip Obunachi</code>):", parse_mode="HTML")
        return
    
    data = user_state[message.chat.id]
    data["step"] = "waiting_for_amount"
    data["service"] = service_text
    
    bot.send_message(message.chat.id, f"<b>{service_text}</b> tanlandi ✅\n\nQancha miqdorda obunachi kerakligini raqamlarda kiriting (masalan: 10):", parse_mode="HTML")

# 4-QADAM: Miqdorni hisoblab, balansni tekshirish
@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get("step") == "waiting_for_amount")
def process_order_amount(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "❌ Iltimos, faqat raqamlarda miqdor kiriting:")
        return
    
    count = int(message.text)
    if count <= 0:
        bot.send_message(message.chat.id, "❌ Miqdor 0 dan ko'p bo'lishi kerak. Qaytadan kiriting:")
        return
        
    data = user_state.pop(message.chat.id, None)
    service = data["service"]
    
    # Narxlarni belgilash
    if service == "Vip Obunachi":
        price_per_item = 1900
    elif service == "Odiy Obunachi":
        price_per_item = 680
    else:  # Arzon Obunachi
        price_per_item = 450
        
    total_price = count * price_per_item
    user_id = message.from_user.id
    current_balance = user_balances.get(user_id, 0)
    
    # Balansni tekshirish
    if current_balance < total_price:
        error_msg = (
            f'<b>Xizmat:</b> {service}\n'
            f'<b>Miqdori:</b> {count} ta\n'
            f'<b>Umumiy narx:</b> {total_price:,} soʻm\n\n'
            '❌ <b>Hisobingizda yetarli mablagʻ yoʻq!</b> <tg-emoji emoji-id="5370941588165893740">✅</tg-emoji>'
        )
        bot.send_message(message.chat.id, error_msg, parse_mode="HTML")
    else:
        success_msg = (
            f'<b>Xizmat:</b> {service}\n'
            f'<b>Miqdori:</b> {count} ta\n'
            f'<b>Umumiy narx:</b> {total_price:,} soʻm\n\n'
            '✅ <b>Buyurtma muvaffaqiyatli qabul qilindi!</b>'
        )
        bot.send_message(message.chat.id, success_msg, parse_mode="HTML")

# "💳 Hisobim" bo'limi
@bot.message_handler(func=lambda message: message.text == "💳 Hisobim")
def show_account_info(message):
    user_id = message.from_user.id
    balance = user_balances.get(user_id, 0)
    
    account_text = (
        '<tg-emoji emoji-id="5197503331215361533">💳</tg-emoji> <b>Sizning shaxsiy hisobingiz:</b>\n\n'
        f"👤 <b>Foydalanuvchi:</b> {message.from_user.first_name}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"💰 <b>Balans:</b> {balance:,} so'm\n"
        "📊 <b>Buyurtmalar soni:</b> 0 ta"
    )
    bot.send_message(message.chat.id, account_text, parse_mode="HTML")

# "➕ Hisobni to'ldirish" tugmasi bosilganda
@bot.message_handler(func=lambda message: message.text == "➕ Hisobni to'ldirish")
def ask_topup_amount(message):
    user_state[message.chat.id] = {"step": "waiting_for_topup"}
    msg = (
        '💳 <b>Hisobni toʻldirish</b>\n\n'
        'Hisobingizni toʻldirmoqchi boʻlgan summani kiriting:\n'
        '<i>(Minimal: 1 000 soʻm, Maksimal: 200 000 soʻm)</i>'
    )
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

# Summani qabul qilib olib, rekvizitlarni chiqarish
@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get("step") == "waiting_for_topup")
def process_topup_amount(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "❌ Iltimos, faqat raqamlarda summa kiriting (masalan: 10000):")
        return
    
    amount = int(message.text)
    
    if amount < 1000:
        bot.send_message(message.chat.id, "❌ Minimal to'ldirish miqdori **1 000 so'm**. Qaytadan kiriting:", parse_mode="HTML")
        return
    
    if amount > 200000:
        bot.send_message(message.chat.id, "❌ Maksimal to'ldirish miqdori **200 000 so'm**. Qaytadan kiriting:", parse_mode="HTML")
        return
    
    user_state.pop(message.chat.id, None)
    
    topup_text = (
        f'<b>Kiritilgan summa:</b> {amount:,} soʻm <tg-emoji emoji-id="5370941588165893740">✅</tg-emoji>\n\n'
        '<b>Hisobni toʻldirish uchun rekvizitlar:</b>\n\n'
        '<b>Karta turi:</b> Humo avto <tg-emoji emoji-id="5386365640359567570">💳</tg-emoji> <tg-emoji emoji-id="5370941588165893740">✅</tg-emoji>\n'
        '<b>Karta raqami:</b> <code>9860606758657385</code> <tg-emoji emoji-id="5370941588165893740">✅</tg-emoji>\n'
        '<b>Karta egasi:</b> Xolboyeva.S <tg-emoji emoji-id="5258011929993026890">👤</tg-emoji> <tg-emoji emoji-id="5370941588165893740">✅</tg-emoji>\n\n'
        '<i>Pulni oʻtkazgandan soʻng, chekni adminlarga yuboring va balansingizga qoʻshib beriladi!</i>'
    )
    bot.send_message(message.chat.id, topup_text, parse_mode="HTML")

# "🔗 Referal havola" bo'limi
@bot.message_handler(func=lambda message: message.text == "🔗 Referal havola")
def show_referral_link(message):
    bot_username = bot.get_me().username
    user_id = message.from_user.id
    ref_link = f"https://t.me/{bot_username}?start={user_id}"
    
    ref_text = (
        '🤝 <b>Referal dasturi</b>\n\n'
        'Do\'stlaringizni taklif qiling va har bir taklif qilingan do\'stingiz uchun balansingizga <b>200 so\'m</b> qo\'shib oling!\n\n'
        f'Sizning silkangiz <tg-emoji emoji-id="5260450573768990626">↗️</tg-emoji>: \n<code>{ref_link}</code>\n\n'
        '<i>Ushbu havolani do\'stlaringizga yuboring!</i>'
    )
    bot.send_message(message.chat.id, ref_text, parse_mode="HTML")

print("NYC SMM XIZMAT boti ishga tushdi...")
bot.infinity_polling()
