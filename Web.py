import Telegram
from flask import Flask, request
import LoadBalancer
import config
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
app = Flask(__name__)
tele = Telegram.Telegram(config.TELEGRAM_API_KEY, url=f'https://{config.HOST}:{config.PORT}', cert=config.CERT)
asyncio.run(tele.setWebhook())
Balancer = LoadBalancer.LoadBalancer()

@app.route('/', methods=['POST'])
def index():
    Balancer.tasks.append(Telegram.DataTypes.Update(request.json))
    return ''
    