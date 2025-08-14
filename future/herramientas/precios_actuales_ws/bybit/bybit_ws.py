# CLASE QUE ESCUCHA LOS PRECIOS ACTUALES
# --------------------------------------
class PreciosActuales:
    def __init__(self):
        self.precios_actuales = {}

    async def precio_actual(self,tipo="linear", symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]):
        import websockets
        import json
        import asyncio
        url = f"wss://stream.bybit.com/v5/public/{tipo.lower()}"
        while True:
            try:
                print("\nCONECTANDOSE AL WEBSOCKET DE BYBIT...\n")
                ws = None
                ws = await websockets.connect(url)
                await ws.send(json.dumps({"op": "subscribe", "args": [f"publicTrade.{s.upper()}" for s in symbols]}))

                async for mensaje in ws:
                    if "data" in mensaje:
                        data = json.loads(mensaje)
                        symbol = data["data"][0]["s"]
                        price = data["data"][0]["p"]
                        self.precios_actuales[symbol] = price
                        #print(self.precios_actuales)
            
            except Exception as e:
                await asyncio.sleep(3.6)
                print(f"ERROR ESCUCHANDO PRECIOS ACTUALES DE BYBIT\n{e}\n")
            finally:
                if ws and ws.open:
                    await ws.close()
# --------------------------------------

#import asyncio
#asyncio.run(PreciosActuales().precio_actual("INVERSE", ["btcusd"]))