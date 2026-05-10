import matplotlib.pyplot as plt
import numpy as np

instancias = ["Pequeña", "Mediana", "Grande"]

# Resultados de la ejecucion
coste_ini = [17814005, 15914425, 16617036]
coste_pm = [3812412, 6813153, 11014655]
coste_dm = [13513285, 14913985, 15316786]

tiempo_pm = [11.7, 34.97, 96.18]
tiempo_dm = [11.05, 22.9, 47.06]

x = np.arange(len(instancias)) 
ancho = 0.25

# Grafica 1: Comparacion de Costes
plt.figure()
plt.bar(x - ancho, coste_ini, ancho, label='Solucion Inicial', color='gray') #x-ancho, x, x+ancho para que las barras se pongan juntas
plt.bar(x, coste_pm, ancho, label='Primer Mejor', color='blue')
plt.bar(x + ancho, coste_dm, ancho, label='Del Mejor', color='orange')

plt.title('Comparacion de Costes')
plt.ylabel('Penalizacion')
plt.xticks(x, instancias)
plt.legend()
plt.savefig('grafica_costes.png')
print("Grafica de costes creada.")

# Grafica 2: Comparacion de Tiempos
plt.figure()
plt.bar(x - ancho/2, tiempo_pm, ancho, label='Primer Mejor', color='blue')
plt.bar(x + ancho/2, tiempo_dm, ancho, label='Del Mejor', color='orange')

plt.title('Comparacion de Tiempos')
plt.ylabel('Segundos')
plt.xticks(x, instancias)
plt.legend()
plt.savefig('grafica_tiempos.png')
print("Grafica de tiempos creada.")
