import zipfile
import pandas as pd
import os
os.environ['MPLCONFIGDIR'] = '/tmp'
from telegram import Update, Bot
import api.analisaDados as d
from flask import Request, jsonify
from httpx import Response

TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)
Bot(token=TOKEN)

def handler(request):
    # Vercel envia o método em minúsculas
    if request.method.lower() != "post":
        return {"error": "Método não permitido"}, 405

    try:
        update_json = request.get_json()  # já é dict
        update = Update.de_json(update_json, bot)

        if update.message and update.message.document:
            bot.send_message(chat_id=update.message.chat.id, text="Recebi o ZIP!")
            file = bot.get_file(update.message.document.file_id)

            # Baixa o ZIP para memória
            zip_bytes = BytesIO()
            file.download(out=zip_bytes)
            zip_bytes.seek(0)

            with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
                txt_name = [f for f in zip_ref.namelist() if f.endswith('.txt')][0]
                with zip_ref.open(txt_name) as f:
                    linhas = f.read().decode("utf-8").splitlines()

            cocos = d.criaDataframe(linhas)
            autores = d.agrupaPorAutor(cocos)
            tabela = d.criaTabela(autores)
            bot.send_message(chat_id=update.message.chat.id, text=f"<pre>{tabela}</pre>", parse_mode="HTML")

            porDia = d.graficoPorDia(cocos)
            with open(porDia, "rb") as photo:
                bot.send_photo(chat_id=update.message.chat.id, photo=photo)

        return {"ok": True}

    except Exception as e:
        return {"error": str(e)}, 500
