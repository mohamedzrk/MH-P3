import random
import time
import matplotlib.pyplot as plt
import numpy as np

from codigo_P1.generador_instancias import generar_instancia
from codigo_P1.practica1 import preprocesar_datos, evaluar_solucion, generar_solucion_inicial, busqueda_primer_mejor, busqueda_del_mejor
from codigo_AG.algoritmo_genetico import algoritmo_genetico
from codigo_AM.algoritmo_memetico import algoritmo_memetico
from codigo_P4.enfriamiento_simulado import enfriamiento_simulado
from codigo_P4.busqueda_tabu import busqueda_tabu

def run_experiment():
    print("Practica 4: Enfriamiento Simulado y Busqueda Tabu")
    
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
    costes_es_list = []
    costes_bt_list = []


    print("\nComparativa de instancias")
    
    # bucle para recorrer las instancias
    for nombre, n_exams, n_students, n_rooms, n_slots in instancias:
        
        print(f"\n{nombre}: tiene {n_exams} examenes, {n_students} alumnos, {n_rooms} aulas y {n_slots} slots")
        student_exam, rooms, exams_df = generar_instancia(n_exams, n_students, n_rooms, n_slots, seed=42)
        random.seed() # Liberamos la semilla para que los algoritmos sí sean aleatorios
        capacidades, estudiantes_por_examen, student_exams_dict, aulas_validas = preprocesar_datos(student_exam, rooms, exams_df)
        
        sol_ini = generar_solucion_inicial(exams_df, aulas_validas, n_slots)
        coste_ini = evaluar_solucion(sol_ini, capacidades, estudiantes_por_examen, student_exams_dict, n_slots)
        
        inicio = time.time()
        _, coste_pm, _ = busqueda_primer_mejor(sol_ini, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, max_evals=999999, limite_tiempo=15)
        t_pm = time.time() - inicio

        
        inicio = time.time()
        _, coste_dm, _ = busqueda_del_mejor(sol_ini, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, max_evals=999999, limite_tiempo=15)
        t_dm = time.time() - inicio

        
        inicio = time.time()
        _, coste_ag, historial_ag = algoritmo_genetico(capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, exams_df, tam_poblacion=50, max_generaciones=9999, prob_cruce=0.8, prob_mutacion=0.05, limite_tiempo=15)
        t_ag = time.time() - inicio

        
        inicio = time.time()
        _, coste_am, historial_am = algoritmo_memetico(capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, exams_df, tam_poblacion=10, max_generaciones=9999, prob_cruce=0.8, prob_mutacion=0.05, evals_bl=25, prob_bl=1.0, lamarkiano=True, limite_tiempo=15)
        t_am = time.time() - inicio

        
        inicio = time.time()
        _, coste_es, historial_es, iters_es, tiempos_es = enfriamiento_simulado(sol_ini, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, temp_inicial=1000, temp_minima=1, alpha=0.95, iters_por_temp=100, limite_tiempo=15)
        t_es = time.time() - inicio

        
        inicio = time.time()
        _, coste_bt, historial_bt, iters_bt, tiempos_bt = busqueda_tabu(sol_ini, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, tenencia_tabu=15, n_candidatos=30, max_iter_sin_mejora=500, max_iteraciones=5000, limite_tiempo=15)
        t_bt = time.time() - inicio
        
        print(f"Constructiva: Coste {coste_ini}")
        print(f"Primer Mejor: Coste {coste_pm} , Tiempo: {t_pm:.2f}s")
        print(f"Del Mejor: Coste {coste_dm} , Tiempo: {t_dm:.2f}s")
        print(f"Genetico: Coste {coste_ag} , Tiempo: {t_ag:.2f}s")
        print(f"Memetico: Coste {coste_am} , Tiempo: {t_am:.2f}s")
        print(f"Enf. Simulado: Coste {coste_es} , Tiempo: {t_es:.2f}s , Iters: {iters_es}")
        print(f"Busqueda Tabu: Coste {coste_bt} , Tiempo: {t_bt:.2f}s , Iters: {iters_bt}")
        
        nombres_inst.append(nombre)
        costes_ini_list.append(coste_ini)
        costes_pm_list.append(coste_pm)
        costes_dm_list.append(coste_dm)
        costes_ag_list.append(coste_ag)
        costes_am_list.append(coste_am)
        costes_es_list.append(coste_es)
        costes_bt_list.append(coste_bt)

        
        # Guardar evolucion ES vs BT de la Mediana
        if nombre == "Mediana":
            plt.figure()
            plt.plot(tiempos_es, historial_es, marker='.', markersize=2, linestyle='-', color='green', label='Enf. Simulado')
            plt.plot(tiempos_bt, historial_bt, marker='.', markersize=2, linestyle='-', color='purple', label='Busqueda Tabu')
            plt.title('Evolucion ES vs BT (Instancia Mediana)')
            plt.xlabel('Tiempo (s)')
            plt.ylabel('Coste')
            plt.legend()
            plt.grid(True)
            plt.savefig('resultados/grafica_evolucion_es_vs_bt.png')
            
    # Grafica de barras agrupadas con todos los algoritmos
    x = np.arange(len(nombres_inst))
    ancho = 0.11
    
    plt.figure(figsize=(12, 6))
    plt.bar(x - ancho*3, costes_ini_list, ancho, label='Constructiva', color='gray')
    plt.bar(x - ancho*2, costes_pm_list, ancho, label='Primer Mejor', color='blue')
    plt.bar(x - ancho, costes_dm_list, ancho, label='Del Mejor', color='orange')
    plt.bar(x, costes_ag_list, ancho, label='Genetico', color='green')
    plt.bar(x + ancho, costes_am_list, ancho, label='Memetico', color='red')
    plt.bar(x + ancho*2, costes_es_list, ancho, label='Enf. Simulado', color='cyan')
    plt.bar(x + ancho*3, costes_bt_list, ancho, label='Busqueda Tabu', color='purple')
    
    plt.title('Comparativa de Costes Finales')
    plt.ylabel('Coste')
    plt.xticks(x, nombres_inst)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig('resultados/grafica_comparativa_costes_P4.png')
    

    

    # Pruebas de parametros (sobre instancia Pequeña)
    print("\nPruebas de parametros (Sobre instancia Pequena)")
    n_exams, n_students, n_rooms, n_slots = 50, 500, 10, 25
    student_exam, rooms, exams_df = generar_instancia(n_exams, n_students, n_rooms, n_slots, seed=42)
    random.seed() # Liberamos la semilla aqui tambien
    capacidades, estudiantes_por_examen, student_exams_dict, aulas_validas = preprocesar_datos(student_exam, rooms, exams_df)
    sol_ini = generar_solucion_inicial(exams_df, aulas_validas, n_slots)
    
    # Efecto de la temperatura inicial en ES
    print("Temperatura inicial")
    temps = [100, 500, 1000, 5000]
    costes_temp = []
    for t in temps:
        print(f"Probando temp_inicial = {t}")
        _, c_es, _, _, _ = enfriamiento_simulado(sol_ini, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, temp_inicial=t, alpha=0.95, iters_por_temp=100, limite_tiempo=15)
        costes_temp.append(c_es)
        
    plt.figure()
    plt.plot(temps, costes_temp, marker='o', color='green')
    plt.title('Efecto de la Temperatura Inicial (ES)')
    plt.xlabel('Temperatura Inicial')
    plt.ylabel('Coste Final')
    plt.grid(True)
    plt.savefig('resultados/grafica_param_temp_inicial.png')
    
    # Efecto del factor de enfriamiento alpha
    print("Factor de enfriamiento alpha")
    alphas = [0.8, 0.9, 0.95, 0.99]
    costes_alpha = []
    for a in alphas:
        print(f"Probando alpha = {a}")
        _, c_es, _, _, _ = enfriamiento_simulado(sol_ini, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, temp_inicial=1000, alpha=a, iters_por_temp=100, limite_tiempo=15)
        costes_alpha.append(c_es)
        
    plt.figure()
    plt.plot(alphas, costes_alpha, marker='s', color='darkgreen')
    plt.title('Efecto del Factor de Enfriamiento (ES)')
    plt.xlabel('Alpha')
    plt.ylabel('Coste Final')
    plt.grid(True)
    plt.savefig('resultados/grafica_param_alpha.png')
    
    # Efecto de las iteraciones por temperatura en ES
    print("Iteraciones por temperatura")
    iters_vals = [25, 50, 100, 200]
    costes_iters = []
    for iv in iters_vals:
        print(f"Probando iters_por_temp = {iv}")
        _, c_es, _, _, _ = enfriamiento_simulado(sol_ini, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, temp_inicial=1000, alpha=0.95, iters_por_temp=iv, limite_tiempo=15)
        costes_iters.append(c_es)
        
    plt.figure()
    plt.plot(iters_vals, costes_iters, marker='o', color='teal')
    plt.title('Efecto de Iteraciones por Temperatura (ES)')
    plt.xlabel('Iteraciones por Temperatura')
    plt.ylabel('Coste Final')
    plt.grid(True)
    plt.savefig('resultados/grafica_param_iters_temp.png')
    
    # Efecto de la tenencia tabu en BT
    print("Tenencia tabu")
    tenencias = [5, 10, 20, 50]
    costes_tenencia = []
    for ten in tenencias:
        print(f"Probando tenencia_tabu = {ten}")
        _, c_bt, _, _, _ = busqueda_tabu(sol_ini, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, tenencia_tabu=ten, n_candidatos=30, max_iter_sin_mejora=500, max_iteraciones=3000, limite_tiempo=15)
        costes_tenencia.append(c_bt)
        
    plt.figure()
    plt.plot(tenencias, costes_tenencia, marker='o', color='purple')
    plt.title('Efecto de la Tenencia Tabu (BT)')
    plt.xlabel('Tenencia Tabu')
    plt.ylabel('Coste Final')
    plt.grid(True)
    plt.savefig('resultados/grafica_param_tenencia.png')
    
    # Efecto del numero de candidatos en BT
    print("Numero de candidatos")
    n_cands = [10, 20, 30, 50]
    costes_cands = []
    for nc in n_cands:
        print(f"Probando n_candidatos = {nc}")
        _, c_bt, _, _, _ = busqueda_tabu(sol_ini, capacidades, estudiantes_por_examen, student_exams_dict, n_slots, aulas_validas, tenencia_tabu=15, n_candidatos=nc, max_iter_sin_mejora=500, max_iteraciones=3000, limite_tiempo=15)
        costes_cands.append(c_bt)
        
    plt.figure()
    plt.plot(n_cands, costes_cands, marker='s', color='darkviolet')
    plt.title('Efecto del Numero de Candidatos (BT)')
    plt.xlabel('Numero de Candidatos')
    plt.ylabel('Coste Final')
    plt.xticks(n_cands)
    plt.grid(True)
    plt.savefig('resultados/grafica_param_candidatos.png')
    
    print("\nHa finalizado correctamente")

if __name__ == "__main__":
    run_experiment()
