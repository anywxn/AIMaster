import os
import telebot
import generator_llama_cpp as cpp
import speech_recognition as sr
from deep_translator import GoogleTranslator
import traceback
import librosa
import soundfile as sf
import time

# Создаем экземпляр бота
bot = telebot.TeleBot('ТОКЕН БОТА СЮДА', parse_mode='HTML')

print("Загрузка модели...")
print("Модель загружена!")


def recognize_speech(phrase_wav_path):
    r = sr.Recognizer()
    hellow = sr.AudioFile(phrase_wav_path)
    with hellow as source:
        audio = r.record(source)
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
    try:
        s = r.recognize_google(audio, language="ru-RU").lower()
        print("Text: " + s)
        result = s
    except Exception as e:
        print("Exception: " + str(e))
        result = None
    return result


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "Привет меня зовут AI-Master!\n"
                 "Я могу распознавать речь в голосовых сообщениях и отвечать на вопросы.\n"
                 "<i>Пришли мне голосовое <b>или</b> текстовое сообщение</i>, \n"
                 "<b>но перед этим посмотри дополнительную информацию по команде /info или по кнопке в меню</b>",
                 parse_mode='HTML')


@bot.message_handler(commands=['info'])
def send_welcome(message):
    bot.reply_to(message, "Привет, я чат-бот <b><i> со всроенной нейросетью модель, отвечу на ваши вопросы.</i></b>"
                          "Чтобы я хорошо распознал голосовое сообщение с вашим вопросом,"
                          "<b><i>запиши голосовое сообщение четко и желательно без лишнего шума</i></b>"
                          "\n<i>Так-же я могу отвечать на ваши текстовые вопросы,</i>"
                          "<i>не забывайте про пунктуацию для лучшего результата.</i>"
                          "\nCтарайтесь подробно описать все в одном вопросе,\n"
                          "<b>Следуйте инструкциям для максимально эффективного результата</b>", parse_mode="html")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.send_message(message.chat.id, '<b><i>⏳ Подожди немного, я думаю...</i></b>', parse_mode="html")
    querus = message.text
    prompt = GoogleTranslator(source="russian", target="english").translate(querus)
    print('с переводом: ' + prompt)
    print('без перевода: ' + querus)

    # запуск модели
    print("запуск модели...")
    answer = cpp.get_answer(
        prompt=querus,
        eos_token=None,
        stopping_strings=None,
    )
    print('без перевода: ' +answer)
    ans = GoogleTranslator(source="english", target="russian").translate(answer)
    print('с переводом: ' +ans)
    if len(ans) > 4000:
        for x in range(0, len(ans), 4000):
            bot.send_message(message.chat.id, ans[x:x + 4000])
    else:
        bot.send_message(message.chat.id, ans)


@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    sent_message = bot.send_message(message.chat.id, "Ваше сообщение распознаётся...")
    bot.send_chat_action(message.chat.id, 'typing')

    # Получаем аудио-файл из сообщения
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Сохраняем файл на диск
    file_id = message.voice.file_id
    file_name = f'./audio/{file_id}.ogg'
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Конвертируем файл в формат WAV
    audio_path = f'./audio/{file_id}.ogg'
    y, sr = librosa.load(audio_path)
    out_path = f'./audio/{file_id}1.wav'
    sf.write(out_path, y, sr, format='wav')

    # Распознаем речь
    recognized_text = recognize_speech(out_path)



    print('voice: ' + recognized_text)
    if recognized_text != "":
        req = recognized_text
        bot.send_chat_action(message.chat.id, 'typing')
        edited_message_text = '<b><i>Ваш запрос: </i></b>' + recognized_text
        bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message.message_id, text=edited_message_text)
        if req != "":
            prompt = GoogleTranslator(source="russian", target="english").translate(recognized_text)
            print(recognized_text)
            # запуск модели
            print("запуск модели...")
            bot.send_chat_action(message.chat.id, 'typing', timeout=120)
            answer = cpp.get_answer(
                prompt=prompt,
                eos_token=None,
                stopping_strings=None,
            )
            print(answer)
            ans = GoogleTranslator(source="english", target="russian").translate(answer)
            if len(ans) > 4000:
                for x in range(0, len(ans), 4000):
                    bot.send_message(message.chat.id, ans[x:x + 4000])
            else:
                bot.send_message(message.chat.id, ans)
            print(ans)
    else:
        bot.send_message(message.chat.id, '<b><i>Ваш запрос не распознан </i></b>' + recognized_text, parse_mode="html")

    os.remove(f'./audio/{file_id}.ogg')
    os.remove(f'./audio/{file_id}1.wav')


def main():
    while True:
        try:
            bot.polling()
        except Exception as e:
            # Выводим сообщение об ошибке
            print(f"Произошла ошибка: {e}")
            traceback_details = traceback.format_exc()
            bot.send_message(633897678, f"Произошла ошибка в боте:\n\n{traceback_details}")
            # Ждем некоторое время перед повторным запуском
            time.sleep(5)


if __name__ == "__main__":
    main()
