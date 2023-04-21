import Bot
import threading


class LoadBalancer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.bots = [Bot.Bot()]
        self.tasks = []
        super().start()

    def run(self):
        while True:
            if self.tasks:
                while self.tasks:
                    self.bots.sort(key=lambda x: x.getLoad())
                    self.bots[0].tasks.append(self.tasks.pop())
                     