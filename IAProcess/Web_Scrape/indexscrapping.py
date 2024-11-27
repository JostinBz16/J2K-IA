import concurrent.futures
import threading
import json

# Otras plataformas que quieres agregar (a futuro)
from IAProcess.Web_Scrape.Platform.Encarguelo import encarguelo_scraping
from IAProcess.Web_Scrape.Platform.Mercado_Libre import mercado_libre


def scrapping(nombre_producto):

    # Obtener productos de Mercado Libre
    # productos_ml = mercado_libre(nombre_producto)

    # Combinar las listas de productos de ambas plataformas

    plataformas = [
        mercado_libre,
        encarguelo_scraping,
        # otra_plataforma,
    ]

    resultados = []
    event = threading.Event()  # Evento para asegurar que todas las tareas se completen

    # Ejecutar en paralelo usando ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tareas = [
            executor.submit(plataforma, nombre_producto) for plataforma in plataformas
        ]

        # Recoger resultados y esperar a que todos terminen
        def track_results():
            nonlocal resultados
            for future in concurrent.futures.as_completed(tareas):
                try:
                    resultados.extend(future.result())
                except Exception as e:
                    print(f"Error en una de las tareas de scraping: {e}")
            event.set()  # Señaliza que todos los hilos terminaron

        # Ejecutar la función para recopilar resultados en otro hilo
        executor.submit(track_results)

        # Esperar a que todas las tareas terminen
        event.wait()
        with open("allProducts.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=4, ensure_ascii=False)
    return resultados
