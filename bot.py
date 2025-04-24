import asyncio
import requests
from telegram import Bot

# Telegram
TOKEN = "7757204285:AAH1cKohAVRBcIHEEV7h7bCLnefn5hNyk44"
CHAT_ID = "7743912374"
CHECK_INTERVAL = 300  # 5 minutos
THRESHOLD = 1200

# CoinMarketCap
API_KEY = "adc709da-b834-48b8-95c4-e9f5da9debae"
CMC_HEADERS = {
    'X-CMC_PRO_API_KEY': API_KEY,
    'Accept': 'application/json'
}

bot = Bot(token=TOKEN)

def get_btc_price():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    params = {
        'symbol': 'BTC',
        'convert': 'USD'
    }
    response = requests.get(url, headers=CMC_HEADERS, params=params)
    if response.status_code != 200:
        raise Exception(f"Erro na API: {response.status_code} - {response.text}")
    data = response.json()
    return data['data']['BTC']['quote']['USD']['price']

# Simulando histórico com chamadas repetidas (já que o plano gratuito da CMC não oferece histórico por hora)
precos_simulados = []

def get_price_history():
    global precos_simulados
    atual = get_btc_price()
    precos_simulados.append(atual)
    if len(precos_simulados) > 24:
        precos_simulados.pop(0)
    return precos_simulados

def analyze_trend():
    prices = get_price_history()
    if len(prices) < 5:
        return "Dados insuficientes para análise."
    media = sum(prices[-5:]) / 5
    atual = prices[-1]
    if atual > media:
        return "Tendência de ALTA - possível momento de compra."
    elif atual < media:
        return "Tendência de BAIXA - possível recuada no preço."
    return "Sem tendência clara."

async def send_alert(text):
    await bot.send_message(chat_id=CHAT_ID, text=text)

async def monitor():
    last_price = get_btc_price()
    trend = analyze_trend()
    await send_alert(f"Monitoramento iniciado: ${last_price:.2f}\n{trend}")

    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        try:
            current_price = get_btc_price()
            trend = analyze_trend()
            diff = current_price - last_price
            if abs(diff) >= THRESHOLD:
                direction = "subiu" if diff > 0 else "caiu"
                await send_alert(
                    f"O Bitcoin {direction} ${abs(diff):.2f} e está em ${current_price:.2f}\n{trend}"
                )
                last_price = current_price
        except Exception as e:
            await send_alert(f"Erro: {e}")

if __name__ == "__main__":
    asyncio.run(monitor())
