posicion = 4                    # Valor de cada posicion
porcentaje_retroceso = 0.05     # Tamaño porcental de cada grid
numero_grid = 440               # Numero de regillas

perdida_por_grid = posicion*porcentaje_retroceso/100
serie_perdidas = numero_grid*(numero_grid+1)/2 # Serie aritmetica
perdidas = perdida_por_grid*serie_perdidas
print("")
print(f"Total perdidas: ${round(perdidas, 2)} USD")
print("")