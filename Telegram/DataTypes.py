import json


class User:
    def __init__(self, filePath):
        with open(filePath, 'r') as f:
            self.data = json.load(f)
    
    def __str__(self):
        return self.data['username']