import os
import logging
import json
import asyncio
from Telegram.DataTypes import *
from Singleton import singleton
from . import Exceptions


@singleton
class UserManager:
    def __init__(self):
        self.UsersFolder = './UserManager/Users/'
        self.users = lambda *x: os.listdir(self.UsersFolder)
        self.cachedUsers = {}
        logging.info('UserManager initialized')

    def createUser(self, chat: Chat):
        if str(chat.id) not in self.users():
            with open(self.UsersFolder + str(chat.id), 'w') as f:
                json.dump({'id': chat.id, 'username': chat.first_name, 'context': [], 'messages': []}, f, indent='\t', ensure_ascii=False)
                logging.info(f'User {chat.id} created')

    def __getitem__(self, item):
        return CachedUser(item)

    async def clearCache(self):
        while True:
            await asyncio.sleep(300)
            for i, k in self.cachedUsers.items():
                with open(self.UsersFolder + str(i), 'w') as f:
                    json.dump(k, f, indent='\t', ensure_ascii=False)
                del self.cachedUsers[i]
            logging.info('UserManager cache cleared')


class CachedUser:
    def __init__(self, id: int):
        self.id = id
        self.UserManager = UserManager()
        if str(self.id) in self.UserManager.users():
            self.cachedUser = self.UserManager.cachedUsers.get(self.id, '')
            if not self.cachedUser:
                with open(self.UserManager.UsersFolder + str(id), 'r') as f:
                    self.cachedUser = json.load(f)
                self.UserManager.cachedUsers[id] = self.cachedUser
        else:
            raise Exceptions.NotRegistered(id)

    def save(self):
        with open(self.UserManager.UsersFolder + str(self.id), 'w') as f:
            json.dump(self.cachedUser, f, indent='\t', ensure_ascii=False)
