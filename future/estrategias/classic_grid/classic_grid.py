'''
Peograma que opera diferententes exchange utilizando el grid de futuro clasico 
'''

# Importar paquetes y librerias
import json
import time
import shutil
import future
import inverse
import inverse_ws
import future_ws

# Abrir el archivo parametros_iniciales.json y cargar su contenido
parametros = json.load(open("future/estrategias/classic_grid/parametros_iniciales.json", "r"))

# Crear una copia temporal del archivo json con los parametros
fecha_inicio = int(time.time())*1000
if parametros['inverso']:
    parametros_copia = f"future/estrategias/classic_grid/parametros/{parametros['activo'].upper()}_{parametros['exchange'].upper()}_INVERSO_{fecha_inicio}.json"
else:
    parametros_copia = f"future/estrategias/classic_grid/parametros/{parametros['activo'].upper()}_{parametros['exchange'].upper()}_LINEAL_{fecha_inicio}.json"
shutil.copy("future/estrategias/classic_grid/parametros_iniciales.json", parametros_copia)


# PARAMETROS INCIALES
# -------------------
exchange = parametros['exchange']
tipo = parametros['direccion']
symbol = parametros['activo']
inverso = parametros['inverso']
apalancamiento = parametros['apalancamiento']
precio_minimo = parametros['precio_minimo']
precio_maximo = parametros['precio_maximo']
numero_regillas = parametros['numero_regillas']
inversion = parametros['inversion']
precio_activación = parametros['precio_activación']
activacion_instantanea = parametros['activacion_instantanea']
ganacia_esperada = parametros['ganacia_esperada']
max_perdia = parametros['max_perdia']
porcentage_ganancia = parametros['porcentage_ganancia']
porcentage_perdida = parametros['porcentage_perdida']
precio_tp = parametros['precio_tp']
precio_sl = parametros['precio_sl']
pausa = parametros['pausa']
# -------------------

# Variables iniciales
# -------------------
if inverso:
    balance_inicial = inverse.patrimonio(exchange, symbol)
    precio_actual = inverse.precio_actual_activo(exchange, symbol)
else:
    balance_inicial = future.patrimonio(exchange, symbol)
    precio_actual = future.precio_actual_activo(exchange, symbol)
riesgoAlcanzado = False
grilla = []
volumenPorNivel = (inversion / (numero_regillas - 1)) / precio_actual
ordenesCompras = 0
ordenesVentas = 0
# -------------------

# Generar el grid
# ---------------
paso = (precio_minimo - precio_maximo) / (numero_regillas - 1)
i = 0
for grid in grilla:
    grilla[i] = precio_minimo + i * paso
    i = i + 1
# ---------------

# Colocar la primera orden
# ------------------------
print(f"COLANDO {numero_regillas} ORDENES")
# ------------------------