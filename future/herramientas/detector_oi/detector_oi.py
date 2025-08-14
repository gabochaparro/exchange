import requests
import json
import time

api_key = "da505233-6424-4583-a67b-aba469de62f1"

def obtener_exchanges():
    
    url = "https://api.coinalyze.net/v1/exchanges"
    headers = {
        "Authorization": f"Token {api_key}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(e)

def obtener_mercados():
    
    url = "https://api.coinalyze.net/v1/future-markets"
    headers = {
        "Authorization": f"Token {api_key}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(e)

def obtener_open_interest(symbol, convertir_a_usd=False):
    
    url = "https://api.coinalyze.net/v1/open-interest"
    
    headers = {
        "Authorization": f"Token {api_key}"
    }
    
    binance = "A"
    bybit = "6"
    okx = "3"
    coinbase = "C"
    simbolos = []
    mercados = obtener_mercados()
    
    for mercado in mercados:
        if symbol.upper() == mercado['base_asset'] and (mercado['exchange'] == binance or mercado['exchange'] == bybit or mercado['exchange'] == coinbase or mercado['exchange'] == okx):
            #print(json.dumps(mercado, indent=2))
            simbolos.append(mercado['symbol'])
                
    params = {
        "symbols": ",".join(simbolos),
        "convert_to_usd": "true" if convertir_a_usd else "false"
    }

    try:
        print(simbolos)
        print(params['symbols'])
        if simbolos != []:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            print(json.dumps(response.json(), indent=2))
            time.sleep(5)
    except requests.exceptions.HTTPError as errh:
        print("❌ Error HTTP:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("❌ Error de conexión:", errc)
    except requests.exceptions.Timeout as errt:
        print("❌ Tiempo de espera agotado:", errt)
    except requests.exceptions.RequestException as err:
        print("❌ Error inesperado:", err)

#respuesta = obtener_exchanges()
#respuesta = obtener_mercados()
respuesta = obtener_open_interest("ETH", True)
#print(json.dumps(respuesta, indent=2))