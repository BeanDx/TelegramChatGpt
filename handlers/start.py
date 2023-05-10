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

START_COMMAND = """<b>Привет!, я могу сгенерировать текст, картинку, а также отправить скриншот сайта по ссылке.\n\nЯ работаю только в этом чате: @ReadyHubChat\nСоздатель: @BeanD_TM\nКанал: @ReadyHub</b>""" # текст по команде /start
BOT_TOKEN = '6128642151:AAFVq9VFnuQk5m7qaJawR7uVPeSjomllpDo'

# Инициализация телеграмм-бота
bot = Bot(token=BOT_TOKEN) 
dp = Dispatcher(bot)

