import random


# seleccion por torneo: se eligen k individuos al azar y se selecciona el mejor
def seleccion_torneo(poblacion, fitness_pob, k=3):
    indices = random.sample(range(len(poblacion)), k) # seleccionamos k individuos al azar
    mejor_idx = indices[0] 
    mejor_fit = fitness_pob[mejor_idx]
    
    for i in range(1, len(indices)): 
        idx = indices[i]
        if fitness_pob[idx] < mejor_fit: # si el fitness del individuo actual es menor que el mejor
            mejor_fit = fitness_pob[idx] # actualizamos el mejor fitness
            mejor_idx = idx # actualizamos el mejor indice
            
    return poblacion[mejor_idx].copy() # devolvemos el mejor individuo



# cruce: se eligen dos padres y se crean hijos con una combinacion de los genes de los padres
def cruce(padre1, padre2):
    hijo1 = {}
    hijo2 = {}
    
    # recorre todos los examenes de los padres
    for exam in padre1.keys():
        if random.random() < 0.5: # para cada examen, se elige aleatoriamente si pertenece al hijo 1 o al hijo 2
            hijo1[exam] = padre1[exam]
            hijo2[exam] = padre2[exam]
        else:
            hijo1[exam] = padre2[exam]
            hijo2[exam] = padre1[exam]
            
    return hijo1, hijo2 # devolvemos los dos hijos, cada uno con una combinacion aleatoria de los genes de los padres


# mutacion: se elige un cromosoma, y hacemos cambios aleatorios en el
def mutacion(cromosoma, n_slots, aulas_validas, prob_mutacion=0.05):
    mutado = cromosoma.copy() 
    
    for exam in mutado.keys(): # recorre todos los examenes del cromosoma
        if random.random() < prob_mutacion: # si el numero aleatorio es menor que la probabilidad de mutacion
            nuevo_slot = random.randint(0, n_slots - 1) # elegimos un nuevo slot aleatorio
            nueva_aula = random.choice(aulas_validas[exam]) # elegimos una nueva aula aleatoria
            mutado[exam] = (nuevo_slot, nueva_aula) # actualizamos el cromosoma
            
    return mutado
