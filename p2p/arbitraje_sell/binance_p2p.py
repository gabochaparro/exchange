import requests
import json

def obtener_anuncios(symbol, fiat, tipo, monto, bancos=[], verificado = False, cantidad=1):
    try:
        anuncios = []
        pagina = 0
        while len(anuncios) < cantidad:
            pagina = pagina + 1
            url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            payload = {
                "asset": symbol.upper(),        # Cripto: USDT, BTC, BUSD, etc.
                "fiat": fiat.upper(),           # Moneda local: COP, ARS, USD, MXN, etc.
                "tradeType": tipo.upper(),      # SELL = vendedores, BUY = compradores
                "page": pagina,                      # Pagina
                "rows": 20                      # Número de anuncios a devolver
            }

            response = requests.post(url, headers=headers, json=payload)

            # Obtener los anuncios deseados
            if response.ok or str(response.status_code) == "200":
                data = response.json()['data']
                #print(json.dumps(data[0], indent=2, ensure_ascii=False))
                for dato in data:
                    anuncio = dato['adv']
                    metodos_pagos = anuncio['tradeMethods']
                    anunciante = dato['advertiser']
                    
                    if verificado:
                        for metodo in metodos_pagos:
                            if metodo['payType'] in bancos:
                                if anunciante['vipLevel'] != None and anunciante['vipLevel'] >= 1 and ((float(anuncio['minSingleTransAmount']) <= float(monto) and float(anuncio['maxSingleTransAmount']) >= float(monto)) or monto == 0):
                                    #print(json.dumps(dato, indent=2, ensure_ascii=False))
                                    metodos = []
                                    for metodo in metodos_pagos:
                                        metodos.append(metodo['payType'])
                                    anuncios.append({
                                        "nickName": anunciante['nickName'],
                                        "precio":anuncio['price'],
                                        "minimo": anuncio['minSingleTransAmount'],
                                        "maximo": anuncio['maxSingleTransAmount'],
                                        "disponible": f"{anuncio['tradableQuantity']} {symbol.upper()}",
                                        "bancos": metodos
                                        })
                                    break
                    else:
                        for metodo in metodos_pagos:
                            if metodo['payType'] in bancos:
                                if (float(anuncio['minSingleTransAmount']) <= float(monto) and float(anuncio['maxSingleTransAmount']) >= float(monto)) or monto == 0:
                                    #print(json.dumps(dato, indent=2, ensure_ascii=False))
                                    metodos = []
                                    for metodo in metodos_pagos:
                                        metodos.append(metodo['payType'])
                                    anuncios.append({
                                        "nickName": anunciante['nickName'],
                                        "precio":anuncio['price'],
                                        "minimo": anuncio['minSingleTransAmount'],
                                        "maximo": anuncio['maxSingleTransAmount'],
                                        "disponible": f"{anuncio['tradableQuantity']} {symbol.upper()}",
                                        "bancos": metodos
                                        })
                                    break
                    
                    if len(anuncios) == cantidad:
                        break

                if len(anuncios) == cantidad:
                    break
            
            else:
                print("ERROR DE REQUEST:", response.status_code)
                return response.status_code

        return anuncios

    except Exception as e:
        print(f"\nERROR EN LA FUNCION: obtener_anuncios()\n{e}")

if __name__ == "__main__":
    anuncios = obtener_anuncios(symbol="usdt", fiat="cop", tipo="sell", monto=0, bancos=["Nequi", "BancolombiaSA"], verificado=False, cantidad=3)
    print(json.dumps(anuncios, indent=2))