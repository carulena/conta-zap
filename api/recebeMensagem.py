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

# ====================
# FUNÇÃO QUE PROCESSA O ZIP
# ====================

# Função assíncrona não necessária, podemos usar função normal
def handle_zip(update_json):
    update = Update.de_json(update_json, bot)
    print("Update recebido:", update)
    print("Chat ID:", update.message.chat.id if update.message else "Sem mensagem")
    print("Document MIME type:", update.message.document.mime_type if update.message and update.message.document else "Nenhum documento")

    if update.message and update.message.document:
        bot.send_message(chat_id=update.message.chat.id, text="Recebi o ZIP!")
        file = bot.get_file(update.message.document.file_id)
        file_path = "/tmp/recebido.zip"
        file.download(file_path)
        
        # abrir zip e ler txt
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            txt_name = [f for f in zip_ref.namelist() if f.endswith('.txt')][0]
            with zip_ref.open(txt_name) as f:
                linhas = f.read().decode("utf-8").splitlines()
        os.remove(file_path)

        cocos = d.criaDataframe(linhas)
        autores = d.agrupaPorAutor(cocos)
        tabela = d.criaTabela(autores)
        bot.send_message(chat_id=update.message.chat.id, text=f"<pre>{tabela}</pre>", parse_mode="HTML")
        
        porDia = d.graficoPorDia(cocos)
        with open(porDia, "rb") as photo:
            bot.send_photo(chat_id=update.message.chat.id, photo=photo)

# ====================
# ROTA PARA RECEBER MENSAGENS DO TELEGRAM
# ====================
@app.route(f"/webhook", methods=["POST"])
def webhook():
    print("webhook")
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    
    if update.message and update.message.document:
        file_id = update.message.document.file_id
        file = bot.get_file(file_id)
        file_bytes = file.download_as_bytearray()
        
        resultado = handle_zip(file_bytes)
        bot.send_message(chat_id=update.message.chat.id, text=resultado)
    
    return "ok"

# ====================
# ROTA PÚBLICA (opcional) para teste
# ====================
@app.route("/")
def index():
    return "Bot rodando!"

# ====================
# EXECUÇÃO LOCAL (apenas para teste)
# ====================
if __name__ == "__main__":
    app.run(port=5000)