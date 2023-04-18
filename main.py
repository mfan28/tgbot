import Telegram
import asyncio
import logging
import openai
import config
from UserManager import Exceptions
from flask import Flask, request
from time import time
import time as t
from threading import Thread


def web(bot: Telegram.Telegram):
    app = Flask(__name__)

    @app.route('/', methods=['POST', 'GET'])
    def index():
        return reqeust.args

    app.run(host=config.HOST, port=config.PORT, ssl_context=(config.CERT, config.KEY))

async def kek(bot: Telegram.Telegram, update: Telegram.DataTypes.Update):
    try:
        cachedUser = bot.UserManager[update.message.chat.id]
    except Exceptions.NotRegistered:
        await bot.sendMessage(update.message.chat, 'Вы не зарегистрированы')
        return
    cachedUser.cachedUser['context'].append({'role': 'user', 'content': update.message.text})
    cachedUser.cachedUser['messages'].append({'role': 'user', 'content': update.message.text, 'time': t.ctime()})
    message = await bot.sendMessage(update.message.chat, 'Бот обрабатывает ваш запрос...')
    comp = await openai.ChatCompletion.acreate(
        model='gpt-3.5-turbo-0301',
        messages=cachedUser.cachedUser['context'],
        stream=True
    )
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


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    openai.api_key = config.OPENAI_API_KEY
    bot = Telegram.Telegram(config.TELEGRAM_API_KEY, url='https://45.146.167.48:80', cert=config.CERT)
    bot.addHandler(Telegram.Handler.CommandHandler('start', start, "start"))
    bot.addHandler(Telegram.Handler.CommandHandler('clearcontext', clear_context, "clear context"))
    bot.addHandler(Telegram.Handler.Handler('', kek))
    loop.create_task(bot.run(webhook=True))
    Thread(target=web, args=(bot,)).start()
    loop.run_forever()
