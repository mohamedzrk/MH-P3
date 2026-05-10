import random
import time
from codigo_P1.practica1 import evaluar_solucion #reutilizamos evaluacion y vecindario de la P1
from codigo_AG.algoritmo_genetico import crear_poblacion_inicial #reutilizamos la funcion del AG
from codigo_AG.operadores import seleccion_torneo, cruce, mutacion #importamos los operadores del AG



# implementamos una busqueda local basada en primer mejor de la P1 pero explorando el vecindario de forma aleatoria
def busqueda_local_memetica(solucion, capacidades, estudiantes_por_examen, student_exams_dict,
                                                        n_slots, aulas_validas, max_evals=50):
    s_actual = solucion.copy()
    coste_actual = evaluar_solucion(s_actual, capacidades, estudiantes_por_examen, 
                                                student_exams_dict, n_slots)
    
    examenes = list(s_actual.keys())
    
    for _ in range(max_evals):
        # Vecino cambiando la franja horaria del examen
        exam = random.choice(examenes) # elegimos un examen aleatorio
        nuevo_slot = random.randint(0, n_slots - 1) # elegimos una franja horaria aleatoria
        aula_actual = s_actual[exam][1] # cogemos el aula asignada
        
        if s_actual[exam][0] == nuevo_slot:
            continue
            
        vecino = s_actual.copy()
        vecino[exam] = (nuevo_slot, aula_actual)
        
        coste_vecino = evaluar_solucion(vecino, capacidades, estudiantes_por_examen, student_exams_dict, 
                                                                                            n_slots)
        
        # Si es mejor, lo aceptamos (Primer Mejor) y seguimos buscando desde ahi
        if coste_vecino < coste_actual:
            s_actual = vecino
            coste_actual = coste_vecino
            
    return s_actual, coste_actual, max_evals



def algoritmo_memetico(capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, exams_df,
                       tam_poblacion=50, max_generaciones=100, prob_cruce=0.8, prob_mutacion=0.05,
                       elitismo=True, limite_tiempo=60, evals_bl=50, prob_bl=1.0, lamarkiano=True):
    
    poblacion = crear_poblacion_inicial(tam_poblacion, exams_df, aulas_validas, n_slots)
    
    # aplicamos busqueda local a la poblacion inicial para que empiece con mejores soluciones
    fitness_pob = []
    for i in range(len(poblacion)):
        if random.random() < prob_bl:
            sol_mejorada, coste_mejorado, _ = busqueda_local_memetica(poblacion[i], capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, max_evals=evals_bl)
            if lamarkiano:
                poblacion[i] = sol_mejorada # lamarkiano: reemplazamos el individuo
            fitness_pob.append(coste_mejorado)
        else:
            coste_ind = evaluar_solucion(poblacion[i], capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
            fitness_pob.append(coste_ind)
    
    # buscamos el mejor de la poblacion
    mejor_idx = 0
    mejor_fitness = fitness_pob[0]
    for i in range(1, len(fitness_pob)):
        if fitness_pob[i] < mejor_fitness:
            mejor_fitness = fitness_pob[i]
            mejor_idx = i
            
    mejor_ind = poblacion[mejor_idx].copy()
    historial_fitness = [mejor_fitness]
    
    generaciones_sin_mejora = 0
    LIMITE_ESTANCAMIENTO = 30
    tiempo_inicio = time.time()
    

    #  para cada generacion
    for gen in range(max_generaciones):
        nueva_poblacion = []
        nuevos_fitness = []
        
        # si hay elitismo, el mejor de la poblacion pasa directo a la nueva generacion
        if elitismo:
            nueva_poblacion.append(mejor_ind.copy())
            nuevos_fitness.append(mejor_fitness)
            
        # generamos nuevos individuos hasta completar la poblacion
        while len(nueva_poblacion) < tam_poblacion:
            p1 = seleccion_torneo(poblacion, fitness_pob)
            p2 = seleccion_torneo(poblacion, fitness_pob)
            
            if random.random() < prob_cruce:
                h1, h2 = cruce(p1, p2)
            else:
                h1, h2 = p1.copy(), p2.copy()
                
            h1 = mutacion(h1, n_slots, aulas_validas, prob_mutacion)
            h2 = mutacion(h2, n_slots, aulas_validas, prob_mutacion)
            
            # parte memetica: aplicamos busqueda local a los hijos
            if random.random() < prob_bl:
                sol_m1, coste_m1, _ = busqueda_local_memetica(h1, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, max_evals=evals_bl)
                if lamarkiano:
                    h1 = sol_m1 # lamarkiano: nos quedamos con la version mejorada
                f1 = coste_m1
            else:
                f1 = evaluar_solucion(h1, capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
                    
            if random.random() < prob_bl:
                sol_m2, coste_m2, _ = busqueda_local_memetica(h2, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, max_evals=evals_bl)
                if lamarkiano:
                    h2 = sol_m2
                f2 = coste_m2
            else:
                f2 = evaluar_solucion(h2, capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
            
            nueva_poblacion.append(h1)
            nuevos_fitness.append(f1)
            if len(nueva_poblacion) < tam_poblacion:
                nueva_poblacion.append(h2)
                nuevos_fitness.append(f2)
                
        poblacion = nueva_poblacion
        fitness_pob = nuevos_fitness # usamos el fitness ya calculado 
        
        # buscamos el mejor de esta generacion
        actual_mejor_idx = 0
        actual_mejor_fitness = fitness_pob[0]
        for i in range(1, len(fitness_pob)):
            if fitness_pob[i] < actual_mejor_fitness:
                actual_mejor_fitness = fitness_pob[i]
                actual_mejor_idx = i
        
        if actual_mejor_fitness < mejor_fitness:
            mejor_fitness = actual_mejor_fitness
            mejor_ind = poblacion[actual_mejor_idx].copy()
            generaciones_sin_mejora = 0
        else:
            generaciones_sin_mejora = generaciones_sin_mejora + 1
            
        historial_fitness.append(mejor_fitness)
        
        if generaciones_sin_mejora >= LIMITE_ESTANCAMIENTO:
            break
            
        if time.time() - tiempo_inicio >= limite_tiempo:
            break
            
    return mejor_ind, mejor_fitness, historial_fitness
