import Telegram
import config
import asyncio
import threading
from UserManager import Exceptions
import openai
import logging
from time import time, ctime

class Bot(threading.Thread):

    async def kek(bot: Telegram.Telegram, update: Telegram.DataTypes.Update):
        try:
            cachedUser = bot.UserManager[update.message.chat.id]
        except Exceptions.NotRegistered:
            await bot.sendMessage(update.message.chat, 'Вы не зарегистрированы')
            return
        cachedUser.cachedUser['context'].append({'role': 'user', 'content': update.message.text})
        cachedUser.cachedUser['messages'].append({'role': 'user', 'content': update.message.text, 'time': ctime()})
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
                await bot.editMessageText(message.chat, message, 'Высокая нагрузка, ждем 20 секунд...')
                await asyncio.sleep(20)
            except openai.InvalidRequestError as tk:
                logging.info(tk.error)
                del cachedUser.cachedUser['context'][1:len(cachedUser.cachedUser['context']) // 2]
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
        cachedUser.cachedUser['messages'].append({'role': 'assistant', 'content': j, 'time': ctime()})
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
    

    def __init__(self):
        super().__init__()
        self.tasks = []
        self.bot = Telegram.Telegram(config.TELEGRAM_API_KEY)
        openai.api_key = config.OPENAI_API_KEY
        self.bot.addHandler(Telegram.Handler.CommandHandler('start', self.start, "start"))
        self.bot.addHandler(Telegram.Handler.CommandHandler('clearcontext', self.clear_context, "clear context"))
        self.bot.addHandler(Telegram.Handler.Handler('', self.kek))
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        threading.Thread(target=self.loop.run_forever, daemon=True).start()
        super().start()
    
    def getLoad(self):
        return len(self.tasks)

    def run(self):
        threading.Thread(target=asyncio.run, args=(self.bot.run(webhook=True),)).start()
        while True:
            if self.tasks:
                while self.tasks:
                    self.bot.updates.append(self.tasks.pop())
                asyncio.run_coroutine_threadsafe(self.bot.solveUpdates(), self.loop)
                