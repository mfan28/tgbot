import Telegram
import asyncio
import logging
import openai
import config
import UserManager
from UserManager import Exceptions
from time import time


async def kek(bot: Telegram.Telegram, update: Telegram.DataTypes.Update):
    try:
        cachedUser = UserManager[update.message.chat.id]
    except Exceptions.NotRegistered:
        await bot.sendMessage(update.message.chat, 'Вы не зарегистрированы')
        return
    cachedUser.cachedUser['context'].append({'role': 'user', 'content': update.message.text})
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
    cachedUser.save()


async def start(bot: Telegram.Telegram, update: Telegram.DataTypes.Update):
    if update.message.chat not in UserManager.users():
        UserManager.createUser(update.message.chat)
        await bot.sendMessage(update.message.chat, f'{update.message.chat.username}, вы зарегистрированы')
    else:
        await bot.sendMessage(update.message.chat, f'{update.message.chat.username}, вы не нуждаетесь в регистрации')


async def clear_context(bot: Telegram.Telegram, update: Telegram.DataTypes.Update):
    try:
        cachedUser = UserManager[update.message.chat.id]
    except Exceptions.NotRegistered:
        await bot.sendMessage(update.message.chat, 'Вы не зарегистрированы')
        return
    cachedUser.cachedUser['context'] = []
    cachedUser.save()
    await bot.sendMessage(update.message.chat, 'Контекст очищен')


if __name__ == '__main__':
    UserManager = UserManager.UserManager()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    openai.api_key = config.OPENAI_API_KEY
    loop = asyncio.get_event_loop()
    bot = Telegram.Telegram(config.TELEGRAM_API_KEY)
    bot.addHandler(Telegram.Handler.CommandHandler('start', start))
    bot.addHandler(Telegram.Handler.CommandHandler('clearcontext', clear_context))
    bot.addHandler(Telegram.Handler.Handler('', kek))
    loop.create_task(bot.run())
    loop.run_forever()
