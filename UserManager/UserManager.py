import os
import json
from Telegram.DataTypes import *
from Singleton import singleton

@singleton
class UserManager:
    def __init__(self):
        self.UsersFolder = './UserManager/Users/'
        self.users = [i for i in os.listdir(self.UsersFolder)]
        self.cachedUsers = {}
        
    def createUser(self, chat: Chat):
        if str(chat.id) not in self.users:
            with open(self.UsersFolder + str(chat.id), 'w') as f:
                json.dump({'id': chat.id, 'username': chat.username, 'context': []}, f)
    
    def __getitem__(self, item):
        return CachedUser(item)
    
class CachedUser:
    def __init__(self,  id: int):
        self.id = id
        self.UserManager = UserManager()
        if str(self.id) in self.UserManager.users:
            cachedUser = self.UserManager.cachedUsers.get(self.id, '')
            if not cachedUser:
                ...
        