import random
import math
import time
from codigo_P1.practica1 import evaluar_solucion
from codigo_P4.operadores_movimiento import generar_vecino


def enfriamiento_simulado(sol_inicial, capacidades, estudiantes_por_examen, student_exams_dict,
                          n_slots, aulas_validas, temp_inicial=1000, temp_minima=1,
                          alpha=0.95, iters_por_temp=100, limite_tiempo=60):
    
    s_actual = sol_inicial.copy()
    coste_actual = evaluar_solucion(s_actual, capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
    
    mejor_sol = s_actual.copy()
    mejor_coste = coste_actual
    historial = [coste_actual]
    tiempos_historial = [0.0]
    
    temperatura = temp_inicial
    tiempo_inicio = time.time()
    iteraciones = 0
    
    # bucle principal
    while temperatura > temp_minima:
        
        for _ in range(iters_por_temp):
            # generamos un vecino
            vecino, _ = generar_vecino(s_actual, n_slots, aulas_validas)
            coste_vecino = evaluar_solucion(vecino, capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
            
            delta = coste_vecino - coste_actual
            
            # regla de Metropolis del tema   
            if delta <= 0:
                s_actual = vecino
                coste_actual = coste_vecino
            else:
                probabilidad = math.exp(-delta / temperatura)
                if random.random() < probabilidad:
                    s_actual = vecino
                    coste_actual = coste_vecino
            
            # actualizamos el mejor global
            if coste_actual < mejor_coste:
                mejor_sol = s_actual.copy()
                mejor_coste = coste_actual
            
            iteraciones += 1
        
        
        historial.append(mejor_coste)
        tiempos_historial.append(time.time() - tiempo_inicio)
        
        # enfriamiento geometrico
        temperatura = temperatura * alpha
        
        if time.time() - tiempo_inicio >= limite_tiempo:
            break
    
    return mejor_sol, mejor_coste, historial, iteraciones, tiempos_historial
