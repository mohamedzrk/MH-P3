import random


#mover un examen a otra franja horaria
def mover_examen(solucion, n_slots, aulas_validas):
    vecino = solucion.copy()
    examenes = list(vecino.keys()) 
    
    exam = random.choice(examenes)
    nuevo_slot = random.randint(0, n_slots - 1)
    aula_actual = vecino[exam][1] 
    
    vecino[exam] = (nuevo_slot, aula_actual)
    
    # guardamos el movimiento para la lista tabu
    movimiento = (exam, solucion[exam][0], nuevo_slot) 
    return vecino, movimiento


#intercambiar las franjas de dos examenes
def intercambiar_examenes(solucion):
    vecino = solucion.copy()
    examenes = list(vecino.keys())
    
    exam1, exam2 = random.sample(examenes, 2) 
    slot1, aula1 = vecino[exam1] 
    slot2, aula2 = vecino[exam2] 
    
    # intercambiamos slots, las aulas se quedan igual
    vecino[exam1] = (slot2, aula1)
    vecino[exam2] = (slot1, aula2)
    
    movimiento = (exam1, exam2, slot1, slot2)
    return vecino, movimiento


# elige un operador al azar
def generar_vecino(solucion, n_slots, aulas_validas):
    if random.random() < 0.5:
        return mover_examen(solucion, n_slots, aulas_validas)
    else:
        return intercambiar_examenes(solucion)
