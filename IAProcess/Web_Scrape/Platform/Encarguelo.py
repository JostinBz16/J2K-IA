import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_price(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            # Precio del producto
            precio_tag = soup.find("p", {"class": "text-3xl mt-2 leading-none font-bold text-primary"})
            
            # Vendedor del producto
            vendedor_tag = soup.find("p", {"class": "text-muted"})
            vendedor = vendedor_tag.text.replace("Producto por ", "") if vendedor_tag else None
            
            # Cantidad de calificaciones
            cantidad_calificaciones_tag = soup.find("span", {"class": "block text-primary"})
            cantidad_calificaciones = cantidad_calificaciones_tag.text.strip().replace(" personas viendo en este momento", "") if cantidad_calificaciones_tag else None
            
            return url, precio_tag.text.strip() if precio_tag else None, vendedor, cantidad_calificaciones
    except:
        print(f"Error al obtener precio del producto: {url}")
        return url, None, None, None

def encarguelo_scraping(nombre_producto):
    base_url = "https://encarguelo.com/productos"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US, en;q=0.5",
    }

    search_query = nombre_producto.replace(" ", "+")
    page = 1
    products_array = []
    urls_to_process = []
    url_to_product = {}

    while True:
        url = f"{base_url}?search={search_query}&page={page}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error al obtener la página {page}. Status Code: {response.status_code}")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        product_listings = soup.find_all("a", {"class":"block rounded-md border border-gray-100 px-4 py-3 bg-white"})
        
        if not product_listings:
            break

        for product in product_listings:
            data = {}
            
            # Nombre del producto
            nombre_tag = product.find("h3", {"class":"mt-1 text-base h-10 leading-tight text-gray-700 text-left line-clamp-2"})
            data["nombre"] = nombre_tag.text.strip() if nombre_tag else None
            
            # Nombre del producto
            descripcion_tag = product.find("h3", {"class":"mt-1 text-base h-10 leading-tight text-gray-700 text-left line-clamp-2"})
            data["descripcion"] = descripcion_tag.text.strip() if descripcion_tag else None
            
            # Calificacion del producto
            calificacion_tag = product.find("p", {"class":"sr-only"})
            if calificacion_tag and calificacion_tag.text:
                calificacion = calificacion_tag.text.strip()
                # Eliminar "de 5 estrellas" del texto
                calificacion = calificacion.replace(" de 5 estrellas", "")
                data["calificacion"] = calificacion
            else:
                data["calificacion"] = None
            
            # Link del producto
            data["link"] = product.get("href")

            # Imagen del producto
            imagen_tag = product.find("img", {"class":"object-contain bg-white"})
            data["imagen"] = imagen_tag["src"] if imagen_tag and "src" in imagen_tag.attrs else None

            # Agregar el campo vendedor al diccionario de datos
            data["vendedor"] = None
            
            # Agregar a las listas de procesamiento
            if data["link"]:
                urls_to_process.append(data["link"])
                url_to_product[data["link"]] = data
            
            products_array.append(data)

        # Procesar los precios en paralelo cada 20 productos o al final de la página
        if len(urls_to_process) >= 20 or not product_listings:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(fetch_price, url, headers) for url in urls_to_process]
                
                for future in as_completed(futures):
                    url, price, vendedor, cantidad_calificaciones = future.result()
                    if url in url_to_product:
                        url_to_product[url]["precio"] = price
                        url_to_product[url]["vendedor"] = vendedor
                        url_to_product[url]["cantidad_calificaciones"] = cantidad_calificaciones
            urls_to_process = []
            url_to_product = {}

        print(f"Procesada la página {page}")
        page += 1

    # # Exportar resultados
    # with open("encarguelo.json", "w", encoding="utf-8") as f:
    #     json.dump(products_array, f, indent=4, ensure_ascii=False)

    df = pd.DataFrame(products_array)
    return df

if __name__ == "__main__":
    nombre_producto = input("Ingrese el nombre del producto que desea buscar: ")
    productos = encarguelo_scraping(nombre_producto)
    print(productos)
