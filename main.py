import Telegram
import asyncio


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    Telegram
    bot = Telegram.Telegram('token')
    a = loop.create_task(bot.getMe())
    print(a
          )

