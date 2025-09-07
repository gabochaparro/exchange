# FUNCION PARA SOLICITAR LAS CREDENCIALES DE CUALQUIER EXCHANGE
# -------------------------------------------------------------
def solicitar_credenciales(exchange: str, debug: bool =False):
    credenciales = False
    
    # Solicitar credenciales de Bybit
    # -------------------------------
    if exchange.upper() == "BYBIT":
        while not credenciales:
            try:
                from pybit.unified_trading import HTTP
                
                # Solicitar credenciales
                # ----------------------
                api_key = input("\nIntroduce tu Api Key de Bybit: \n-> ")
                api_secret = input("\nIntroduce tu Api Secret de Bybit: \n-> ")
                # ----------------------

                # Definir la session para Bybit
                # -----------------------------
                bybit_session = HTTP(
                                    testnet=False,
                                    api_key=api_key,
                                    api_secret=api_secret,
                                    )
                bybit_session.get_api_key_information()
                credenciales = True
                return bybit_session
                # -----------------------------
            except Exception as e:
                print("\n⚠️  No pude conectarme a Bybit ⚠️  Revisa tus credenciales")
                if debug:
                    print(f"\n{e}")
        # -------------------------------
    
    # Solicitar credenciales de Binance
    # -------------------------------
    if exchange.upper() == "BINANCE":
        while not credenciales:
            try:
                from binance.client import Client
                
                # Solicitar credenciales
                # ----------------------
                api_key = input("\nIntroduce tu Api Key de Binance: \n-> ")
                api_secret = input("\nIntroduce tu Api Secret de Binance: \n-> ")
                # ----------------------

                # Definir el cliente para Binance
                # -------------------------------
                binance_client = Client(
                                            api_key=api_key,
                                            api_secret=api_secret,
                                            tld="com"
                                        )
                binance_client.get_account_api_permissions()
                credenciales = True
                return binance_client
                # -------------------------------
            except Exception as e:
                print("\n⚠️  No pude conectarme a Binance ⚠️  Revisa tus credenciales")
                if debug:
                    print(f"\n{e}")
        # -------------------------------
# -------------------------------------------------------------