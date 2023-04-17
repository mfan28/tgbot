import Telegram
from flask import Flask, request
import config

app = Flask(__name__)
bot = Telegram.Telegram(config.TELEGRAM_API_KEY)

@app.route('/', methods=['POST', 'GET'])
def index():
    for i in request.json:
        print(i)
    return request.args
    
if __name__ == '__main__':
    app.run(host=config.HOST, debug=True)