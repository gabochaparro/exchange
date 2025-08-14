# CLASE QUE ESCUCHA LOS PRECIOS ACTUALES
# --------------------------------------
class PreciosActuales:
    def __init__(self):
        self.precio_actual = {}

    async def precio_actual_activo(self, tipo ="f",  symbol= "BTCUSDT"): #tipo = "d" para inversos
        import websockets
        import json
        import asyncio
        url = f"wss://{tipo.lower()}stream.binance.com/ws/{symbol.lower()}@aggTrade"
        while True:
            try:
                print("\nCONECTANDOSE AL WEBSOCKET DE BINANCE...\n")
                ws = None
                ws = await websockets.connect(url)

                async for mensaje in ws:
                    data = json.loads(mensaje)
                    symbol = data["s"]
                    price = float(data["p"])
                    self.precio_actual[symbol] = price
                    #print(self.precio_actual)
            
            except Exception as e:
                await asyncio.sleep(3.6)
                print(f"ERROR ESCUCHANDO PRECIOS ACTUALES DE BINANCE\n{e}\n")
            finally:
                if ws and ws.open:
                    await ws.close()
# --------------------------------------

#import asyncio
#asyncio.run(PreciosActuales().precio_actual_activo("D", "opusd_PERP"))