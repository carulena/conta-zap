import zipfile
import pandas as pd
import os
from telegram import Update, Bot
from telegram.ext import ContextTypes
import analisaDados as d
from flask import Flask, request, jsonify

# Inicializa Flask
app = Flask(__name__)

# Lê token do ambiente (melhor do que token.txt)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)

# Função assíncrona não necessária, podemos usar função normal
def handle_zip(update_json):
    update = Update.de_json(update_json, bot)
    
    if update.message and update.message.document:
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

# Rota webhook
@app.route("/api/webhook", methods=["POST"])
def webhook():
    update_json = request.get_json(force=True)
    handle_zip(update_json)
    return jsonify({"ok": True})