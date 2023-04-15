import Telegram
import asyncio
import logging
import openai
import config
import UserManager
from time import time


async def kek(bot: Telegram.Telegram, update: Telegram.DataTypes.Update):
    message = await bot.sendMessage(update.message.chat, 'Бот обрабатывает ваш запрос...')
    comp = await openai.ChatCompletion.acreate(
        model='gpt-3.5-turbo-0301',
        messages=[
            {'role': 'user', 'content': f'{update.message.text}'}
        ],
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


if __name__ == '__main__':
    UserManager = UserManager.UserManager()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    openai.api_key = config.OPENAI_API_KEY
    loop = asyncio.get_event_loop()
    bot = Telegram.Telegram(config.TELEGRAM_API_KEY)
    kekHandler = Telegram.Handler('', kek)
    bot.addHandler(kekHandler)
    loop.create_task(bot.run())
    loop.run_forever()
