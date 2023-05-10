LINK_CHAT = 'https://t.me/ReadyHubChat' # ссылка на чат
START_COMMAND = """<b>Привет!, я могу сгенерировать текст, картинку, а также отправить скриншот сайта по ссылке.\n\nЯ работаю только в этом чате: @ReadyHubChat\nСоздатель: @BeanD_TM\nКанал: @ReadyHub</b>""" # текст по команде /start
NON_ARG_TEXT = """<b>Вы не ввели текст запроса!\n\nПопробуйте:</b>\n<code>/chat Привет!</code>\n<code>/img стул</code>\n<code>/site google.com</code>"""
CHAT_ID = -121212 # your chat id [from https://t.me/myidbot]
ADMIN_ID = 121212 # your id [from https://t.me/myidbot]
DELAY = 10 # Задержка после запросов (.5 = 0.50)
BOT_TOKEN = '' # from BotFather
OPENAI_TOKEN = 'sk-121212' # token openAI

# Если не будете использовать доп. группы, все равно не меняйте эти значения:
SECOND_GROUP = -1231231231
TEST_GROUP = -323232323232

CHAT_IDS = [CHAT_ID,
           SECOND_GROUP,
          TEST_GROUP] # for spam
