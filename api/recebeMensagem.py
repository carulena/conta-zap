import zipfile
import pandas as pd
import os
os.environ['MPLCONFIGDIR'] = '/tmp'
from telegram import Update, Bot
import api.analisaDados as d
from flask import Request, jsonify

TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)

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

def handler(request: Request):
    if request.method != "POST":
        return jsonify({"error": "Método não permitido"}), 405

    update_json = request.get_json(force=True)
    handle_zip(update_json)
    return jsonify({"ok": True})
