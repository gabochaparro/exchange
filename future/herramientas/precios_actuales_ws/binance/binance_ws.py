# CLASE QUE ESCUCHA LOS PRECIOS ACTUALES
# --------------------------------------
class PreciosActuales:
    def __init__(self):
        self.precios_actuales = {}

    async def precio_actual(self, symbol= "BTCUSDT"):
        import websockets
        import json
        import asyncio
        url = f"wss://fstream.binance.com/ws/{symbol.lower()}@aggTrade"
        while True:
            try:
                print("\nCONECTANDOSE AL WEBSOCKET DE BYBIT...\n")
                ws = None
                ws = await websockets.connect(url)

                async for mensaje in ws:
                    data = json.loads(mensaje)
                    symbol = data["s"]
                    price = data["p"]
                    self.precios_actuales[symbol] = price
                    print(self.precios_actuales)
            
            except Exception as e:
                await asyncio.sleep(3.6)
                print(f"ERROR ESCUCHANDO PRECIOS ACTUALES DE BYBIT\n{e}\n")
            finally:
                if ws and ws.open:
                    await ws.close()
# --------------------------------------

import asyncio
asyncio.run(PreciosActuales().precio_actual("ETHUSDT"))