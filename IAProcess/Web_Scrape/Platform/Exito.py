import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


def exito_scraper(nombre_producto):
    base_url = f"https://www.exito.com/s?q={nombre_producto.replace(' ', '+')}&sort=score_desc&page=0"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")
    products = []

    # Obtener el número de páginas
    try:
        pagination = soup.find(
            "div", {"class": "Pagination_containerLinkPagination__keSJG"}
        ).find_all("ul")
        print(pagination)
        last_page_modified = int(
            pagination[-1].text
        )  # Obtenemos la penúltima entrada que contiene el número de la última página
    except:
        last_page_modified = 0  # En caso de error, asumir que solo hay una página
    print(last_page_modified)
    # Recorrer todas las páginas de resultados
    for page in range(0, last_page_modified):
        result = requests.get(
            "https://www.exito.com/s?q={}&sort=score_desc&page={}".format(
                nombre_producto.replace(" ", "-"), (page * 50) + 1
            )
        )
        content_pagination = result.content
        page_soup = BeautifulSoup(content_pagination, "html.parser")
        print(page_soup)
        # Extraer los datos de los productos
        product_cards = page_soup.find_all(
            "article", {"productCard_productCard__M0677 productCard_column__Lp3OF"}
        )
        for card in product_cards:
            product = {}

            # Nombre del producto
            name_tag = card.find("div", {"class": "styles_name__qQJiK"})
            product["nombre"] = name_tag.text.strip() if name_tag else None

            # Precio del producto
            price_tag = card.find(
                "p", {"class": "ProductPrice_container__price__XmMWA"}
            )
            if price_tag:
                raw_price = price_tag.text.strip()
                product["precio"] = float(raw_price.replace("$", "").replace(",", "."))
            else:
                product["precio"] = None

            # URL de la imagen del producto
            image_tag = card.find("img", {"class": "styles_productCardImage__RBIdi"})
            if image_tag and "src" in image_tag.attrs:
                product["imagen"] = image_tag["src"]
            else:
                product["imagen"] = None

            # Nombre del vendedor
            seller_tag = card.find("span", {"data-fs-product-details-seller__name"})
            if seller_tag:
                seller_name = seller_tag.text.strip().replace("Vendido por: ", "")
                product["vendedor"] = seller_name
            else:
                product["vendedor"] = None

            # Calificación del producto
            rating_tag = card.find(
                "span", {"data-fs-reviews-reviews-ratings-calification"}
            )
            if rating_tag:
                product["calificacion"] = float(rating_tag.text.strip())
            else:
                product["calificacion"] = None

            products.append(product)

    return products


# Solicitar al usuario el nombre del producto a buscar
nombre_producto = input("¿Qué producto quieres buscar en Éxito?: ")
productos = exito_scraper(nombre_producto)

# Mostrar los resultados obtenidos
if productos:
    for producto in productos:
        print(f"Nombre: {producto.get('nombre', 'N/A')}")
        print(f"Precio: {producto.get('precio', 'N/A')}")
        print(f"Imagen: {producto.get('imagen', 'N/A')}")
        print(f"Vendedor: {producto.get('vendedor', 'N/A')}")
        print(f"Calificación: {producto.get('calificacion', 'N/A')}")
else:
    print("No se encontraron productos.")
