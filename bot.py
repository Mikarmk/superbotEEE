import config
import telebot
from database import create_database, save_file_info, get_user_files
from typing import NoReturn
import os

create_database()

bot = telebot.TeleBot(config.token)

def show_help(message: telebot.types.Message) -> NoReturn:
    help_text = "Доступные команды:\n"
    help_text += "/help - Показать список доступных команд\n"
    help_text += "/files - Показать все файлы, которые вы отправили\n"
    bot.send_message(message.chat.id, help_text)

def get_main_menu_keyboard() -> telebot.types.ReplyKeyboardMarkup:
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        telebot.types.KeyboardButton('/help'),
        telebot.types.KeyboardButton('/files')
    ]
    keyboard.add(*buttons)
    return keyboard

@bot.message_handler(commands=['start'])
def start_command(message: telebot.types.Message) -> NoReturn:
    # Create a personal folder for the user
    user_folder = f"files/{message.chat.username}"
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    keyboard = get_main_menu_keyboard()
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите команду из меню:", reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def show_commands(message: telebot.types.Message) -> NoReturn:
    show_help(message)

@bot.message_handler(commands=['files'])
def show_user_files(message: telebot.types.Message) -> NoReturn:
    files = get_user_files(message.chat.id)
    if not files:
        bot.send_message(message.chat.id, "Вы еще не отправляли файлы.")
    else:
        response = "Ваши файлы:\n\n"
        for file_type, file_id, timestamp in files:
            response += f"Тип: {file_type}\nID: {file_id}\nВремя: {timestamp}\n\n"
        bot.send_message(message.chat.id, response)

@bot.message_handler(content_types=['document', 'photo', 'audio', 'video'])
def handle_files(message: telebot.types.Message) -> NoReturn:
    file_type = message.content_type
    if file_type == 'document':
        file_id = message.document.file_id
    elif file_type == 'photo':
        file_id = message.photo[-1].file_id
    elif file_type == 'audio':
        file_id = message.audio.file_id
    elif file_type == 'video':
        file_id = message.video.file_id
    else:
        return

    save_file_info(message.chat.id, message.chat.username, file_type, file_id)
    bot.send_message(message.chat.id, "Это файл")

def save_file_info(user_id: int, username: str, file_type: str, file_id: str) -> None:
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path

    downloaded_file = bot.download_file(file_path)

    file_extension = os.path.splitext(file_path)[1]
    file_name = f"{file_id}{file_extension}"
    file_save_path = f"files/{username}/{file_name}"

    with open(file_save_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    save_file_info_to_database(user_id, file_type, file_name)

def save_file_info_to_database(user_id: int, file_type: str, file_name: str) -> None:
    pass

@bot.message_handler(commands=['files'])
def show_user_files(message: telebot.types.Message) -> NoReturn:
    user_folder = f"files/{message.chat.username}"
    if not os.path.exists(user_folder):
        bot.send_message(message.chat.id, "Вы еще не отправляли файлы.")
        return

    files = os.listdir(user_folder)
    if not files:
        bot.send_message(message.chat.id, "Вы еще не отправляли файлы.")
    else:
        for file_name in files:
            file_path = os.path.join(user_folder, file_name)
            with open(file_path, 'rb') as file:
                if file_name.endswith('.doc') or file_name.endswith('.docx'):
                    bot.send_document(message.chat.id, file)
                elif file_name.endswith('.jpg') or file_name.endswith('.png'):
                    bot.send_photo(message.chat.id, file)
                elif file_name.endswith('.mp3') or file_name.endswith('.wav'):
                    bot.send_audio(message.chat.id, file)
                elif file_name.endswith('.mp4') or file_name.endswith('.avi'):
                    bot.send_video(message.chat.id, file)
                else:
                    bot.send_document(message.chat.id, file)






if __name__ == '__main__':
    bot.infinity_polling()
