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
        print("hey, I'm inside your function")
        if self.request.method.lower() != "post":
            return {"error": "Método não permitido"}, 405

        try:
            # Pega o JSON enviado pelo Telegram
            update_json = request.get_json()
            update = Update.de_json(update_json, bot)

            if update.message and update.message.document:
                chat_id = update.message.chat.id
                bot.send_message(chat_id=chat_id, text="Recebi o ZIP!")

                # Baixa o arquivo ZIP
                file = bot.get_file(update.message.document.file_id)
                zip_bytes = BytesIO()
                file.download(out=zip_bytes)
                zip_bytes.seek(0)

                # Lê o arquivo TXT dentro do ZIP
                with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
                    txt_name = [f for f in zip_ref.namelist() if f.endswith('.txt')][0]
                    with zip_ref.open(txt_name) as f:
                        linhas = f.read().decode("utf-8").splitlines()

                # Processa os dados com suas funções
                cocos = d.criaDataframe(linhas)
                autores = d.agrupaPorAutor(cocos)
                tabela = d.criaTabela(autores)

                bot.send_message(chat_id=chat_id, text=f"<pre>{tabela}</pre>", parse_mode="HTML")

                # Gera o gráfico e envia
                porDia = d.graficoPorDia(cocos)
                with open(porDia, "rb") as photo:
                    bot.send_photo(chat_id=chat_id, photo=photo)

            return {"ok": True}

        except Exception as e:
            return {"error": str(e)}, 500