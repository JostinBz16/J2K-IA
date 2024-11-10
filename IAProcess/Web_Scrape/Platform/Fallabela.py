import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import traceback


# Función para hacer scraping de los listados de productos en Falabella
def falabella(nombre_producto):
    try:
        base_url = "https://www.falabella.com.co/falabella-co/search?Ntt={}".format(
            nombre_producto.replace(" ", "+")
        )
        r = requests.get(base_url)

        contenido = r.content

        soup = BeautifulSoup(contenido, "html.parser")

        # Array para añadir los objetos
        products_array = []
        page = 1
        try:
            pagination = soup.find("ol", {"class": "jsx-1389196899"}).find_all("li")
            last_page_modified = int(
                pagination[-2].text
            )  # Obtenemos la penúltima entrada que contiene el número de la última página
            print(pagination)
        except:
            last_page_modified = 1  # En caso de error, asumir que solo hay una página
        products_array = []

        for page in range(0, last_page_modified):
            result = requests.get(
                "https://www.falabella.com.co/falabella-co/search?Ntt={}&page={}".format(
                    nombre_producto.replace(" ", "+"), (page * 50) + 1
                )
            )

            content_pagination = result.content
            soup = BeautifulSoup(content_pagination, "html.parser")
            # Extraer cada producto del contenedor de resultados de búsqueda
            alldivs = soup.find_all("div", {"class": "search-results-item"})

            data = {}
            for div in alldivs:
                # Extraer el nombre del producto
                name_tag = div.find("b", {"class": "pod-subTitle"}).text
                data["nombre"] = name_tag.text.strip() if name_tag else None
                print(name_tag)
                # Extraer el precio del producto
                price_tag = div.find("li", {"data-event-price": True})
                data["precio"] = price_tag.text.strip() if price_tag else None

                # Extraer la imagen del producto
                img_tag = div.find("img", {"class": "jsx-2487856160"})
                data["imagen"] = (
                    img_tag["src"] if img_tag and "src" in img_tag else None
                )

                # Extraer el nombre del vendedor
                seller_tag = div.find("span", {"class": "pod-sellerText"})
                data["vendedor"] = seller_tag.text.strip() if seller_tag else None

                # Extraer los comentarios del producto
                comentarios = []
                comment_tags = div.find_all("p", {"class": "_review-text_16yc3_2"})
                for comment in comment_tags:
                    comentarios.append(comment.text.strip())
                data["comentarios"] = comentarios if comentarios else None
                print(data)
                products_array.append(data)

            page += 1  # Pasar a la siguiente página

        # Convertir a DataFrame  y retornar resultados
        df = pd.DataFrame(products_array)
        print(df)
        return products_array if products_array else []
    except Exception as e:
        traceback.print_exc()
        raise e
