import Telegram
import asyncio


async def main():
    bot = Telegram.Telegram('6029827241:AAHH3CtJ9WypzEBYn2-u73J096KEuyZ8SZU')
    for i in range(3):
        print((await bot.getUpdates()))

if __name__ == '__main__':
    print('start')
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
