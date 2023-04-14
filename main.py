import Telegram
import asyncio
import logging
import openai
import config
from time import time


async def echo(bot: Telegram.Telegram, update: Telegram.DataTypes.Update):
    await bot.sendMessage(update.message.chat, update.message.text)


async def kek(bot: Telegram.Telegram, update: Telegram.DataTypes.Update):
    message = await bot.sendMessage(update.message.chat, 'Бот обрабатывает ваш запрос...')
    comp = await openai.ChatCompletion.acreate(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': 'расскажи максимально подробно про интегралы с примерами'}
        ],
        stream=True
    )
    j = ''
    t1, t2 = time(), time()
    async for i in comp:
        await bot.sendChatAction(message.chat, Telegram.Actions.TYPING)
        j += i['choices'][0]['delta'].get('content', '')
        t1 = time()
        if t1 - t2 > 3 and j != message.text and j:
            t1, t2 = time(), t1
            message = await bot.editMessageText(message.chat, message, j)
    await bot.editMessageText(message.chat, message, j)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    openai.api_key = config.OPENAI_API_KEY
    loop = asyncio.get_event_loop()
    bot = Telegram.Telegram(config.TELEGRAM_API_KEY)
    echoHandler = Telegram.Handler('', echo)
    kekHandler = Telegram.Handler('кек', kek)
    bot.addHandler(kekHandler)
    bot.addHandler(echoHandler)
    loop.create_task(bot.run())
    loop.run_forever()