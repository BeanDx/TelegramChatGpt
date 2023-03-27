import openai
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command, CommandStart # for filter command ban
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command
import requests # for img command
from io import BytesIO
import asyncio # for sleep 

import shelve # database

LINK_CHAT = 'https://t.me/ReadyHubChat' # ссылка на чат
START_COMMAND = """<b>Привет!, я могу сгенерировать текст, картинку, а также отправить скриншот сайта по ссылке.\n\nЯ работаю только в этом чате: @ReadyHubChat\nСоздатель: @BeanD_TM\nКанал: @ReadyHub</b>""" # текст по команде /start
CHAT_ID = -12345 # your chat id [from https://t.me/myidbot]
ADMIN_ID = 12345 # your id [from https://t.me/myidbot]
DELAY = 10 # Задержка после запросов (.5 = 0.50s)
BOT_TOKEN = '' # from BotFather
OPENAI_TOKEN = '' # token openAI

# Инициализация OpenAI API
openai.api_key = OPENAI_TOKEN  

# Инициализация телеграмм-бота
bot = Bot(token=BOT_TOKEN) 
dp = Dispatcher(bot)

# Инициализация логгера
logging.basicConfig(level=logging.INFO)

# Инициализация хранилища
db = shelve.open('users.db') # name of database

@dp.message_handler(Command('start'))
async def start_command(message: types.Message):
    await message.answer(START_COMMAND, parse_mode='HTML')


# Обработчик команды /chat
@dp.message_handler(Command('chat'))
async def cmd_chat(message: types.Message):
    if message.chat.id == CHAT_ID: # Проверяем, что запрос был отправлен в определенной группе
        user_id = message.from_user.id # Получаем ID пользователя, который отправил запрос
        # Получаем список забаненных пользователей из хранилища
        with shelve.open('ban_list') as db:
            banned_users = list(db.keys())
        if str(user_id) in banned_users: # Проверяем, находится ли ID пользователя в списке забаненных пользователей
            await message.reply('Вы забанены и не можете использовать эту команду.')
        else:
            query = message.text.replace('/chat ', '') # Получаем текст запроса пользователя
            if len(query) > 300:  # Проверяем длину запроса пользователя
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
        if message.chat.id == CHAT_ID: # Проверяем, что запрос был отправлен в определенной группе
            user_id = message.from_user.id # Получаем ID пользователя, который отправил запрос
        # Получаем список забаненных пользователей из хранилища
        with shelve.open('ban_list') as db:
            banned_users = list(db.keys())
        if str(user_id) in banned_users: # Проверяем, находится ли ID пользователя в списке забаненных пользователей
            await message.reply('Вы забанены и не можете использовать эту команду.')
        else:
            if message.chat.id == CHAT_ID:
                query = message.text.replace('/img ', '') # Получаем текст запроса пользователя
                
                if len(query) > 50: # Проверяем длину запроса пользователя
                    await message.reply("Слишком длинный запрос. Максимальная длина запроса - 50 символов.")
                else:
                    response = openai.Image.create(
                        prompt=f"Generate image of {query}",
                        n=1,
                        size="1024x1024",
                        response_format="url")
                image_url = response['data'][0]['url'] # Получаем URL изображения
                # Загружаем изображение из URL
                image_content = requests.get(image_url).content 
                image_file = BytesIO(image_content)
                await bot.send_photo(chat_id=message.chat.id, photo=image_file, caption=f'Картинка по запросу: {query}') # Отправляем изображение пользователю
                await asyncio.sleep(DELAY) # делаем задержку в 10 секунд
            else:
                await message.reply(START_COMMAND, parse_mode='HTML')

# Обработчик команды /site
@dp.message_handler(Command('site'))
async def screen_site(message: types.Message):
    if message.chat.id == CHAT_ID: # Проверяем, что запрос был отправлен в определенной группе
        user_id = message.from_user.id # Получаем ID пользователя, который отправил запрос
    # Получаем список забаненных пользователей из хранилища
    with shelve.open('ban_list') as db:
        banned_users = list(db.keys())
    if str(user_id) in banned_users: # Проверяем, находится ли ID пользователя в списке забаненных пользователей
        await message.reply('Вы забанены и не можете использовать эту команду.')
    else:
        if message.chat.id == CHAT_ID:
            query = message.text.replace('/site ', '') # Получаем текст запроса пользователя
            await bot.send_photo(chat_id=message.chat.id, photo=f"https://mini.s-shot.ru/1366x768/JPEG/1366/Z100/?{query}", caption=f'Сайт [{query}]') # Отправляем изображение пользователю


# Обработчик команды /gpt_ban
@dp.message_handler(lambda message: message.reply_to_message, commands=['gpt_ban'])
async def chat_ban_handler(message: types.Message):
    if message.from_user.id != 2074068795: # Проверяем, что команду отправил именно тот пользователь, которому это разрешено
        await message.reply('Вы не можете использовать эту команду.')
    else:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            with shelve.open('ban_list') as db:
                db[str(user_id)] = True
            await message.answer(f'Пользователь {user_id} заблокирован.')
        else:
            await message.answer('Необходимо ответить на сообщение пользователя для блокировки.')

# Обработчик команды /chat_unban
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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
