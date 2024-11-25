import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
import json
import re

# Tipo de cambio (Ejemplo: 1 USD = 4503 COP)
TIPO_CAMBIO = 4503  # Cambia este valor según el tipo de cambio actual


def convertir_a_pesos(precio_usd):
    """Convierte el precio de USD a pesos usando el tipo de cambio y formatea el resultado."""
    if precio_usd:
        try:
            # El precio viene como un string que puede contener "$" y comas
            precio_usd = precio_usd.replace("$", "").replace(",", "")
            # Convertir a pesos
            precio_en_pesos = float(precio_usd) * TIPO_CAMBIO
            # Formatear el precio con puntos y agregar el signo de peso
            return f"${precio_en_pesos:,.0f}"
        except ValueError:
            return None
    return None


def buscar_productos_amazon(query):
    # URL de búsqueda de Amazon con la estructura solicitada
    url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"

    # Lista de User-Agents para rotar entre ellos y simular un navegador distinto en cada intento
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1",
    ]

    # Lista para almacenar los datos de los productos
    productos_array = []

    # Variable de control para la paginación
    pagina = 1
    while True:
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept-Language": "en-US, en;q=0.5",
        }

        # Construir URL para cada página
        url_pagina = f"{url}&page={pagina}"

        # Realizar la solicitud HTTP a Amazon
        response = requests.get(url_pagina, headers=headers)

        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Encontrar los productos en la página actual
            productos = soup.find_all("div", {"data-component-type": "s-search-result"})

            # Extraer datos de cada producto
            for item in productos:
                data = {}

                # Precio en dólares
                precio = item.find("span", {"class": "a-offscreen"})
                if precio:
                    precio_usd = precio.text.strip()
                    # Convertir precio de USD a pesos y formatearlo
                    data["precio"] = convertir_a_pesos(precio_usd)
                else:
                    data["precio"] = None

                categoria_tag = soup.find("div", {"id": "departments"})

                if categoria_tag:
                    # Buscar el primer <li> que contiene la categoría dentro de <ul>
                    categoria_item = categoria_tag.find("li")
                    if categoria_item:
                        # Buscar el <span> dentro del <a> que contiene la categoría
                        span_categoria = categoria_item.find("a").find("span")
                        if span_categoria:
                            data["categoria"] = (
                                span_categoria.text.strip()
                            )  # Guardar el texto del span
                        else:
                            data["categoria"] = None
                    else:
                        data["categoria"] = None
                else:
                    data["categoria"] = None

                # Enlace del producto (link)
                enlace_relativo = item.find("a", {"class": "a-link-normal"})["href"]
                data["link"] = f"https://www.amazon.com{enlace_relativo}"

                # Calificación del producto
                calificacion = item.find("span", {"class": "a-size-base"})
                if calificacion:
                    data["calificacion"] = calificacion.text.strip()
                else:
                    data["calificacion"] = None

                # Extraer la cantidad de votos del producto
                cantidad_votos = item.find("span", {"class": "a-size-base"})
                if cantidad_votos:
                    data["cantidad_calificacion"] = cantidad_votos.text.strip()
                else:
                    data["cantidad_calificacion"] = None

                # Navegar al enlace del producto para extraer más detalles
                product_url = data["link"]
                try:
                    response_product = requests.get(product_url)
                    if response_product.status_code == 200:
                        product_soup = BeautifulSoup(
                            response_product.content, "html.parser"
                        )
                        time.sleep(0.5)

                        # Nombre del producto
                        nombre_articulo_tag = product_soup.find(
                            "h1", {"id": "title"}
                        ).find("span")
                        data["nombre"] = (
                            nombre_articulo_tag.text.strip()
                            if nombre_articulo_tag
                            else None
                        )

                        # Extraer la imagen del producto
                        imagen_tag = product_soup.find(
                            "img", {"class": "a-dynamic-image"}
                        )
                        if imagen_tag and "src" in imagen_tag.attrs:
                            data["imagen"] = imagen_tag["src"]
                        else:
                            data["imagen"] = None

                        # Extraer vendedor
                        vendedor_tag = product_soup.find("a", {"id": "bylineInfo"})
                        if vendedor_tag:
                            vendedor_nombre = vendedor_tag.text.strip()
                            # Eliminar "Visit the" si está presente en el nombre del vendedor
                            vendedor_nombre = re.sub(
                                r"^Visit the\s*", "", vendedor_nombre
                            )
                            data["vendedor"] = vendedor_nombre
                        else:
                            data["vendedor"] = None

                        # Extraer descripción del producto
                        descripcion_tag = product_soup.find(
                            "table", {"class": "a-normal a-spacing-micro"}
                        )
                        if descripcion_tag:
                            data["descripcion"] = descripcion_tag.text.strip()
                        else:
                            data["descripcion"] = None

                        # Extraer categoría
                        # Buscar el primer <li> dentro del <ul> y luego el <span> dentro del <a>
                        # Extraer categoría específica desde el div correcto
                        # Extraer categoría general desde el div de departamentos

                        # Extraer disponibilidad
                        disponibilidad_tag = product_soup.find(
                            "span", {"class": "a-size-medium"}
                        )
                        if disponibilidad_tag:
                            data["disponible"] = disponibilidad_tag.text.strip()
                        else:
                            data["disponible"] = None

                        # Extraer stock disponible
                        stock_tag = product_soup.find(
                            "span", {"class": "a-size-medium"}
                        )
                        if stock_tag:
                            data["disponible"] = True
                            data["stock"] = 1
                        else:
                            data["disponible"] = False
                            data["stock"] = 0

                    else:
                        # Si no se puede acceder a la página del producto
                        data["imagen"] = None
                        data["vendedor"] = None
                        data["descripcion"] = None
                        data["categoria"] = None
                        data["stock"] = None

                except Exception as e:
                    print(f"Error al acceder al producto: {product_url} - {e}")
                    data["imagen"] = None
                    data["vendedor"] = None
                    data["descripcion"] = None
                    data["categoria"] = None
                    data["stock"] = None

                # Agregar el producto a la lista
                productos_array.append(data)

            # Verificar si hay más páginas
            siguiente_pagina = soup.find(
                "a",
                {
                    "class": "s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"
                },
            )
            if siguiente_pagina:
                pagina += 1
                time.sleep(random.uniform(1, 3))  # Espera entre páginas
            else:

                break

        elif response.status_code == 503:
            # Pausa creciente en caso de error 503
            espera = 2**pagina
            print(f"503 Error. Reintentando en {espera} segundos...")
            time.sleep(espera)

        else:
            print(f"Error al realizar la solicitud: {response.status_code}")
            break

    # Convertir la lista de productos en un DataFrame de pandas
    df = pd.DataFrame(productos_array)

    # # Guardar los datos en un archivo JSON llamado amazon.json
    # with open("amazon.json", "w", encoding="utf-8") as f:
    #     json.dump(productos_array, f, indent=4, ensure_ascii=False)

    # Mostrar el DataFrame con columnas truncadas, excepto la de "link"
    print("Amazon")
    # print(df)

    return productos_array if productos_array else []


# Solicitar al usuario el nombre del producto a buscar
# producto_buscar = input("Ingrese el nombre del producto a buscar en Amazon: ")
# df_amazon = buscar_productos_amazon(producto_buscar)
