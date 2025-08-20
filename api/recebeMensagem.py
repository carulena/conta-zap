import asyncio
import os
from http.server import BaseHTTPRequestHandler
 
# Configura o matplotlib para rodar em /tmp (Vercel serverless)
os.environ['MPLCONFIGDIR'] = '/tmp'
from io import BytesIO
from telegram import Update, Bot
import api.analisaDados as d
import telegram
import pandas as pd
from flask import Flask, request
import zipfile

# Inicializa bot
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)

app = Flask(__name__)

# ====================
# FUNÇÃO QUE PROCESSA O ZIP
# ====================
def handle_zip(file_bytes, chat_id):
    # Salva ZIP em /tmp
    file_path = "/tmp/recebido.zip"
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Extrai TXT
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        txt_name = [f for f in zip_ref.namelist() if f.endswith('.txt')][0]
        with zip_ref.open(txt_name) as f:
            linhas = f.read().decode("utf-8").splitlines()
    os.remove(file_path)

    # Processa dados
    cocos = d.criaDataframe(linhas)
    autores = d.agrupaPorAutor(cocos)
    tabela = d.criaTabela(autores)

    # Envia resultados
    bot.send_message(chat_id=chat_id, text=f"<pre>{tabela}</pre>", parse_mode="HTML")

    # Gera gráfico (opcional)
    porDia = d.graficoPorDia(cocos)
    with open(porDia, "rb") as photo:
        bot.send_photo(chat_id=chat_id, photo=photo)

# ====================
# ROTA PARA RECEBER WEBHOOK DO TELEGRAM
# ====================
@app.route("/webhook", methods=["POST"])
def webhook():
    update_json = request.get_json(force=True)
    update = Update.de_json(update_json, bot)

    if update.message and update.message.document:
        file_id = update.message.document.file_id
        file = asyncio.run(bot.get_file(file_id))                # coroutine
        file_bytes = asyncio.run(file.download_as_bytearray())   # coroutine
        handle_zip(file_bytes, update.message.chat.id)

    return "ok"

# ====================
# ROTA PÚBLICA (opcional) para teste
# ====================
@app.route("/")
def index():
    return "Bot rodando!"