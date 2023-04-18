class NotRegistered(Exception):
    def __init__(self, id):
        super().__init__(f'{id}, not registered')