import aiohttp
from . import DataTypes
import json


class Telegram():
    def __init__(self, token: str):
        self.session = aiohttp.ClientSession()
        self.apiEndpoint = f'https://api.telegram.org/bot{token}/'
        
    async def getMe(self):
        async with self.session.get(self.apiEndpoint + 'getMe') as response:
            if await json.loads(response.text())['ok']:
                return DataTypes.User(json.loads(await response.text())['result'])

    async def getUpdates(self):
        async with self.session.get(self.apiEndpoint + 'getUpdates') as response:
            response = json.loads(await response.text())
            if response['ok']:
                return [DataTypes.Update(i) for i in response['result']]