posicion = 794               # Valor de la posicion
porcentaje_retroceso = 1.8  # Retroceso en porcentaje
numero_grid = 14           # Numero de regillas

perdida_por_grid = posicion*porcentaje_retroceso/100
serie_perdidas = numero_grid*(numero_grid+1)/2 # Serie aritmetica
perdidas = perdida_por_grid*serie_perdidas
print(perdidas)