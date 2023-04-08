import json


class User:
    def __init__(self, data):
        for k, v in data .items():
            self.__setattr__(k,v)

    def __str__(self):
        return str(self.__dict__)


class Update:
    def __init__(self, data):
        ...


class Message:
    ...


class Chat:
    def __init__(self, data):
        for k, v in data.items():
            self.__setattr__(k, v)
