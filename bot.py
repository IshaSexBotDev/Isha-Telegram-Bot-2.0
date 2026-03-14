import telebot
from telebot import types
import random

# --- සැකසුම් (Settings) ---
API_TOKEN = '8610855532:AAGXbazbop18st9N_ueScO9ekTsgeO7UJHA'
bot = telebot.TeleBot(API_TOKEN)

# මෙහි දත්ත තාවකාලිකව ගබඩා වේ (සර්වර් එක Restart වූ විට මෙය Reset වේ)
# වඩාත් ස්ථිරව තබා ගැනීමට පසුව Google Sheets සම්බන්ධ කරමු.
media_data = {
    'video': [],
    'image': [],
    'gif': [],
    'j_movie': []
}

user_history = {}

# --- බොට්ගේ ක්‍රියාකාරීත්වය ---

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = [
        types.KeyboardButton("Video 🎥"),
        types.KeyboardButton("Image 🖼️"),
        types.KeyboardButton("GIFs ⚡"),
        types.KeyboardButton("Japan Movie 🇯🇵"),
        types.KeyboardButton("Upload Mode 📤")
    ]
    markup.add(*btns)
    bot.send_message(message.chat.id, "සාදරයෙන් පිළිගන්න! ඔබට අවශ්‍ය දේ තෝරන්න:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.from_user.id
    choice = message.text

    category_map = {
        "Video 🎥": "video",
        "Image 🖼️": "image",
        "GIFs ⚡": "gif",
        "Japan Movie 🇯🇵": "j_movie"
    }

    if choice in category_map:
        cat = category_map[choice]
        all_files = media_data[cat]
        
        if not all_files:
            bot.send_message(message.chat.id, "සමාවන්න, තවමත් මේ ගොනුවට දත්ත ඇතුළත් කර නැත.")
            return

        # කලින් නොබලපු ඒවා සෙවීම
        seen = user_history.get(user_id, {}).get(cat, [])
        unseen = [f for f in all_files if f not in seen]

        if not unseen:
            # සියල්ල නරඹා ඇත්නම් නැවත මුල සිට පෙන්වීමට History එක Clear කරයි
            user_history[user_id][cat] = []
            unseen = all_files
            bot.send_message(message.chat.id, "ඔබ සියල්ල නරඹා අවසන්. නැවත මුල සිට පෙන්වයි...")

        selected_file = random.choice(unseen)

        # File එක යැවීම
        if cat == "video" or cat == "j_movie":
            bot.send_video(message.chat.id, selected_file)
        elif cat == "image":
            bot.send_photo(message.chat.id, selected_file)
        elif cat == "gif":
            bot.send_animation(message.chat.id, selected_file)

        # History එකට එකතු කිරීම
        if user_id not in user_history: user_history[user_id] = {}
        if cat not in user_history[user_id]: user_history[user_id][cat] = []
        user_history[user_id][cat].append(selected_file)

    elif choice == "Upload Mode 📤":
        bot.send_message(message.chat.id, "දැන් මට ඕනෑම Media එකක් එවන්න. මම එය Database එකට එක් කරගන්නම්.")

# Media ලබාගෙන Database එකට දැමීම (ඔබ විසින් පමණක් කළ යුතුය)
@bot.message_handler(content_types=['video', 'photo', 'animation'])
def auto_upload(message):
    file_id = ""
    category = ""

    if message.video:
        file_id = message.video.file_id
        category = "video"
    elif message.photo:
        file_id = message.photo[-1].file_id
        category = "image"
    elif message.animation:
        file_id = message.animation.file_id
        category = "gif"

    if file_id:
        media_data[category].append(file_id)
        bot.reply_to(message, f"සාර්ථකව {category} ගොනුව එක් කරන ලදී! ✅")

bot.polling()
