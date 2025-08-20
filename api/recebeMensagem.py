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
# Inicializa o bot globalmente (sem criar servidor local)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)

app = Flask(__name__)

async def download_file(file_id):
    f = await bot.get_file(file_id)
    return await f.download_as_bytearray()

async def send_message(chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text)

async def send_photo(chat_id, photo_bytes):
    await bot.send_photo(chat_id=chat_id, photo=photo_bytes)

# ====================
# FUNÇÃO QUE PROCESSA O ZIP
# ====================
async def handle_zip(file_bytes, chat_id):
    # Salva temporariamente em /tmp
    file_path = "/tmp/recebido.zip"
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # abrir zip e ler txt
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        txt_name = [f for f in zip_ref.namelist() if f.endswith('.txt')][0]
        with zip_ref.open(txt_name) as f:
            linhas = f.read().decode("utf-8").splitlines()
    os.remove(file_path)

    cocos = d.criaDataframe(linhas)
    autores = d.agrupaPorAutor(cocos)
    tabela = d.criaTabela(autores)
    
    # Envia mensagens assíncronas
    await send_message(chat_id, f"{tabela}")
    
    # porDia = d.graficoPorDia(cocos)
    # with open(porDia, "rb") as photo:
    #     loop.run_until_complete(send_photo(chat_id, photo.read()))

# ====================
# ROTA PARA RECEBER MENSAGENS DO TELEGRAM
# ====================
@app.route("/webhook", methods=["POST", "GET"])
async def webhook():
    if request.method == "GET":
        return "Webhook ativo!"

    update_json = request.get_json(force=True)
    update = Update.de_json(update_json, bot)

    if update.message and update.message.document:
        file_id = update.message.document.file_id
        file_bytes = await download_file(file_id)  # 🔹 baixar bytes do ZIP
        await handle_zip(file_bytes, update.message.chat.id)

    return "ok"
# ====================
# ROTA PÚBLICA (opcional) para teste
# ====================
@app.route("/")
def index():
    return "Bot rodando!"

# ====================
# EXECUÇÃO LOCAL (apenas para teste)
# # ====================
# if __name__ == "__main__":
#     app.run(port=5000)