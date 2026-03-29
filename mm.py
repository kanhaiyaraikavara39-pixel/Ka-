import os
import sys
import time
import subprocess
import threading
import random

# --- १. ऑटो इंस्टॉलर ---
def install_requirements():
    required = ["pyTelegramBotAPI", "instagrapi", "requests", "Pillow"]
    for package in required:
        try:
            if package == "pyTelegramBotAPI": import telebot
            else: __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_requirements()

import telebot
from telebot import types
from instagrapi import Client

# --- २. सेटिंग्स ---
API_TOKEN = '8642737538:AAEZeFzobubyQX9XpJduqUOQ1Z1GOgnikTo'
ADMIN_ID = 8555060319

bot = telebot.TeleBot(API_TOKEN)
cl = Client()
SESSION_FILE = "insta_session.json"
VAULT_FOLDER = "media_vault"

if not os.path.exists(VAULT_FOLDER): os.makedirs(VAULT_FOLDER)

# --- ३. हर मिनट पोस्ट करने वाला लॉजिक (Non-Stop) ---

def non_stop_posting_loop():
    print("🚀 हर मिनट पोस्टिंग वाला सिस्टम चालू हो गया है...")
    while True:
        try:
            # फोल्डर से फाइलें चेक करना
            files = [f for f in os.listdir(VAULT_FOLDER) if f.lower().endswith(('.mp4', '.jpg', '.jpeg', '.png'))]
            
            if not files:
                print("⚠️ तिजोरी खाली है! कृपया टेलीग्राम पर वीडियो या फोटो भेजें।")
            else:
                # रैंडम फाइल चुनना
                chosen_file = random.choice(files)
                path = os.path.join(VAULT_FOLDER, chosen_file)
                
                caption = f"🚩 जय श्री राम! 🔥\nOwner: @kanhaiya.raikwar77\n#Sanatan #Gaming #Modi #ReelsIndia"
                
                print(f"📤 पोस्ट किया जा रहा है: {chosen_file}")
                
                if path.lower().endswith(".mp4"):
                    cl.clip_upload(path, caption)
                else:
                    cl.photo_upload(path, caption)
                
                print(f"✅ सफलतापूर्वक पोस्ट हुआ! अब १ मिनट का इंतज़ार...")

            # ठीक ६० सेकंड (१ मिनट) का गैप
            time.sleep(60) 
            
        except Exception as e:
            print(f"⚠️ पोस्टिंग एरर: {str(e)[:50]}... ५ सेकंड में फिर कोशिश करेंगे।")
            time.sleep(5)

# --- ४. टेलीग्राम कंट्रोल और बटन ---

@bot.message_handler(commands=['start'])
def welcome(message):
    if message.from_user.id != ADMIN_ID: return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # बटन जोड़े गए हैं
    markup.add("🔑 Real Login", "📊 Check Status")
    bot.send_message(message.chat.id, "🚩 कन्हैया भाई, बोट तैयार है!\n\n'Check Status' से ऑनलाइन देखें और वीडियो भेजकर पोस्टिंग चालू करें।", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📊 Check Status")
def check_bot_status(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        if cl.user_id:
            me = cl.account_info()
            bot.send_message(message.chat.id, f"✅ **बोट ऑनलाइन है!**\n👤 आईडी: {me.username}\n🚀 मोड: हर मिनट पोस्टिंग चालू है।")
        else:
            bot.send_message(message.chat.id, "❌ बोट अभी लॉगिन नहीं है। 'Real Login' दबाएं।")
    except:
        bot.send_message(message.chat.id, "❌ बोट ऑफलाइन है या लॉगिन फेल हो गया है।")

@bot.message_handler(func=lambda m: m.text == "🔑 Real Login")
def start_login(message):
    msg = bot.send_message(message.chat.id, "अपनी आईडी भेजें (user:pass):")
    bot.register_next_step_handler(msg, process_login)

def process_login(message):
    try:
        u, p = message.text.split(":")
        cl.login(u.strip(), p.strip())
        cl.dump_settings(SESSION_FILE)
        bot.send_message(message.chat.id, "✅ लॉगिन सफल! अब हर मिनट पोस्टिंग शुरू हो रही है।")
        
        # पोस्टिंग लूप को बैकग्राउंड में शुरू करें
        threading.Thread(target=non_stop_posting_loop, daemon=True).start()
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ फेल: {str(e)[:100]}")

@bot.message_handler(content_types=['video', 'photo'])
def save_files(message):
    if message.from_user.id != ADMIN_ID: return
    file_id = message.video.file_id if message.content_type == 'video' else message.photo[-1].file_id
    ext = ".mp4" if message.content_type == 'video' else ".jpg"
    
    file_info = bot.get_file(file_id)
    data = bot.download_file(file_info.file_path)
    
    path = os.path.join(VAULT_FOLDER, f"post_{int(time.time())}{ext}")
    with open(path, 'wb') as f: f.write(data)
    bot.send_message(message.chat.id, "📥 फाइल तिजोरी में सेव हो गई! यह अब हर मिनट पोस्ट होती रहेगी।")

if __name__ == "__main__":
    bot.polling(none_stop=True)
