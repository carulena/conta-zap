import os
from http.server import BaseHTTPRequestHandler
 
# Configura o matplotlib para rodar em /tmp (Vercel serverless)
os.environ['MPLCONFIGDIR'] = '/tmp'
from io import BytesIO
from telegram import Update, Bot
import api.analisaDados as d
import pandas as pd
import json
import asyncio


# Inicializa o bot globalmente (sem criar servidor local)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)

class handler(BaseHTTPRequestHandler):
    
   def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)  # bytesupdate_json = json.loads(body)         # agora é dict
        update_json = json.loads(body)         # agora é dict
        update = Update.de_json(update_json, bot)
        chat_id = update.message.chat.id
        asyncio.run(bot.send_message(chat_id=chat_id, text="Recebi o ZIP!"))
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")
