import Telegram
import asyncio
import logging


async def echo(bot: Telegram.Telegram, update: Telegram.DataTypes.Update):
    await bot.sendMessage(update.message.chat, update.message.text)

async def kek(bot: Telegram.Telegram, update: Telegram.DataTypes.Update):
    await bot.sendMessage(update.message.chat, 'лол')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    loop = asyncio.get_event_loop()
    bot = Telegram.Telegram('6029827241:AAHH3CtJ9WypzEBYn2-u73J096KEuyZ8SZU')
    echoHandler = Telegram.Handler('', echo)
    kekHandler = Telegram.Handler('кек', kek)
    bot.addHandler(kekHandler)
    bot.addHandler(echoHandler)
    loop.create_task(bot.run())
    loop.run_forever()