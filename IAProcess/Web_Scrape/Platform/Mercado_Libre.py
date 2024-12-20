import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json
import random


# Función para hacer scraping de los listados de productos en Mercado Libre


def mercado_libre(nombre_producto):
    articulo = nombre_producto
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1",
    ]

    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US, en;q=0.5",
    }
    r = requests.get(
        "https://listado.mercadolibre.com.co/{}#D[A:{}]".format(
            articulo.replace(" ", "-"), articulo.replace(" ", "-")
        ),
        headers=headers,
    )

    contenido = r.content
    if r.status_code != 200:
        print(
            f"Error al obtener la página para {articulo}. Status Code: {r.status_code}"
        )
        return []  # Retornar vacío si la solicitud falla
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
            data["nombre"] = item.find(
                "h2", {"class": "poly-box poly-component__title"}
            ).text
            data["precio"] = item.find("span", {"class": "andes-money-amount"}).text

            # # Extraer el precio anterior
            # precio_antes_tag = item.find(
            #     "span", {"class": "andes-money-amount__fraction"}
            # )
            # if precio_antes_tag:
            #     data["precio_antes"] = (
            #         precio_antes_tag.text.strip()
            #     )  # Extrae y limpia el texto del precio anterior
            # else:
            #     data["precio_antes"] = None  # Si no se encuentra, asigna None

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

            # Extraer la cantidad de votos
            votos_tag = item.find("span", {"class": "poly-reviews__total"})
            if votos_tag:
                data["cantidad_calificacion"] = (
                    votos_tag.text.strip().replace("(", "").replace(")", "")
                )
            else:
                data["cantidad_calificacion"] = None

            # Navegar al enlace del producto para extraer la imagen, comentarios, vendedor, cantidad vendida, descripción, categoría y stock disponible
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

                    # Extraer el nombre del vendedor
                    vendedor_tag = product_soup.find(
                        "div", {"class": "ui-pdp-seller__header__title"}
                    )
                    if vendedor_tag:
                        vendedor_nombre = (
                            vendedor_tag.text.strip().replace("Vendido por", "").strip()
                        )

                        # Añadir un espacio después de "Tienda Oficial"
                        if "Tienda Oficial" in vendedor_nombre:
                            vendedor_nombre = vendedor_nombre.replace(
                                "Tienda Oficial", "Tienda Oficial "
                            )

                        data["vendedor"] = vendedor_nombre
                    else:
                        data["vendedor"] = (
                            None  # Si no se encuentra el vendedor, asigna None
                        )

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
                            data["vendidos"] = int(
                                match.group(1)
                            )  # Extraer el número de productos vendidos
                        else:
                            data["vendidos"] = (
                                None  # Si no se encuentra un número, asignar None
                            )
                    else:
                        data["vendidos"] = (
                            None  # Si no se encuentra la cantidad de vendidos, asignar None
                        )

                    # Extraer la descripción del producto
                    descripcion_tag = product_soup.find(
                        "p", {"class": "ui-pdp-description__content"}
                    )
                    if descripcion_tag:
                        data["descripcion"] = (
                            descripcion_tag.text.strip()
                        )  # Extraer la descripción
                    else:
                        data["descripcion"] = (
                            None  # Si no se encuentra la descripción, asignar None
                        )

                    # Extraer si el vendedor es confiable (etiqueta platino o Tienda Oficial)
                    confiable_tag = product_soup.find(
                        "div", {"class": "ui-seller-data-status__lider-seller"}
                    )
                    tienda_oficial_tag = product_soup.find(
                        "span", {"class": "ui-pdp-seller__label-sold"}
                    )  # Buscar si es "Tienda Oficial"

                    if confiable_tag:
                        data["confiable"] = (
                            True  # El vendedor tiene la etiqueta "platino"
                        )
                    elif (
                        tienda_oficial_tag
                        and "Tienda Oficial" in tienda_oficial_tag.text
                    ):
                        data["confiable"] = True  # El vendedor es una "Tienda Oficial"
                    else:
                        data["confiable"] = (
                            False  # Si no es ni "platino" ni "Tienda Oficial"
                        )

                    # Extraer disponibilidad
                    stock_tag = product_soup.find(
                        "span", {"class": "ui-pdp-buybox__quantity__available"}
                    )
                    disponible_tag = product_soup.find(
                        "div", {"class": "ui-pdp-stock-information"}
                    )

                    if disponible_tag is None:
                        # Verificar si es el último disponible
                        ultimo_tag = product_soup.find(
                            "div", {"class": "ui-pdp-buybox__quantity"}
                        )
                        if (
                            ultimo_tag
                            and "¡Última disponible!" in ultimo_tag.text.strip()
                        ):  # Validar el texto dentro de la etiqueta
                            data["disponible"] = True
                            data["stock"] = 1
                        else:
                            data["disponible"] = False
                            data["stock"] = 0
                    else:
                        # Extraer texto de disponibilidad y verificar si hay stock disponible
                        disponible_text = disponible_tag.get_text(strip=True)
                        if (
                            "Stock disponible" in disponible_text
                        ):  # Validar el texto dentro de la etiqueta
                            data["disponible"] = True
                            if stock_tag:
                                stock_texto = stock_tag.text.strip()
                                # Buscar un número en el texto de stock disponible (ej. "Quedan 3 disponibles")
                                match = re.search(r"(\d+)", stock_texto)
                                if match:
                                    data["stock"] = int(
                                        match.group(1)
                                    )  # Extraer la cantidad de stock disponible
                            else:
                                data["stock"] = (
                                    0  # Si no se encuentra información de stock
                                )
                        else:
                            data["disponible"] = False
                            data["stock"] = 0

                else:
                    data["imagen"] = None
                    data["vendedor"] = None
                    data["vendidos"] = None
                    data["descripcion"] = None
                    data["confiable"] = None
                    data["stock"] = None
                    data["disponible"] = None

            except Exception as e:
                print(f"Error al acceder a {product_url}: {e}")
                print(
                    f"Error al hacer la solicitud de la imagen, comentarios, vendedor y cantidad vendida: {e}"
                )
                data["imagen"] = None
                data["vendedor"] = None
                data["vendidos"] = None
                data["descripcion"] = None
                data["confiable"] = None
                data["stock"] = None
                data["disponible"] = None

            products_array.append(data)

    # Mueve el retorno aquí para que devuelva todos los productos
    df = pd.DataFrame(products_array)
    print("Mercado Libre")
    # with open("libre.json", "w", encoding="utf-8") as f:
    #     json.dump(products_array, f, indent=4, ensure_ascii=False)
    return products_array if products_array else []
