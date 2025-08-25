posicion = 250*3                    # Valor de cada posicion
porcentaje_retroceso = 0.18     # Tamaño porcental de cada grid
numero_grid = 150               # Numero de regillas

perdida_por_grid = posicion*porcentaje_retroceso/100
serie_perdidas = numero_grid*(numero_grid+1)/2 # Serie aritmetica
perdidas = perdida_por_grid*serie_perdidas
print(f"\nTotal perdidas: ${round(perdidas, 2)} USD")
print(f"Retroceso maximo: {round(numero_grid*porcentaje_retroceso, 2)}%")