import credenciales
import requests
import hashlib
import hmac
import time
import json

def coinex(method, path, params=None):
    try:
        # Construir la URL completa
        url = "https://api.coinex.com/v2" + path
        print(url)

        # Credenciales
        access_id = credenciales.coinex_api_key
        api_secret = credenciales.coinex_api_secret
    
        # Añadir parámetros de autenticación
        if params is None:
            params = {}
        timestamp = str(int(time.time() * 1000))
        params['access_id'] = access_id
        params['tonce'] = timestamp
        
        # Crear una cadena de consulta de parámetros ordenada
        query_string = '&'.join([f"{key}={params[key]}" for key in sorted(params)])
        
        # Concatenar los componentes para la firma
        if query_string:
            prepared_str = f"{method.upper()}{path}?{query_string}{timestamp}"
        else:
            prepared_str = f"{method.upper()}{path}{timestamp}"
        print("String to sign:", prepared_str)
        
        # Firmar el string
        signed_str = hmac.new(bytes(api_secret, 'latin-1'), msg=bytes(prepared_str, 'latin-1'), digestmod=hashlib.sha256).hexdigest().lower()

        # Headers de la petición
        headers = {
            'X-COINEX-KEY': access_id,
            'X-COINEX-SIGN': signed_str,
            'X-COINEX-TIMESTAMP': timestamp
        }
        
        # Hacer la petición
        response = requests.request(method=method, url=url, params=params, headers=headers, data=None)

        # Verificar si la petición fue exitosa
        if response.status_code == 200:
            # Retornar el contenido de la respuesta
            return response.json()
        else:
            print("ERROR EN EL REQUEST:", response.status_code, response.text)
            return None

    except Exception as e:
        print("ERROR EN LA PETICIÓN DE COINEX")
        print(e)
        return None

# Parametros
method = "GET"
path = "/futures/pending-position"
params = {
    "market": "BTCUSDT",
    "market_type": "FUTURES"
}

prueba = coinex(method=method, path=path, params=params)
print(json.dumps(prueba, indent=2))
