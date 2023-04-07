import aiohttp
from . import DataTypes
import json

class Telegram():
    def __init__(self, token: str):
        self.session = aiohttp.ClientSession()
        self.apiEndpoint = f'https://api.telegram.org/bot{token}/'
        
    async def getMe(self):
        async with self.session.get(self.apiEndpoint + 'getMe') as response:
            return DataTypes.User(json.loads(await response.text())['result'])