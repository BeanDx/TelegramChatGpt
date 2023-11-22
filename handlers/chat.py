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

LINK_CHAT = 'https://t.me/ReadyHubChat' # ссылка на чат
START_COMMAND = """<b>Привет!, я могу сгенерировать текст, картинку, а также отправить скриншот сайта по ссылке.\n\nЯ работаю только в этом чате: @ReadyHubChat\nСоздатель: @BeanD_TM\nКанал: @ReadyHub</b>""" # текст по команде /start
NON_ARG_TEXT = """<b>Вы не ввели текст запроса!\n\nПопробуйте:</b>\n<code>/chat Привет!</code>\n<code>/img стул</code>\n<code>/site google.com</code>"""
CHAT_ID = -1001790665314 # your chat id [from https://t.me/myidbot]
ADMIN_ID = 2074068795 # your id [from https://t.me/myidbot]
DELAY = 10 # Задержка после запросов (.5 = 0.50)
BOT_TOKEN = '' # from BotFather
OPENAI_TOKEN = '' # token openAI

SECOND_GROUP = -1001775763708
TEST_GROUP = -1001883705590

CHAT_IDS = [CHAT_ID,
           SECOND_GROUP,
          TEST_GROUP] # for spam

BOT_TOKEN = '6128642151:AAFVq9VFnuQk5m7qaJawR7uVPeSjomllpDo'


# Инициализация телеграмм-бота
bot = Bot(token=BOT_TOKEN) 
dp = Dispatcher(bot)

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
