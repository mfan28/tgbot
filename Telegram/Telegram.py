import aiohttp
from . import DataTypes
from .Handler import Handler, CommandHandler
import json
from typing import List
import logging


class Telegram:
    def __init__(self, token: str):
        self.apiEndpoint = f'https://api.telegram.org/bot{token}/'
        self.offset = 0
        self.updates = []
        self.handlers = []
        logging.info('bot init success')

    async def setMyCommands(self) -> bool:
        a = [json.loads(str(DataTypes.BotCommand(i.command, i.description)).replace('\'', '\"')) for i in self.handlers if isinstance(i, CommandHandler)]
        async with self.session.get(self.apiEndpoint + 'setMyCommands', params={'commands': str(a).replace('\'', '\"')}) as response:
            if json.loads(await response.text()):
                return True
            else:
                return False

    async def getMe(self) -> DataTypes.User:
        async with self.session.get(self.apiEndpoint + 'getMe') as response:
            if await json.loads(response.text())['ok']:
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
                return [DataTypes.Update(i) for i in response['result']]
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
                return DataTypes.Message(response['result'])

    async def sendChatAction(self, chat: DataTypes.Chat, action: str) -> bool:
        async with self.session.post(self.apiEndpoint + 'sendChatAction',
                                     params={'chat_id': chat.id, 'action': action}) as response:
            response = json.loads(await response.text())
        if response:
            return True
        else:
            return False

    async def run(self):
        self.session = aiohttp.ClientSession()
        await self.setMyCommands()
        while True:
            self.updates = await self.getUpdates()
            for i in self.updates:
                for j in self.handlers:
                    if await j.check(self, i):
                        break
                self.updates.remove(i)
