import os
import json
from Telegram.DataTypes import *


class UserManager:
    def __init__(self):
        self.UsersFolder = './UserManager/Users/'
        self.users = [i for i in os.listdir(self.UsersFolder)]
        self.cachedUsers = {}
        
    def createUser(self, user: User):
        if str(user.id) not in self.users:
            with open(self.UsersFolder + str(user.id), 'w') as f:
                json.dump({'id': user.id, 'username': user.username, 'context': []}, f)
    
    def __getitem__(self, item):
        user = str(item)
        if user in self.users:
            b = self.cachedUsers.get(user, '')
            if not b:
                with open(self.UsersFolder + user, 'r') as f:
                    a = json.load(f)
                    self.cachedUsers[user] = a
                    return a
            else:
                return b
        else:
            return None
    
    class CachedUser:
        def __init__(self, data):
            self.data = data
            
        def __del__(self):
            del self
        