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
    '''
    The bot main class

    Args:
        token (str): Telegram bot token
        url (str): url for telegram webhook (optional)
        cert (str): path to self-signed certificate for webhook (optional)
    Attributes:
        self.apiEndpoint (str): string to Telegram api endpoint
        self.offset (int): offset for retrieving updates via long pooling
        self.updates (list[Telegram.DataTypes.Update]): list of Updates
        self.cert (str): path to self-signed certificate
        self.url (str): url to Telegram webhook
        self.UserManager (UserManager.UserManager): UserManager object
    '''
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
        '''
        setting commands to bot from self.handlers

        Returns:
            bool: True on success
        '''
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
        '''
        get webhook info

        Returns:
            bool: true on success
        '''
        async with self.session.get(self.apiEndpoint + 'getWebhookInfo') as response:
            logging.info(json.loads(await response.text()))
            if json.loads(await response.text())['ok'] and (not json.loads(await response.text())['result']['url'] or
                                                            json.loads(await response.text())['result'][
                                                                'url'] != self.url):
                return True
            else:
                return False

    async def setWebhook(self):
        '''
        set webhook

        Returns:
            bool: true on success
        '''
        data = {
            'url': self.url,
            'certificate': open(self.cert, 'rb')
        }
        if not self.session:
            self.session = aiohttp.ClientSession()
        async with self.session.post(self.apiEndpoint + 'setWebhook', data=data) as response:
            logging.info(json.loads(await response.text()))
            if json.loads(await response.text())['ok']:
                logging.info(f'Webhook setted on {self.url}')
                return True
            else:
                return False

    async def getMe(self) -> DataTypes.User:
        '''
        getMe method

        Returns:
            DataTypes.User: return bot User object
        '''
        async with self.session.get(self.apiEndpoint + 'getMe') as response:
            if json.loads(await response.text())['ok']:
                return DataTypes.User(json.loads(await response.text())['result'])

    def addHandler(self, handler: Handler):
        '''
        addHandler add new handler to process

        Args:
            handler (Handler): handler to process
        '''
        self.handlers.append(handler)
        logging.info(f'handler {handler} added')

    async def getUpdates(self) -> List[DataTypes.Update]:
        '''
        getUpdate method to retrieve updates from Telegram

        Returns:
            List[DataTypes.Update]: on success
        '''
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
        '''
        sendMessage method

        Args:
            chat (DataTypes.Chat): to which chat message supposed to be send
            text (str): message
        Returns:
            DataTypes.Message: message object which was sent
        '''
        async with self.session.post(self.apiEndpoint + 'sendMessage',
                                     params={'chat_id': chat.id, 'text': text}) as response:
            response = json.loads(await response.text())
            if response['ok'] and response['result']:
                return DataTypes.Message(response['result'])

    async def editMessageText(self, chat: DataTypes.Chat, message: DataTypes.Message, text: str) -> DataTypes.Message:
        '''
        editMessageText edits a message which was sent by bot

        Args:
            chat (DataTypes.Chat): chat in which message needs to be edited
            message (DataTypes.Message): message which needs to be replaced
            text (str): text to replace
        Returns:
            DataTypes.Message: message object whicch was sent
        '''
        async with self.session.post(self.apiEndpoint + 'editMessageText',
                                     params={'chat_id': chat.id, 'message_id': message.message_id,
                                             'text': text}) as response:
            response = json.loads(await response.text())
            if response['ok'] and response['result']:
                logging.info(f'message edited {message.message_id}')
                return DataTypes.Message(response['result'])

    async def sendChatAction(self, chat: DataTypes.Chat, action: str) -> bool:
        '''
        sendChatAction send action to the chat

        Args:
            chat (DataTypes.Chat): to which chat action needs to be send
            action (str): action to send
        Returns:
            bool:
        '''
        async with self.session.post(self.apiEndpoint + 'sendChatAction',
                                     params={'chat_id': chat.id, 'action': action}) as response:
            response = json.loads(await response.text())
        if response:
            logging.info(f'Action sended {action}, {chat.id}')
            return True
        else:
            return False

    async def solveUpdates(self):
        '''
        solveUpdates method to run Updates with webhook
        '''
        for i in self.updates:
            logging.info(i)
            for j in self.handlers:
                if await j.check(self, i):
                    break
            self.updates.remove(i)

    async def run(self, webhook=False):
        '''
        run methods to run Telegram bot

        Args:
            webhook (bool): webhook enabled?
        '''
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
            asyncio.create_task(self.UserManager.saveAll())
            self.session = aiohttp.ClientSession()
            await self.setMyCommands()
            while True:
                await asyncio.sleep(10)
