import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


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
                

            # Navegar al enlace del producto para extraer la imagen, comentarios, vendedor, cantidad vendida y descripción
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
                        data["imagen"] = imagen_tag["src"]  # Extraer la URL de la imagen
                    else:
                        data["imagen"] = None  # Si no se encuentra la imagen, asigna None

                    # Extraer todos los comentarios
                    comentarios = []
                    comentario_tags = product_soup.find_all(
                        "p",
                        {"class": "ui-review-capability__summary__plain_text__summary_container"},
                    )
                    if comentario_tags:
                        for comentario in comentario_tags:
                            comentarios.append(comentario.text.strip())
                    data["comentarios"] = comentarios if comentarios else None

                    # Extraer el nombre del vendedor
                    vendedor_tag = product_soup.find(
                        "div", {"class": "ui-pdp-seller__header__title"}
                    )
                    if vendedor_tag:
                        data["vendedor"] = vendedor_tag.text.strip().replace("Vendido por", "").strip()  # Extraer el nombre del vendedor
                    else:
                        data["vendedor"] = None  # Si no se encuentra el vendedor, asigna None

                    # Extraer la cantidad de productos vendidos
                    vendidos_tag = product_soup.find(
                        "span",
                        {
                            "class": "ui-pdp-color--BLACK ui-pdp-size--XSMALL ui-pdp-family--BOLD"
                        },
                    )
                    if vendidos_tag:
                        vendidos_texto = vendidos_tag.text.strip()
                        # Buscar un número en el texto de cantidad vendida (ej. "500 vendidos")
                        match = re.search(r"(\d+)", vendidos_texto)
                        if match:
                            data["vendidos"] = int(match.group(1))  # Extraer el número de productos vendidos
                        else:
                            data["vendidos"] = None  # Si no se encuentra un número, asignar None
                    else:
                        data["vendidos"] = None  # Si no se encuentra la cantidad de vendidos, asignar None

                    # Extraer la descripción del producto
                    descripcion_tag = product_soup.find(
                        "p", {"class": "ui-pdp-description__content"}
                    )
                    if descripcion_tag:
                        data["descripcion"] = descripcion_tag.text.strip()  # Extraer la descripción
                    else:
                        data["descripcion"] = None  # Si no se encuentra la descripción, asignar None
                        
                    # Extraer si el vendedor es confiable (etiqueta platino)
                    confiable_tag = product_soup.find("div", {"class": "ui-seller-data-status__lider-seller"})
                    if confiable_tag:
                        data["confiable"] = True  # El vendedor tiene la etiqueta "platino"
                    else:
                        data["confiable"] = False  # El vendedor no tiene la etiqueta "platino"

                else:
                    data["imagen"] = None
                    data["comentarios"] = None
                    data["vendedor"] = None
                    data["vendidos"] = None
                    data["descripcion"] = None
                    data["confiable"] = None

            except Exception as e:
                print(f"Error al acceder a {product_url}: {e}")
                data["imagen"] = None
                data["comentarios"] = None
                data["vendedor"] = None
                data["vendidos"] = None
                data["descripcion"] = None
                data["confiable"] = None

            except Exception as e:
                print(
                    f"Error al hacer la solicitud de la imagen, comentarios, vendedor y cantidad vendida: {e}"
                )
                data["imagen"] = None
                data["comentarios"] = None
                data["vendedor"] = None
                data["vendidos"] = None
                data["descripcion"] = None
                data["confiable"] = None

            products_array.append(data)

    # Mueve el retorno aquí para que devuelva todos los productos
    df = pd.DataFrame(products_array)
    print(df)
    return products_array if products_array else []
