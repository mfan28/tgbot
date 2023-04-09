import Telegram
import asyncio


async def main():
    bot = Telegram.Telegram('6029827241:AAHH3CtJ9WypzEBYn2-u73J096KEuyZ8SZU')
    print(await bot.getUpdates())

if __name__ == '__main__':
    asyncio.run(main())
