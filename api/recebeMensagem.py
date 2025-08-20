import os
from http.server import BaseHTTPRequestHandler
 
# Configura o matplotlib para rodar em /tmp (Vercel serverless)
os.environ['MPLCONFIGDIR'] = '/tmp'
import zipfile
from io import BytesIO
from telegram import Update, Bot
import api.analisaDados as d
import pandas as pd


# Inicializa o bot globalmente (sem criar servidor local)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)

class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        print(self)
        update_json = self.request.get_json()
        update = Update.de_json(update_json, bot)
        chat_id = update.message.chat.id
        bot.send_message(chat_id=chat_id, text="Recebi o ZIP!")
       