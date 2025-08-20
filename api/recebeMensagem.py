import os
os.environ['MPLCONFIGDIR'] = '/tmp'
import zipfile
from fastapi import FastAPI, Request
import asyncio
from telegram import Bot, Update
import api.analisaDados as d

# Config matplotlib para Vercel

# Bot
TOKEN = os.environ["TELEGRAM_TOKEN"]
bot = Bot(token=TOKEN)

# FastAPI app
app = FastAPI()

async def handle_zip(file_bytes, chat_id):
    file_path = "/tmp/recebido.zip"
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        txt_name = [f for f in zip_ref.namelist() if f.endswith(".txt")][0]
        with zip_ref.open(txt_name) as f:
            linhas = f.read().decode("utf-8").splitlines()
    os.remove(file_path)

    # Processa dados
    cocos = d.criaDataframe(linhas)
    autores = d.agrupaPorAutor(cocos)
    tabela = d.criaTabela(autores)

    await bot.send_message(chat_id, f"<pre>{tabela}</pre>", parse_mode="HTML")

    porDia = d.graficoPorDia(cocos)
    with open(porDia, "rb") as photo:
        await bot.send_photo(chat_id, photo=photo)

@app.post("/webhook")
async def webhook(request: Request):
    update_json = await request.json()
    update = Update.de_json(update_json, bot)

    if update.message and update.message.document:
        file_id = update.message.document.file_id
        file = await bot.get_file(file_id)
        file_bytes = await file.download_as_bytearray()

        # não bloqueia resposta → processa em background
        asyncio.create_task(handle_zip(file_bytes, update.message.chat.id))

    # resposta imediata para o Telegram não reenviar várias vezes
    return {"ok": True}

@app.get("/")
async def index():
    return {"status": "Bot rodando!"}
