import Telegram
import asyncio
import logging
import openai
import config
from UserManager import Exceptions
from flask import Flask
from time import time
import time as t
from threading import Thread


def web(bot: Telegram.Telegram, loop):
    app = Flask(__name__)
    from flask import request
    @app.route('/', methods=['POST'])
    def index():
        bot.updates.append(Telegram.DataTypes.Update(request.json))
        asyncio.run_coroutine_threadsafe(bot.solveUpdates(), loop)
        return ''

    app.run()


async def kek(bot: Telegram.Telegram, update: Telegram.DataTypes.Update):
    try:
        cachedUser = bot.UserManager[update.message.chat.id]
    except Exceptions.NotRegistered:
        await bot.sendMessage(update.message.chat, 'Вы не зарегистрированы')
        return
    cachedUser.cachedUser['context'].append({'role': 'user', 'content': update.message.text})
    cachedUser.cachedUser['messages'].append({'role': 'user', 'content': update.message.text, 'time': t.ctime()})
    message = await bot.sendMessage(update.message.chat, 'Бот обрабатывает ваш запрос...')
    while True:
        try:
            comp = await openai.ChatCompletion.acreate(
                model='gpt-3.5-turbo-0301',
                messages=cachedUser.cachedUser['context'],
                stream=True
                )
            break
        except openai.error.RateLimitError as ratelimit:
            logging.info(update, ratelimit.error)
    j = ''
    t1, t2 = time(), time()
    async for i in comp:
        j += i['choices'][0]['delta'].get('content', '')
        t1 = time()
        if t1 - t2 > 3 and j != message.text and j:
            t1, t2 = time(), t1
            await bot.sendChatAction(message.chat, Telegram.Actions.TYPING)
            message = await bot.editMessageText(message.chat, message, j)
    await bot.editMessageText(message.chat, message, j)
    cachedUser.cachedUser['context'].append({'role': 'assistant', 'content': j})
    cachedUser.cachedUser['messages'].append({'role': 'assistant', 'content': j, 'time': t.ctime()})
    cachedUser.save()


async def start(bot: Telegram.Telegram, update: Telegram.DataTypes.Update):
    if update.message.chat.id not in bot.UserManager.users():
        bot.UserManager.createUser(update.message.chat)
        await bot.sendMessage(update.message.chat, f'{update.message.chat.first_name}, вы зарегистрированы')
    else:
        await bot.sendMessage(update.message.chat, f'{update.message.chat.first_name}, вы не нуждаетесь в регистрации')


async def clear_context(bot: Telegram.Telegram, update: Telegram.DataTypes.Update):
    try:
        cachedUser = bot.UserManager[update.message.chat.id]
    except Exceptions.NotRegistered:
        await bot.sendMessage(update.message.chat, 'Вы не зарегистрированы')
        return
    cachedUser.cachedUser['context'] = []
    cachedUser.save()
    await bot.sendMessage(update.message.chat, 'Контекст очищен')


def start():
    loop = asyncio.get_event_loop()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    openai.api_key = config.OPENAI_API_KEY
    bot = Telegram.Telegram(config.TELEGRAM_API_KEY, url=f'https://{config.HOST}:{config.PORT}', cert=config.CERT)
    bot.addHandler(Telegram.Handler.CommandHandler('start', start, "start"))
    bot.addHandler(Telegram.Handler.CommandHandler('clearcontext', clear_context, "clear context"))
    bot.addHandler(Telegram.Handler.Handler('', kek))
    loop.create_task(bot.run(webhook=True))
    Thread(target=web, args=(bot, loop)).start()
    loop.run_forever()
