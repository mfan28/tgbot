import aiohttp
from . import DataTypes
import json
from typing import List


class Telegram():
    def __init__(self, token: str):
        self.session = aiohttp.ClientSession()
        self.apiEndpoint = f'https://api.telegram.org/bot{token}/'
        self.offset = 0
        
    async def getMe(self) -> DataTypes.User:
        async with self.session.get(self.apiEndpoint + 'getMe') as response:
            if await json.loads(response.text())['ok']:
                return DataTypes.User(json.loads(await response.text())['result'])

    async def getUpdates(self) -> List:
        async with self.session.get(self.apiEndpoint + 'getUpdates', params={'timeout': 10, 'offset': self.offset}) as response:
            response = json.loads(await response.text())
            if response['ok'] and response['result']:
                self.offset = response['result'][-1]['update_id'] + 1
                return [DataTypes.Update(i) for i in response['result']]
            else:
                return []
