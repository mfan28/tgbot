from typing import Callable
from . import DataTypes
from . import Telegram


class Handler:
    def __init__(self, text: str, callback: Callable):
        self.text = text
        self.callback = callback
        
    def check(self, bot: Telegram, update: DataTypes.Update):
        if self.text in update.message.text:
            self.callback(bot, update)
        