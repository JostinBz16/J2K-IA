import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


# Función para hacer scraping de los listados de productos en Mercado Libre
def mercado_libre(nombre_producto):
    articulo = nombre_producto
    r = requests.get(
        "https://listado.mercadolibre.com.co/{}#D[A:{}]".format(
            articulo.replace(" ", "-"), articulo.replace(" ", "-")
        )
    )
    contenido = r.content

    soup = BeautifulSoup(contenido, "html.parser")

    # Última página
    try:
        pagination = soup.find("ul", {"class": "andes-pagination"}).find_all("li")
        last_page_modified = int(
            pagination[-2].text
        )  # Obtenemos la penúltima entrada que contiene el número de la última página
    except:
        last_page_modified = 1  # En caso de error, asumir que solo hay una página

    # Array para añadir los objetos
    products_array = []

    for page in range(0, last_page_modified):
        result = requests.get(
            "https://listado.mercadolibre.com.co/{}_Desde_{}_NoIndex_True".format(
                articulo.replace(" ", "-"), (page * 50) + 1
            )
        )
        content_pagination = result.content
        soup_pagination = BeautifulSoup(content_pagination, "html.parser")

        # Asegúrate de usar el selector correcto para los productos
        alldivs = soup_pagination.find_all(
            "div", {"class": "ui-search-result__wrapper"}
        )  # Cambiar selector por el actual

        product_urls = []  # Lista para almacenar los enlaces de productos
        for item in alldivs:
            data = {}
            data["nombre_articulo"] = item.find(
                "h2", {"class": "poly-box poly-component__title"}
            ).text
            data["precio"] = item.find("span", {"class": "andes-money-amount"}).text

            # Extraer el precio anterior
            precio_antes_tag = item.find(
                "span", {"class": "andes-money-amount__fraction"}
            )
            if precio_antes_tag:
                data["precio_antes"] = (
                    precio_antes_tag.text.strip()
                )  # Extrae y limpia el texto del precio anterior
            else:
                data["precio_antes"] = None  # Si no se encuentra, asigna None

            data["link"] = item.find("a", {"class": ""})["href"]
            product_urls.append(
                data["link"]
            )  # Agregar el enlace del producto a la lista

            # Encuentra el span que contiene la calificación
            rating_tag = item.find("span", {"class": "poly-reviews__rating"})
            if rating_tag:
                data["calificacion"] = rating_tag.text.strip()
            else:
                data["calificacion"] = None  # Si no se encuentra el elemento

            # Navegar al enlace del producto para extraer la imagen
            product_url = data["link"]
            try:
                response = requests.get(product_url)
                if response.status_code == 200:
                    product_soup = BeautifulSoup(response.content, "html.parser")

                    # Extraer la imagen del producto
                    imagen_tag = product_soup.find(
                        "img", {"class": "ui-pdp-image ui-pdp-gallery__figure__image"}
                    )
                    if imagen_tag and "src" in imagen_tag.attrs:
                        data["imagen"] = imagen_tag[
                            "src"
                        ]  # Extraer la URL de la imagen
                    else:
                        data["imagen"] = (
                            None  # Si no se encuentra la imagen, asigna None
                        )

                    # Extraer todos los comentarios
                    comentarios = []
                    comentario_tags = product_soup.find_all(
                        "p",
                        {"class": "ui-review-capability-comments__comment__content"},
                    )

                    if comentario_tags:
                        for comentario in comentario_tags:
                            comentarios.append(comentario.text.strip())

                    # Almacenar comentarios si existen, de lo contrario asignar None
                    data["comentarios"] = comentarios if comentarios else None

                else:
                    data["imagen"] = None
                    data["comentarios"] = None
            except Exception as e:
                print(f"Error al hacer la solicitud de la imagen y comentarios: {e}")
                data["imagen"] = None
                data["comentarios"] = None

            products_array.append(data)
            print(products_array)
            return products_array
            # print(data)

    # Convertir a DataFrame y mostrar
    df = pd.DataFrame(products_array)
    print(df)

    archivo_json = "productos.json"
    with open(archivo_json, "w", encoding="utf-8") as file:
        json.dump(products_array, file, indent=4, ensure_ascii=False)
