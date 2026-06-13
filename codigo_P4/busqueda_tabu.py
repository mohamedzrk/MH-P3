import random
import time
from codigo_P1.practica1 import evaluar_solucion
from codigo_P4.operadores_movimiento import mover_examen


def busqueda_tabu(sol_inicial, capacidades, estudiantes_por_examen, student_exams_dict,
                  n_slots, aulas_validas, tenencia_tabu=15, n_candidatos=30,
                  max_iter_sin_mejora=500, max_iteraciones=5000, limite_tiempo=60):
    
    s_actual = sol_inicial.copy()
    coste_actual = evaluar_solucion(s_actual, capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
    
    mejor_sol = s_actual.copy()
    mejor_coste = coste_actual
    
    # lista tabu: cuando se llena quitamos el mas antiguo
    lista_tabu = []
    
    historial = [coste_actual]
    tiempos_historial = [0.0]
    iter_sin_mejora = 0
    tiempo_inicio = time.time()
    
    for iteracion in range(max_iteraciones):
        
        # generamos candidatos y cogemos el mejor que no sea tabu
        mejor_vecino = None
        mejor_coste_vecino = None
        mejor_movimiento = None
        
        for _ in range(n_candidatos):
            vecino, movimiento = mover_examen(s_actual, n_slots, aulas_validas)
            coste_vecino = evaluar_solucion(vecino, capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
            
            # miramos si esta prohibido
            mov_inverso = (movimiento[0], movimiento[2], movimiento[1])
            es_tabu = (mov_inverso in lista_tabu or movimiento in lista_tabu)
            
            # criterio de aspiracion: si es mejor que el mejor global, lo aceptamos igual
            if es_tabu and coste_vecino < mejor_coste:
                es_tabu = False
            
            if not es_tabu and (mejor_coste_vecino is None or coste_vecino < mejor_coste_vecino):
                mejor_vecino = vecino
                mejor_coste_vecino = coste_vecino
                mejor_movimiento = movimiento
        
        if mejor_vecino is None:
            break
        
        # aceptamos el mejor vecino aunque empeore
        s_actual = mejor_vecino
        coste_actual = mejor_coste_vecino
        lista_tabu.append(mejor_movimiento)
        if len(lista_tabu) > tenencia_tabu:
            lista_tabu.pop(0) # quitamos el movimiento mas antiguo
        
        # actualizamos mejor global
        if coste_actual < mejor_coste:
            mejor_sol = s_actual.copy()
            mejor_coste = coste_actual
            iter_sin_mejora = 0
        else:
            iter_sin_mejora += 1
        
        historial.append(mejor_coste)
        tiempos_historial.append(time.time() - tiempo_inicio)
        
        if iter_sin_mejora >= max_iter_sin_mejora:
            break
            
        if time.time() - tiempo_inicio >= limite_tiempo:
            break
    
    return mejor_sol, mejor_coste, historial, iteracion + 1, tiempos_historial
