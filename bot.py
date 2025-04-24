import asyncio
import requests
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = "7757204285:AAH1cKohAVRBcIHEEV7h7bCLnefn5hNyk44"
CHAT_ID = "7743912374"
CHECK_INTERVAL = 180
THRESHOLD = 1200

bot = Bot(token=TOKEN)

def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return data["bitcoin"]["usd"]

def get_price_history():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1&interval=hourly"
    response = requests.get(url)
    data = response.json()
    prices = [p[1] for p in data["prices"]]
    return prices

def analyze_trend():
    prices = get_price_history()
    if len(prices) < 5:
        return "Dados insuficientes para análise."
    media = sum(prices[-5:]) / 5
    atual = prices[-1]
    if atual > media:
        return "Tendência de ALTA"
    elif atual < media:
        return "Tendência de BAIXA"
    return "Sem tendência clara."

async def send_alert(text):
    await bot.send_message(chat_id=CHAT_ID, text=text)

async def monitor():
    last_price = get_btc_price()
    await send_alert(f"Monitoramento iniciado: ${last_price:.2f}")
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        try:
            current_price = get_btc_price()
            diff = abs(current_price - last_price)
            if diff >= THRESHOLD:
                direction = "subiu" if current_price > last_price else "caiu"
                trend = analyze_trend()
                await send_alert(f"O Bitcoin {direction} ${diff:.2f} e está em ${current_price:.2f}
{trend}")
                last_price = current_price
        except Exception as e:
            await send_alert(f"Erro: {e}")

if __name__ == "__main__":
    asyncio.run(monitor())