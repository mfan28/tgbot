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
        try:
            a = update.message.text
        except Exception:
            return False
        if self.text in update.message.text:
            asyncio.create_task(self.callback(bot, update))
            return True
        else:
            return False


class CommandHandler(Handler):
    def __init__(self, command: str, callback: Callable, description: str):
        super().__init__('/' + command, callback)
        self.command = command
        self.callback = callback
        self.description = description

    def __repr__(self):
        return super().__repr__()

    async def check(self, bot: Telegram, update: DataTypes.Update) -> bool:
        return await super().check(bot, update)

