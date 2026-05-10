import time
import matplotlib.pyplot as plt
import numpy as np

from codigo_P1.generador_instancias import generar_instancia
from codigo_P1.practica1 import preprocesar_datos, evaluar_solucion, generar_solucion_inicial, busqueda_primer_mejor, busqueda_del_mejor
from codigo_AG.algoritmo_genetico import algoritmo_genetico
from codigo_AM.algoritmo_memetico import algoritmo_memetico

def run_experiment():
    print("Practica 3: Algoritmos Memeticos")
    
    instancias = [
        ("Pequeña", 50, 500, 10, 25),
        ("Mediana", 100, 1000, 10, 50),
        ("Grande", 200, 2000, 10, 100)
    ]
    
    # variables para guardar los resultados
    nombres_inst = []
    costes_ini_list = []
    costes_pm_list = []
    costes_dm_list = []
    costes_ag_list = []
    costes_am_list = []
    


    print("\nComparativa de instancias")

    # bucle para recorrer las instancias
    for nombre, n_exams, n_students, n_rooms, n_slots in instancias:

        #  en cada instancia generamos los datos, preprocesamos y aplicamos los algoritmos
        print(f"\n{nombre}: tiene {n_exams} examenes, {n_students} alumnos, {n_rooms} aulas y {n_slots} slots")
        student_exam, rooms, exams_df = generar_instancia(n_exams, n_students, n_rooms, n_slots, seed=42)
        capacidades, estudiantes_por_examen, student_exams_dict, aulas_validas = preprocesar_datos(student_exam, rooms, exams_df)
        
        inicio = time.time()
        sol_ini = generar_solucion_inicial(exams_df, aulas_validas, n_slots)
        coste_ini = evaluar_solucion(sol_ini, capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
        t_ini = time.time() - inicio
        
        inicio = time.time()
        # 5000 evaluaciones
        _, coste_pm, _ = busqueda_primer_mejor(sol_ini, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, max_evals=5000)
        t_pm = time.time() - inicio
        
        inicio = time.time()
        # 5000 evaluaciones
        _, coste_dm, _ = busqueda_del_mejor(sol_ini, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, max_evals=5000)
        t_dm = time.time() - inicio
        
        inicio = time.time()
        # 5000 evaluaciones
        _, coste_ag, historial_ag = algoritmo_genetico(capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, exams_df, tam_poblacion=50, max_generaciones=100, prob_cruce=0.8, prob_mutacion=0.05)
        t_ag = time.time() - inicio
        
        inicio = time.time()
        # 4850 evaluaciones
        _, coste_am, historial_am = algoritmo_memetico(capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, exams_df, tam_poblacion=10, max_generaciones=18, prob_cruce=0.8, prob_mutacion=0.05, evals_bl=25, prob_bl=1.0, lamarkiano=True, limite_tiempo=60)
        t_am = time.time() - inicio
        
        print(f"Constructiva: Coste {coste_ini} | Tiempo: {t_ini:.2f}s")
        print(f"Primer Mejor: Coste {coste_pm} | Tiempo: {t_pm:.2f}s")
        print(f"Del Mejor: Coste {coste_dm} | Tiempo: {t_dm:.2f}s")
        print(f"Genetico: Coste {coste_ag} | Tiempo: {t_ag:.2f}s")
        print(f"Memetico: Coste {coste_am} | Tiempo: {t_am:.2f}s")
        
        nombres_inst.append(nombre) # guardamos los nombres de las instancias
        costes_ini_list.append(coste_ini)
        costes_pm_list.append(coste_pm)
        costes_dm_list.append(coste_dm)
        costes_ag_list.append(coste_ag)
        costes_am_list.append(coste_am)
        
        # Guardar evolucion AG vs AM de la Mediana
        if nombre == "Mediana":
            plt.figure()
            plt.plot(historial_ag, marker='.', linestyle='-', color='b', label='Genetico')
            plt.plot(historial_am, marker='.', linestyle='-', color='r', label='Memetico')
            plt.title('Evolucion AG vs AM (Instancia Mediana)')
            plt.xlabel('Generacion')
            plt.ylabel('Coste')
            plt.legend()
            plt.grid(True)
            plt.savefig('resultados/grafica_evolucion_ag_vs_am.png')
            
    # Grafica de barras agrupadas con todos los algoritmos
    x = np.arange(len(nombres_inst))
    ancho = 0.15
    
    plt.figure()
    plt.bar(x - ancho*2, costes_ini_list, ancho, label='Constructiva', color='gray')
    plt.bar(x - ancho, costes_pm_list, ancho, label='Primer Mejor', color='blue')
    plt.bar(x, costes_dm_list, ancho, label='Del Mejor', color='orange')
    plt.bar(x + ancho, costes_ag_list, ancho, label='Genetico', color='green')
    plt.bar(x + ancho*2, costes_am_list, ancho, label='Memetico', color='red')
    
    plt.title('Comparativa de Costes Finales')
    plt.ylabel('Coste')
    plt.xticks(x, nombres_inst)
    plt.legend()
    plt.savefig('resultados/grafica_comparativa_costes_P3.png')
    

    print("\nPruebas de parametros AM (Sobre instancia Pequena)")
    n_exams, n_students, n_rooms, n_slots = 50, 500, 10, 25
    student_exam, rooms, exams_df = generar_instancia(n_exams, n_students, n_rooms, n_slots, seed=42)
    capacidades, estudiantes_por_examen, student_exams_dict, aulas_validas = preprocesar_datos(student_exam, rooms, exams_df)
    
    # Efecto de las evaluaciones de busqueda local
    print("Evaluaciones de busqueda local")
    evals_vals = [10, 30, 50, 100]
    costes_evals = []
    
    for ev in evals_vals:
        print(f"Probando evals_bl = {ev}")
        _, c_am, _ = algoritmo_memetico(capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, exams_df,
                                        tam_poblacion=20, max_generaciones=20, prob_cruce=0.8, prob_mutacion=0.05,
                                        evals_bl=ev, prob_bl=1.0, lamarkiano=True)
        costes_evals.append(c_am)
        
    plt.figure()
    plt.plot(evals_vals, costes_evals, marker='o', color='r')
    plt.title('Efecto de las Evaluaciones de BL en el Coste')
    plt.xlabel('Evaluaciones BL')
    plt.xticks(evals_vals)
    plt.ylabel('Coste Final')
    plt.savefig('resultados/grafica_param_evals_bl.png')
    
    # Efecto de la probabilidad de aplicar busqueda local
    print("Probabilidad de busqueda local")
    pbl_vals = [0.1, 0.25, 0.5, 1.0]
    costes_pbl = []
    for pbl in pbl_vals:
        print(f"Probando prob_bl = {pbl}")
        _, c_am, _ = algoritmo_memetico(capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, exams_df, tam_poblacion=20, max_generaciones=20, prob_cruce=0.8, prob_mutacion=0.05, evals_bl=25, prob_bl=pbl, lamarkiano=True)
        costes_pbl.append(c_am)
        
    plt.figure()
    plt.plot(pbl_vals, costes_pbl, marker='s', color='purple')
    plt.title('Efecto de la Probabilidad de aplicar BL')
    plt.xlabel('Probabilidad BL')
    plt.xticks(pbl_vals)
    plt.ylabel('Coste Final')
    plt.savefig('resultados/grafica_param_prob_bl.png')
    
    # Comparativa Lamarkiano vs Baldwiniano
    print("Lamarkiano vs Baldwiniano")
    _, coste_lamark, hist_lamark = algoritmo_memetico(capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, exams_df, tam_poblacion=20, max_generaciones=30, prob_cruce=0.8, prob_mutacion=0.05, evals_bl=25, prob_bl=1.0, lamarkiano=True)
    _, coste_baldw, hist_baldw = algoritmo_memetico(capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, exams_df, tam_poblacion=20, max_generaciones=30, prob_cruce=0.8, prob_mutacion=0.05, evals_bl=25, prob_bl=1.0, lamarkiano=False)
    print(f"Lamarkiano: Coste {coste_lamark}")
    print(f"Baldwiniano: Coste {coste_baldw}")
    
    plt.figure()
    plt.plot(hist_lamark, marker='.', linestyle='-', color='r', label='Lamarkiano')
    plt.plot(hist_baldw, marker='.', linestyle='-', color='blue', label='Baldwiniano')
    plt.title('Lamarkiano vs Baldwiniano')
    plt.xlabel('Generacion')
    plt.ylabel('Coste')
    plt.legend()
    plt.grid(True)
    plt.savefig('resultados/grafica_lamark_vs_baldw.png')
    
    print("Ha finalizado correctamente")

if __name__ == "__main__":
    run_experiment()
