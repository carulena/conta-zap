import pandas as pd 
import re
import matplotlib.pyplot as plt
from io import BytesIO
def criaDataframe(linhas):
    padrao = r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}) - (.*?): (.*)$"

    mensagens = []
    for msg in linhas:
        m = re.match(padrao, msg)
        if m:
            data, autor, texto = m.groups()
        else:
            # quando não tem autor (ex: "Cássia adicionou você")
            padrao_sem_autor = r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}) - (.*)$"
            m2 = re.match(padrao_sem_autor, msg)
            if m2:
                data, texto = m2.groups()
                autor = None
            else:
                continue
        mensagens.append([data, autor, texto])

    df = pd.DataFrame(mensagens, columns=["data", "autor", "mensagem"])

    df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y %H:%M')

    cocos = df[df['data'] > '2025-08-15 00:00:00']
    return filtraPorCocos(cocos)


def filtraPorCocos(cocos):
    emoji = "💩"

    # Filtrar
    cocos = cocos[cocos['mensagem'].str.contains(emoji, regex=False) & 
    (cocos['mensagem'].str.len() > 1)]
    return cocos
    
def agrupaPorAutor(cocos):
    resumo = cocos.groupby('autor').agg(
    cocos=('mensagem', 'count') 
    ).reset_index().sort_values(by='cocos',  ascending=False)
    return resumo
    
def criaTabela(resumo):
    tabela = "Autor       | Total cocos\n"
    tabela += "-------------------------\n"
    for _, row in resumo.iterrows():
        tabela += f"{row['autor']:<10} | {row['cocos']}\n"
        
    return tabela


def graficoPorDia(cocos, arquivo="tabela.png"):
    cocos['dia'] = cocos['data'].dt.date

    # contar mensagens por dia e por autor
    contagem = cocos.groupby(['dia', 'autor'])['mensagem'].count().reset_index()
    contagem = contagem.rename(columns={'mensagem': 'total_mensagens'})

    print(contagem)
    pivot = contagem.pivot(index='dia', columns='autor', values='total_mensagens').fillna(0)

    pivot.plot(kind='line', marker='o', figsize=(10,6))
    plt.title("Mensagens por dia por autor")
    plt.xlabel("Dia")
    plt.ylabel("Número de mensagens")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend(title="Autor")
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf 

