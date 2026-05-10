import numpy as np
import pandas as pd
import random

def generar_instancia(n_exams=100, n_students=2000, n_rooms=10, n_slots=40, seed=42):
    random.seed(seed) 
    np.random.seed(seed) 
    
    student_exam = []
    for s in range(n_students):
        k = random.randint(3, 6) # cada alumno tiene entre 3 y 6 examenes
        exams = np.random.choice(n_exams, size=k, replace=False) # elige k examenes al azar sin repetir
        for e in exams:
            student_exam.append([s, e]) # crea una lista de tuplas (alumno, examen)
            
    student_exam = pd.DataFrame(student_exam, columns=["student", "exam"])
    exam_students = student_exam.groupby("exam").size() # cuenta cuantos alumnos tiene cada examen
    
    capacities = np.random.randint(30, 200, size=n_rooms) # asigna una capacidad aleatoria a cada sala
    rooms = pd.DataFrame({
        "room": range(n_rooms),
        "capacity": capacities
    })
    
    exams_df = pd.DataFrame({
        "exam": exam_students.index,
        "n_students": exam_students.values
    })
    
    return student_exam, rooms, exams_df
