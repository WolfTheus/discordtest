import discord
from discord.ext import tasks, commands
from discord import app_commands
import os
import random
from datetime import datetime
import requests
import unicodedata
from dotenv import load_dotenv

# Carrega variáveis .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("DISCORD_TOKEN não está configurado")

WEATHER_TOKEN = os.getenv("OPENWEATHER_TOKEN")

# Intents e criação do bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)  # NÃO cria nova tree!
# Usa bot.tree direto (já existe internamente)
# === Função utilitária ===
def limpar_nome_cidade(cidade):
    cidade = cidade.lower().strip()
    cidade = unicodedata.normalize('NFD', cidade)
    cidade = cidade.encode('ascii', 'ignore').decode('utf-8')
    return cidade

# === Slash Commands ===

@bot.tree.command(name="ping", description="Responde com Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

@bot.tree.command(name="hora", description="Mostra a data e hora atual")
async def hora(interaction: discord.Interaction):
    agora = datetime.now()
    hora_formatada = agora.strftime("%H:%M:%S")
    data_formatada = agora.strftime("%d/%m/%Y")
    await interaction.response.send_message(f"📅 Hoje é {data_formatada}, 🕒 agora são {hora_formatada}.")

@bot.tree.command(name="motivacao", description="Receba uma frase motivacional aleatória")
async def motivacao(interaction: discord.Interaction):
    frases = [
        "💪 Você é mais forte do que imagina!",
        "🚀 Não desista agora, o sucesso está perto!",
        "🏃 Cada passo conta. Continue em frente!",
        "🌟 Grandes coisas levam tempo. Continue tentando!"
    ]
    frase = random.choice(frases)
    await interaction.response.send_message(frase)

@bot.tree.command(name="clima", description="Veja o clima de uma cidade")
@app_commands.describe(cidade="Nome da cidade desejada")
async def clima(interaction: discord.Interaction, cidade: str):
    cidade = limpar_nome_cidade(cidade)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={WEATHER_TOKEN}&lang=pt_br&units=metric"
    resposta = requests.get(url)

    if resposta.status_code == 200:
        dados = resposta.json()
        nome = dados["name"]
        pais = dados["sys"]["country"]
        temp = dados["main"]["temp"]
        descricao = dados["weather"][0]["description"]
        sensacao = dados["main"]["feels_like"]
        umidade = dados["main"]["humidity"]

        mensagem = (
            f"🌤️ **Clima em {nome}, {pais}**\n"
            f"🌡️ Temperatura: **{temp}°C**\n"
            f"🥵 Sensação Térmica: **{sensacao}°C**\n"
            f"📝 Descrição: **{descricao.capitalize()}**\n"
            f"💧 Umidade: **{umidade}%**"
        )
    else:
        mensagem = "❌ Cidade não encontrada. Verifique se digitou corretamente."

    await interaction.response.send_message(mensagem)

# === Mantém o bot acordado com mensagens automáticas ===
@tasks.loop(minutes=10)
async def manter_online():
    canal = discord.utils.get(bot.get_all_channels(), name="no-sleep")
    if canal:
        await canal.send("💤 Estou acordado! Só conferindo o sistema...")

# === Evento on_ready ===
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot conectado como {bot.user}")
    manter_online.start()

bot.run(TOKEN)
