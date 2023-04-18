import aiohttp
from . import DataTypes
import config
from .Handler import Handler, CommandHandler
import json
from typing import List
import logging
import asyncio
import UserManager


class Telegram:
    def __init__(self, token: str, url: str = '', cert: str = ''):
        self.apiEndpoint = f'https://api.telegram.org/bot{token}/'
        self.offset = 0
        self.updates = []
        self.handlers = []
        self.cert = cert
        self.url = url
        self.UserManager = UserManager.UserManager()
        logging.info('bot init success')

    async def setMyCommands(self) -> bool:
        a = [json.loads(str(DataTypes.BotCommand(i.command, i.description)).replace('\'', '\"')) for i in self.handlers
             if isinstance(i, CommandHandler)]
        async with self.session.get(self.apiEndpoint + 'setMyCommands',
                                    params={'commands': str(a).replace('\'', '\"')}) as response:
            if json.loads(await response.text()):
                logging.info(f'commands setted {a}')
                return True
            else:
                return False

    async def getWebhookInfo(self):
        async with self.session.get(self.apiEndpoint + 'getWebhookInfo') as response:
            logging.info(json.loads(await response.text()))
            if json.loads(await response.text())['ok'] and (not json.loads(await response.text())['result']['url'] or
                                                            json.loads(await response.text())['result'][
                                                                'url'] != self.url):
                return True
            else:
                return False

    async def setWebhook(self):
        data = {
            'url': self.url,
            'certificate': open(self.cert, 'rb')
        }
        async with self.session.post(self.apiEndpoint + 'setWebhook', data=data) as response:
            logging.info(json.loads(await response.text()))
            if json.loads(await response.text())['ok']:
                logging.info(f'Webhook setted on {self.url}')
                return True
            else:
                return False

    async def getMe(self) -> DataTypes.User:
        async with self.session.get(self.apiEndpoint + 'getMe') as response:
            if json.loads(await response.text())['ok']:
                return DataTypes.User(json.loads(await response.text())['result'])

    def addHandler(self, handler: Handler):
        self.handlers.append(handler)
        logging.info(f'handler {handler} added')

    async def getUpdates(self) -> List[DataTypes.Update]:
        async with self.session.get(self.apiEndpoint + 'getUpdates',
                                    params={'timeout': 10, 'offset': self.offset}) as response:
            response = json.loads(await response.text())
            if response['ok'] and response['result']:
                self.offset = response['result'][-1]['update_id'] + 1
                result = [DataTypes.Update(i) for i in response['result']]
                logging.info(f'updates getted {result}')
                return result
            else:
                return []

    async def sendMessage(self, chat: DataTypes.Chat, text: str) -> DataTypes.Message:
        async with self.session.post(self.apiEndpoint + 'sendMessage',
                                     params={'chat_id': chat.id, 'text': text}) as response:
            response = json.loads(await response.text())
            if response['ok'] and response['result']:
                return DataTypes.Message(response['result'])

    async def editMessageText(self, chat: DataTypes.Chat, message: DataTypes.Message, text: str) -> DataTypes.Message:
        async with self.session.post(self.apiEndpoint + 'editMessageText',
                                     params={'chat_id': chat.id, 'message_id': message.message_id,
                                             'text': text}) as response:
            response = json.loads(await response.text())
            if response['ok'] and response['result']:
                logging.info(f'message edited {message.message_id}')
                return DataTypes.Message(response['result'])

    async def sendChatAction(self, chat: DataTypes.Chat, action: str) -> bool:
        async with self.session.post(self.apiEndpoint + 'sendChatAction',
                                     params={'chat_id': chat.id, 'action': action}) as response:
            response = json.loads(await response.text())
        if response:
            logging.info(f'Action sended {action}, {chat.id}')
            return True
        else:
            return False

    async def solveUpdates(self):
        for i in self.updates:
            logging.info(i)
            for j in self.handlers:
                if await j.check(self, i):
                    break
            self.updates.remove(i)

    async def run(self, webhook=False):
        if not webhook:
            asyncio.create_task(self.UserManager.saveAll())
            self.session = aiohttp.ClientSession()
            await self.setMyCommands()
            logging.info(await self.getMe())
            while True:
                self.updates = await self.getUpdates()
                for i in self.updates:
                    for j in self.handlers:
                        if await j.check(self, i):
                            break
                    self.updates.remove(i)
        else:
            asyncio.create_task(self.UserManager.clearCache())
            self.session = aiohttp.ClientSession()
            await self.setWebhook()
            if await self.getWebhookInfo():
                await self.setWebhook()
            await self.setMyCommands()
