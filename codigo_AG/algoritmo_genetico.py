import random
import time
from codigo_P1.practica1 import evaluar_solucion, generar_solucion_inicial #importamos las funciones de la practica anterior
from codigo_AG.operadores import seleccion_torneo, cruce, mutacion #importamos los operadores del AG

# creamos la poblacion inicial
def crear_poblacion_inicial(tam_poblacion, exams_df, aulas_validas, n_slots):
    # utilizamos  de la practica anterior
    poblacion = []
    for _ in range(tam_poblacion):
        sol = generar_solucion_inicial(exams_df, aulas_validas, n_slots) #generamos una solucion inicial aleatoria
        poblacion.append(sol) #añadimos la solucion a la poblacion
    return poblacion



def algoritmo_genetico(capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, exams_df,
                       tam_poblacion=50, max_generaciones=100, prob_cruce=0.8, prob_mutacion=0.05, elitismo=True, limite_tiempo=60):
    
    poblacion = crear_poblacion_inicial(tam_poblacion, exams_df, aulas_validas, n_slots) # creamos 50 soluciones aleatorias como poblacion inicial

    fitness_pob = [] # lista para guardar el fitness de cada individuo
    for ind in poblacion:
        coste_ind = evaluar_solucion(ind, capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
        fitness_pob.append(coste_ind) # calculamos el fitness de cada individuo
    
    # guardamos la mejor solucion de esta generacion
    mejor_idx = 0
    mejor_fitness = fitness_pob[0]
    for i in range(1, len(fitness_pob)):
        if fitness_pob[i] < mejor_fitness:
            mejor_fitness = fitness_pob[i]
            mejor_idx = i
            
    mejor_ind = poblacion[mejor_idx].copy() # guardamos la mejor solucion
    
    historial_fitness = [mejor_fitness] # guardamos el fitness de la mejor solucion
    
    
    generaciones_sin_mejora = 0 # inicializamos el contador de generaciones sin mejora
    LIMITE_ESTANCAMIENTO = 30 # limite de generaciones sin mejora
    tiempo_inicio = time.time() 
    
    for gen in range(max_generaciones): # bucle principal del algoritmo genetico
        nueva_poblacion = [] 
        
        # Elitismo: guardamos la mejor solución tal cual en la siguiente generación
        if elitismo:
            nueva_poblacion.append(mejor_ind.copy())
            
        # mientras no se llegue a 50, hecemos un torneo, cruce y mutacion
        while len(nueva_poblacion) < tam_poblacion:
            p1 = seleccion_torneo(poblacion, fitness_pob)
            p2 = seleccion_torneo(poblacion, fitness_pob)
            
            if random.random() < prob_cruce: # si el numero aleatorio es menor que la probabilidad de cruce
                h1, h2 = cruce(p1, p2)
            else:
                h1, h2 = p1.copy(), p2.copy()
                
            h1 = mutacion(h1, n_slots, aulas_validas, prob_mutacion)
            h2 = mutacion(h2, n_slots, aulas_validas, prob_mutacion)
            
            nueva_poblacion.append(h1)
            if len(nueva_poblacion) < tam_poblacion:
                nueva_poblacion.append(h2)
                
        poblacion = nueva_poblacion

        # calculamos el fitness de cada individuo de la nueva poblacion
        fitness_pob = []
        for ind in poblacion: # recorre todos los individuos de la poblacion
            coste_ind = evaluar_solucion(ind, capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
            fitness_pob.append(coste_ind) # guardamos el fitness de cada individuo
        
        # guardamos la mejor solucion de esta generacion
        actual_mejor_idx = 0
        actual_mejor_fitness = fitness_pob[0]
        for i in range(1, len(fitness_pob)): # recorre todos los individuos de la poblacion
            if fitness_pob[i] < actual_mejor_fitness: # si el fitness del individuo actual es menor que el mejor fitness actualizamos el mejor fitness y el indice
                actual_mejor_fitness = fitness_pob[i]
                actual_mejor_idx = i 
        

        if actual_mejor_fitness < mejor_fitness: # si el mejor fitness de la generacion actual es menor que el mejor fitness global
            mejor_fitness = actual_mejor_fitness
            mejor_ind = poblacion[actual_mejor_idx].copy() # actualizamos el mejor fitness
            generaciones_sin_mejora = 0 # reiniciamos el contador
        else:
            generaciones_sin_mejora += 1
            
        historial_fitness.append(mejor_fitness) # guardamos el fitness de la mejor solucion
        
        if generaciones_sin_mejora >= LIMITE_ESTANCAMIENTO:
            break # si se llega al limite de generaciones sin mejora, se rompe el bucle
        
        # parar si se pasa del tiempo maximo
        if time.time() - tiempo_inicio >= limite_tiempo:
            break
            
    return mejor_ind, mejor_fitness, historial_fitness # finalmente devolvemos la mejor solucion, su fitness y el historial de fitness

