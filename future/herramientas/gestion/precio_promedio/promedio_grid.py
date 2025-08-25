'''
Función que calcula el precio promedio y el precio de liquidación de un grid
'''
def promedio_grid(precio_actual, inversion, intervalo, monto_por_compra, apalancamiento):
    cantidad_grid =int(inversion*apalancamiento/monto_por_compra)
    print("CANTIDAD DE GRILLAS:",cantidad_grid)
    intervalo = intervalo/100
    lista_precio = [precio_actual]
    sumatoria_precio = 0
    precio_promedio = precio_actual
    precio_liquidacion = precio_promedio*(1-inversion/monto_por_compra)

    while cantidad_grid > 1:
        lista_precio.append(lista_precio[-1]/(1+intervalo))
        cantidad_grid = cantidad_grid - 1

    for precio in lista_precio:
        sumatoria_precio = sumatoria_precio + precio
        indice = lista_precio.index(precio)
        ultimo_precio = precio
        if precio > precio_liquidacion:
            precio_promedio = sumatoria_precio/(indice+1)
            precio_liquidacion = precio_promedio*(1-inversion/((indice+1)*monto_por_compra))
        else:
            ultimo_precio = lista_precio[indice-1]
            indice = indice-1
            break
    
    print("")
    print("Inversión:", inversion, "USDT")
    print(f"Apalancamiento: {int(apalancamiento)}x")
    print("Cantidad de grid:", indice+1)
    print("Monto por cada compra:", monto_por_compra, "USDT")
    print(f"Rango de cobertura: ({ultimo_precio} , {lista_precio[0]}) ({round(100*(precio_actual-ultimo_precio)/precio_actual,2)}%)")
    print(f"Precio Promedio: {precio_promedio} ({round(100*((precio_actual-precio_promedio)/precio_actual),2)}%)")
    print(f"Precio Liquidación: {precio_liquidacion} ({round(100*((precio_actual-precio_liquidacion)/precio_actual),2)}%)")
    print("")

continuar = True
while continuar:
    try:
        comision = 0         #float(input("Comisión del broker: "))
        inversion = 10000        #float(input("Introduce el monto de la inversión: "))
        apalancamiento = 5      #float(input("Introduce el apalancamiento: "))
        precio_actual = 23539    #float(input("Introduce el precio actual: "))
        distancia_grid = 0.18    #float(input("Introduce la distancia del grid: "))
        ganancia_grid = 0.018       #float(input("Introduce la ganancia por grid: "))

        promedio_grid( 
                        apalancamiento=apalancamiento,
                        inversion=inversion,
                        precio_actual=precio_actual, 
                        intervalo=distancia_grid+2*comision, 
                        monto_por_compra=inversion*ganancia_grid/distancia_grid
                    )
    
    except Exception as e:
        print("Valor incorrecto")
        print("")
    
    seguir = input("Seguir Calculando? (Sí/No): ")
    print("")

    if seguir.upper() == "NO" or seguir.upper() == "N":
        continuar = False
        print("Fin del cálculo")
        print("")
