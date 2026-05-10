import numpy as np
import pandas as pd
import random
import time
from collections import Counter
try:
    from codigo_P1.generador_instancias import generar_instancia
except ImportError:
    from generador_instancias import generar_instancia

# Pesos de la función objetivo
W1 = 10 # si dos examenes de un mismo alumno son consecutivos
W2 = 20 # si dos examenes de un mismo alumno son en el mismo dia
W3 = 1  # si hay franjas con muchos examenes y otras con pocos
PENALIZACION_DURA = 100000

SLOTS_POR_DIA = 4 # numero de franjas horarias por dia

def preprocesar_datos(student_exam, rooms, exams_df):
    
    
    capacidades = {}
    for index, row in rooms.iterrows():
        capacidades[row['room']] = row['capacity']

    estudiantes_por_examen = {}
    for index, row in exams_df.iterrows():
        estudiantes_por_examen[row['exam']] = row['n_students']
    
    # Guardamos los examenes a los que asiste cada estudiante
    student_exams_dict = student_exam.groupby('student')['exam'].apply(list).to_dict()
    
    # Aulas válidas para cada examen (las que son mas grandes que el numero de alumnos)
    aulas_validas = {}
    
    # Buscamos cual es el aula mas grande de todas por si acaso hace falta
    aula_mas_grande = 0
    capacidad_maxima = 0
    for room, cap in capacidades.items():
        if cap > capacidad_maxima:
            capacidad_maxima = cap
            aula_mas_grande = room
    
    for exam, n_stud in estudiantes_por_examen.items():
        validas = []
        for r, cap in capacidades.items():
            if cap >= n_stud:
                validas.append(r)
                
        if len(validas) == 0:
            # Si no cabe en ninguna, le asignamos la más grande por defecto 
            validas.append(aula_mas_grande)
            
        aulas_validas[exam] = validas
            
    return capacidades, estudiantes_por_examen, student_exams_dict, aulas_validas


def evaluar_solucion(solucion, capacidades, estudiantes_por_examen, student_exams_dict, n_slots):
    coste = 0
    
    # Creamos un diccionario para saber cuantos examenes hay en cada slot
    sol_por_slot = {}
    for s in range(n_slots):
        sol_por_slot[s] = []
    
    # Capacidad de aula
    for exam in solucion:
        slot = solucion[exam][0]
        room = solucion[exam][1]
        
        sol_por_slot[slot].append(exam)
        
        # Penalizacion si hay mas alumnos que sillas
        if estudiantes_por_examen[exam] > capacidades[room]:
            coste = coste + PENALIZACION_DURA
            
    #  Restricciones por estudiante y blandas
    for student in student_exams_dict:
        exams = student_exams_dict[student]
        
        slots_student = []
        for e in exams:
            if e in solucion:
                slots_student.append(solucion[e][0])
                
        slots_student.sort()
        
        # Comprobar si hay examenes superpuestos a la misma hora
        num_slots = len(slots_student)
        num_unicos = len(set(slots_student))
        if num_unicos < num_slots:
            coste = coste + (PENALIZACION_DURA * (num_slots - num_unicos))
            
        # Comprobar si hay exámenes consecutivos
        for i in range(num_slots - 1):
            if slots_student[i+1] == slots_student[i] + 1: 
                coste = coste + W1
                
        # Comprobar si hay exámenes en el mismo día
        dias = []
        for s in slots_student:
            dia_del_examen = int(s / SLOTS_POR_DIA)
            dias.append(dia_del_examen)
            
        conteo_dias = Counter(dias)
        for dia, count in conteo_dias.items():
            if count > 1:
                coste = coste + (W2 * (count - 1))
                
    #Distribución restamos el slot que mas examenes tiene con el que menos
    uso_slots = []
    for s in range(n_slots):
        uso_slots.append(len(sol_por_slot[s]))
        
    if n_slots > 0:
        max_uso = max(uso_slots)
        min_uso = min(uso_slots)
        coste = coste + (W3 * (max_uso - min_uso))
    
    return coste


def generar_solucion_inicial(exams_df, aulas_validas, n_slots):
    solucion = {}
    for index, row in exams_df.iterrows():
        exam = row['exam']
        posibles_aulas = aulas_validas[exam]
        
        # cogemos un aula y una hora al azar
        room = random.choice(posibles_aulas)
        slot = random.randint(0, n_slots - 1)
        
        solucion[exam] = (slot, room)
        
    return solucion


def generar_vecinos_por_cambio(solucion, n_slots, aulas_validas):
    vecinos = []
    
    # Obtenemos la lista de todos los exámenes para poder iterar
    examenes = list(solucion.keys())
    
    for i in range(len(examenes)):
        exam1 = examenes[i]
        slot1 = solucion[exam1][0]
        room1 = solucion[exam1][1]
        
        # 1. Vecino cambiando la franja horaria del examen
        for slot in range(n_slots):
            if slot != slot1:
                vecino = solucion.copy()
                vecino[exam1] = (slot, room1)
                vecinos.append(vecino)
                
        # 2. Vecinos intercambiando franjas entre dos exámenes
        for j in range(i + 1, len(examenes)):
            exam2 = examenes[j]
            slot2 = solucion[exam2][0]
            room2 = solucion[exam2][1]
            
            # Solo tiene sentido intercambiar si están en distintas horas
            if slot1 != slot2:
                vecino = solucion.copy()
                # Intercambiamos sus slots, pero mantienen sus aulas originales
                vecino[exam1] = (slot2, room1)
                vecino[exam2] = (slot1, room2)
                vecinos.append(vecino)
                
    return vecinos


def busqueda_primer_mejor(sol_inicial, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, max_evals):
    s_actual = sol_inicial.copy()
    coste_actual = evaluar_solucion(s_actual, capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
    
    mejora = True
    evals = 0
    
    while mejora == True and evals < max_evals:
        mejora = False
        vecindario = generar_vecinos_por_cambio(s_actual, n_slots, aulas_validas)
        
        for vecino in vecindario:
            coste_vecino = evaluar_solucion(vecino, capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
            evals = evals + 1
            
            # Si encontramos uno mejor paramos el bucle y nos lo quedamos
            if coste_vecino < coste_actual:
                s_actual = vecino
                coste_actual = coste_vecino
                mejora = True
                break 
                
    return s_actual, coste_actual, evals


def busqueda_del_mejor(sol_inicial, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, max_evals):
    s_actual = sol_inicial.copy()
    coste_actual = evaluar_solucion(s_actual, capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
    
    mejora = True
    evals = 0
    
    while mejora == True and evals < max_evals:
        mejora = False
        mejor_vecino = s_actual
        mejor_coste_vecino = coste_actual
        
        vecindario = generar_vecinos_por_cambio(s_actual, n_slots, aulas_validas)
        
        for vecino in vecindario:
            coste_vecino = evaluar_solucion(vecino, capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
            evals = evals + 1
            
            # Comprobamos si es el mejor de todos los que hemos visto
            if coste_vecino < mejor_coste_vecino:
                mejor_coste_vecino = coste_vecino
                mejor_vecino = vecino
                mejora = True
                
            if evals >= max_evals:
                break
                
        # Aplicamos el mejor cambio despues de mirar todos
        if mejora == True:
            s_actual = mejor_vecino
            coste_actual = mejor_coste_vecino
            
    return s_actual, coste_actual, evals

def ejecutar_experimento(nombre_instancia, n_exams, n_students, n_rooms, n_slots):
    print("\n" + nombre_instancia)
    print("Generando instancia: Exámenes=" + str(n_exams) + ", Estudiantes=" + str(n_students))
    
    tiempo_inicio = time.time()
    
    # Generamos los datos de la instancia
    student_exam, rooms, exams_df = generar_instancia(n_exams, n_students, n_rooms, n_slots, seed=42)
    
    # Preparamos los diccionarios
    capacidades, estudiantes_por_examen, student_exams_dict, aulas_validas = preprocesar_datos(student_exam, rooms, exams_df)
    
    # Creamos la solución inicial aleatoria
    solucion_inicial = generar_solucion_inicial(exams_df, aulas_validas, n_slots)
    coste_inicial = evaluar_solucion(solucion_inicial, capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
    
    tiempo_fin = time.time()
    tiempo_generacion = round(tiempo_fin - tiempo_inicio, 2)
    
    print("   Solución inicial - Coste: " + str(coste_inicial) + " (Tiempo: " + str(tiempo_generacion) + "s)")
    
    # Evaluar Primer Mejor
    tiempo_inicio_pm = time.time()
    solucion_pm, coste_pm, evaluaciones_pm = busqueda_primer_mejor(solucion_inicial, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, max_evals=5000)
    tiempo_fin_pm = time.time()
    tiempo_pm = round(tiempo_fin_pm - tiempo_inicio_pm, 2)
    print("   [Primer Mejor] Coste: " + str(coste_pm) + " | Evals: " + str(evaluaciones_pm) + " | Mejoría: " + str(coste_inicial - coste_pm) + " | Tiempo: " + str(tiempo_pm) + "s")
    
    # Evaluar Del Mejor
    tiempo_inicio_dm = time.time()
    solucion_dm, coste_dm, evaluaciones_dm = busqueda_del_mejor(solucion_inicial, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, max_evals=5000)
    
    tiempo_fin_dm = time.time()
    tiempo_dm = round(tiempo_fin_dm - tiempo_inicio_dm, 2)
    print("   [Del Mejor]    Coste: " + str(coste_dm) + " | Evals: " + str(evaluaciones_dm) + " | Mejoría: " + str(coste_inicial - coste_dm) + " | Tiempo: " + str(tiempo_dm) + "s")


if __name__ == "__main__":
    print("Planificación de Exámenes")
    
    ejecutar_experimento("Instancia Pequeña", 50, 500, 10, 25)
    ejecutar_experimento("Instancia Mediana", 100, 1000, 10, 50)
    ejecutar_experimento("Instancia Grande", 200, 2000, 10, 100)
    
    print("\nEjecución finalizada.")
