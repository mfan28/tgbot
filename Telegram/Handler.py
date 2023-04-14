from typing import Callable
from . import DataTypes
from . import Telegram
import asyncio


class Handler:
    def __init__(self, text: str, callback: Callable):
        self.text = text
        self.callback = callback
        
    def __repr__(self):
        return f'((HANDLER) (CALLBACK = {self.callback}) (TEXT = {self.text}))'

    async def check(self, bot: Telegram, update: DataTypes.Update) -> bool:
        if self.text in update.message.text:
            await self.callback(bot, update)
            return True
        else:
            return False
        