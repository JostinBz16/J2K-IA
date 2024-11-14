import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import traceback


# Función para hacer scraping de los listados de productos en Alkosto
def alkosto(nombre_producto):
    try:
        base_url = f"https://www.alkosto.com/search?text={nombre_producto}"
        r = requests.get(base_url)
        contenido = r.content
        soup = BeautifulSoup(contenido, "html.parser")

        products_array = []

        # Obtener el número de páginas
        try:
            pagination = soup.find_all("button", {"class": "ais-InfiniteHits-loadMore"})
            last_page_modified = len(pagination)  # Número de páginas
        except:
            last_page_modified = 1  # En caso de error, solo una página

        # Recorrer todas las páginas de resultados
        for page_num in range(1, last_page_modified + 1):
            # Actualizar URL de la página
            page_url = f"https://www.alkosto.com/search?text={nombre_producto}&page={page_num}&sort=relevance"
            result = requests.get(page_url)
            content_pagination = result.content
            soup = BeautifulSoup(content_pagination, "html.parser")

            # Extraer todos los bloques de producto
            alldivs = soup.find_all("div", {"class": "product__item__information"})

            for div in alldivs:
                data = {}

                # Extraer el nombre del producto
                name_tag = div.find("h3", {"class": "product__item__top__title"})
                data["nombre"] = name_tag.text.strip() if name_tag else None

                # Extraer URL del producto
                url_tag = div.find("a", {"class": "product__item__information__image"})
                if url_tag and "href" in url_tag.attrs:
                    data["link"] = url_tag["href"]

                # Extraer el precio del producto
                price_tag = div.find("span", {"class": "price"})
                if price_tag:
                    raw_price = price_tag.text.strip()
                    data["precio"] = raw_price.replace("$", "")

                # Extraer el precio anterior del producto
                old_price_tag = div.find(
                    "p", {"class": "product__price--discounts__old"}
                )
                if old_price_tag:
                    data["precio_antes"] = old_price_tag.text.strip().replace("$", "")
                else:
                    data["precio_antes"] = None

                # Extraer la URL de la imagen del producto
                img_tag = div.find(
                    "img", {"class": "product__item__information__image"}
                )
                data["imagen"] = (
                    img_tag["src"] if img_tag and "src" in img_tag.attrs else None
                )

                # Extraer comentarios
                comentarios_tag = div.find_all("div", {"class": "yotpo-read-more-text"})
                comentarios = [
                    comentario.text.strip() for comentario in comentarios_tag
                ]
                data["comentarios"] = comentarios if comentarios else None

                products_array.append(data)

        return products_array if products_array else []
    except Exception as e:
        print(f"Error: {e}")


# Solicitar al usuario el nombre del producto a buscar
nombre_producto = input("¿Qué producto quieres buscar?: ")
productos = alkosto(nombre_producto)

# Mostrar los resultados obtenidos
if productos:
    for producto in productos:
        nombre = producto.get("nombre", "N/A")
        precio = producto.get("precio", "N/A")
        precio_antes = producto.get("precio_antes", "N/A")
        imagen = producto.get("imagen", "N/A")
        url = producto.get("link", "N/A")
        comentarios = producto.get("comentarios", "N/A")
        print(
            f"Nombre: {nombre}, Precio: {precio}, Precio Anterior: {precio_antes}, Imagen: {imagen}, Link: {url}, Comentarios: {comentarios}"
        )
else:
    print("No se encontraron productos.")
