import json
from typing import Dict


class User:
    def __init__(self, data: Dict):
        for k, v in data .items():
            self.__setattr__(k, v)

    def __repr__(self):
        return str(self.__dict__)


class Update:
    def __init__(self, data: Dict):
        types = {
            'message': Message,
            'edited_message': Message,
        }
        for k, v in data.items():
            a = types.get(k, v)
            if a != v:
                self.__setattr__(k, a(v))
            else:
                self.__setattr__(k, v)

    def __repr__(self):
        return str(self.__dict__)


class Message:
    def __init__(self, data: Dict):
        types = {
            'from': User,
            'chat': Chat
        }
        for k, v in data.items():
            a = types.get(k, v)
            if a != v:
                self.__setattr__(k, a(v))
            else:
                self.__setattr__(k, v)

    def __repr__(self):
        return str(self.__dict__)


class Chat:
    def __init__(self, data: Dict):
        for k, v in data.items():
            self.__setattr__(k, v)

    def __repr__(self):
        return str(self.__dict__)
