import openai
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command, CommandStart # for filter command ban
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command
from aiogram.types import ChatType # for spam
import requests # for img command
from io import BytesIO
import asyncio # for sleep 
import time # for ping command

import shelve # database

from config.config import * # configuration

# handlers
#from handlers.start import start_command
#from handlers.chat import cmd_chat

# Инициализация OpenAI API
openai.api_key = OPENAI_TOKEN  

# Инициализация телеграмм-бота
bot = Bot(token=BOT_TOKEN) 
dp = Dispatcher(bot)

# Инициализация логгера
logging.basicConfig(level=logging.INFO)

# Инициализация хранилища
db = shelve.open('./db/users.db') # name of database

@dp.message_handler(Command('start'))
async def start_command(message: types.Message):
    await message.answer(START_COMMAND, parse_mode='HTML')


# Обработчик команды /chat
@dp.message_handler(Command('chat'))
async def cmd_chat(message: types.Message):
    if message.chat.id == CHAT_ID or message.chat.id == SECOND_GROUP or message.chat.id == TEST_GROUP:  # Проверяем, что запрос был отправлен в определенной группе
        user_id = message.from_user.id # Получаем ID пользователя, который отправил запрос
        # Получаем список забаненных пользователей из хранилища
        with shelve.open('ban_list') as db:
            banned_users = list(db.keys())
        if str(user_id) in banned_users: # Проверяем, находится ли ID пользователя в списке забаненных пользователей
            await message.reply('Вы забанены и не можете использовать эту команду.')
        else:
            query = message.text.lstrip('/chat').strip() # Получаем текст запроса пользователя
            if not query:  # Проверяем, что аргументы команды не пустые
                await message.reply(NON_ARG_TEXT, parse_mode='HTML')
            elif len(query) > 300:  # Проверяем длину запроса пользователя
                await message.reply("Слишком длинный запрос. Максимальная длина запроса - 300 символов.")
            else:
                # Запрашиваем ответ от OpenAI
                response = openai.Completion.create(
                    model='text-davinci-003',
                    prompt=message.text[:2042],
                    temperature=0.9,
                    max_tokens=2000,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.6,
                    stop=["You:"])
                await message.reply(response.choices[0].text) # Отправляем ответ пользователю
                await asyncio.sleep(DELAY) # делаем задержку в 10 секунд


# Обработчик команды /img
@dp.message_handler(Command('img'))
async def cmd_img(message: types.Message):
    if message.chat.id not in [CHAT_ID, SECOND_GROUP]:
        await message.reply(START_COMMAND, parse_mode='HTML')
        return
    
    user_id = message.from_user.id # Получаем ID пользователя, который отправил запрос
    with shelve.open('ban_list') as db:
        banned_users = list(db.keys())
    if str(user_id) in banned_users:
        await message.reply('Вы забанены и не можете использовать эту команду.')
        return

    query = message.text.lstrip('/img').strip() # Получаем текст запроса пользователя
    if not query:
        await message.reply(NON_ARG_TEXT, parse_mode='HTML')
        return
    elif len(query) > 50:
        await message.reply("Слишком длинный запрос. Максимальная длина запроса - 50 символов.")
        return

    response = openai.Image.create(
        prompt=f"Generate image of {query}",
        n=1,
        size="1024x1024",
        response_format="url"
    )
    image_url = response['data'][0]['url'] # Получаем URL изображения
    image_content = requests.get(image_url).content 
    image_file = BytesIO(image_content)
    await bot.send_photo(chat_id=message.chat.id, photo=image_file, caption=f'Картинка по запросу: {query}')
    await asyncio.sleep(DELAY)


# Обработчик команды /site
@dp.message_handler(Command('site'))
async def screen_site(message: types.Message):
    if message.chat.id == CHAT_ID or message.chat.id == SECOND_GROUP: # Проверяем, что запрос был отправлен в определенной группе
        user_id = message.from_user.id # Получаем ID пользователя, который отправил запрос
    # Получаем список забаненных пользователей из хранилища
    with shelve.open('ban_list') as db:
        banned_users = list(db.keys())
    if str(user_id) in banned_users: # Проверяем, находится ли ID пользователя в списке забаненных пользователей
        await message.reply('Вы забанены и не можете использовать эту команду.')
    else:
        if message.chat.id == CHAT_ID:
            query = message.text.replace('/site ', '') # Получаем текст запроса пользователя
            photo_url = f"https://mini.s-shot.ru/1366x768/JPEG/1366/Z100/?{query}"
            photo = types.InputFile.from_url(photo_url)
            await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=f'Сайт [{query}]')

# Обработчик команды /gpt_ban
@dp.message_handler(lambda message: message.reply_to_message, commands=['gpt_ban'])
async def chat_ban_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID: # Проверяем, что команду отправил именно тот пользователь, которому это разрешено
        await message.reply('Вы не можете использовать эту команду.')
    else:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            with shelve.open('ban_list') as db:
                db[str(user_id)] = True
            await message.answer(f'Пользователь {user_id} заблокирован.')
        else:
            await message.answer('Необходимо ответить на сообщение пользователя для блокировки.')

# Обработчик команды /gpt_unban
@dp.message_handler(lambda message: message.reply_to_message, commands=['gpt_unban'])
async def chat_unban_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID: # Проверяем, что команду отправил именно тот пользователь, которому это разрешено
        await message.reply('Вы не можете использовать эту команду.')
    else:
        if message.chat.id == CHAT_ID:
            user_id = message.reply_to_message.from_user.id
            with shelve.open('ban_list') as db:
                if str(user_id) in db:
                    del db[str(user_id)]
                await message.reply(f'Пользователь {user_id} разбанен.')


# Обработчик команды /spam
@dp.message_handler(Command('spam'))
async def on_spam_command(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Эта команда доступна только администраторам бота.")
        return
    text = message.get_args()
    if text == '':
        await message.reply('<b>Ты ввел без аргументов!</b>', parse_mode='HTML')
    else:
        # Отправляем сообщение во все чаты, где есть бот
        for chat_id in CHAT_IDS:
            chat = await message.bot.get_chat(chat_id)
            if chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
                await message.bot.send_message(chat_id, text)

# Обработчик команды /ping
@dp.message_handler(Command('ping'))
async def ping_command(message: types.Message):
    # Отправляем сообщение "ping" и замеряем время отправки
    start = time.monotonic()
    
    # Замеряем время получения ответа и вычисляем разницу
    end = time.monotonic()
    delta_ms = round((end - start) * 1000, 2)
    
    # Отправляем сообщение с задержкой (ping) в миллисекундах
    await message.answer(f"Задержка: {delta_ms} мс")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
