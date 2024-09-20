import future


# Función que detiene la estrategia por TP/SL
#--------------------------------------------
def detener_estrategia(exchange, symbol, sl, tp):
    try:
        
        # Función que mide la ganancia actual (en porcentaje %)
        # -----------------------------------------------------
        def ganancia_actual(exchange, balance_inicial):
            try:
                return 100*(future.patrimonio(exchange) - balance_inicial)/balance_inicial
            
            except Exception  as e:
                print("ERROR EN LA FUNCIÓN ganancia_actual()")
                print(e)
                print("")
        # -----------------------------------------------------

        # Función que cierra todo
        # -----------------------
        def cerrar_todo(exchange, symbol):
            try:
                print("CERRANDO ESTRTATEGIA...")
                future.cancelar_orden(exchange, symbol, orderId="")
                future.cerrar_posicion(exchange, symbol, "LONG")
                future.cerrar_posicion(exchange, symbol, "SHORT")
            
            except Exception as e:
                print("ERROR CERRANDO TODO")
                print(e)
                print("")
        # -----------------------

        # Iniciar gestión
        iniciar_estrategia = True

        # Balance inicial
        balance_inicial = future.patrimonio(exchange)

        while iniciar_estrategia:
            
            # Obtener la ganancia actual
            ganancia = ganancia_actual(exchange,balance_inicial)

            # Verificar la gestión
            if ganancia > 1.0011*tp or ganancia <= -abs(sl):
                cerrar_todo(exchange,symbol)
                iniciar_estrategia = False
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN detener_estrategia()")
        print(e)
        print("")
#--------------------------------------------