# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import re
# import traceback


# # Función para hacer scraping de los listados de productos en Falabella
# def falabella(nombre_producto):
#     try:
#         base_url = f"https://www.falabella.com.co/falabella-co/search?Ntt={nombre_producto.replace(' ', '+')}"
#         r = requests.get(base_url)
#         contenido = r.content
#         soup = BeautifulSoup(contenido, "html.parser")

#         products_array = []

#         # Obtener el número de páginas
#         try:
#             pagination = soup.find("ol", {"class": "jsx-1389196899"}).find_all("li")
#             last_page_modified = int(pagination[-2].text)  # Última página
#         except:
#             last_page_modified = 1  # En caso de error, solo una página

#         # Recorrer todas las páginas de resultados
#         for page_num in range(1, last_page_modified + 1):
#             # Actualizar URL de la página
#             page_url = f"https://www.falabella.com.co/falabella-co/search?Ntt={nombre_producto.replace(' ', '+')}&page={page_num}"
#             result = requests.get(page_url)
#             content_pagination = result.content
#             soup = BeautifulSoup(content_pagination, "html.parser")

#             # Extraer todos los bloques de producto
#             alldivs = soup.find_all("div", {"class": "jsx-1068418086"})

#             for div in alldivs:
#                 data = {}

#                 # Extraer el nombre del producto
#                 name_tag = div.find("b", {"class": "pod-subTitle"})
#                 data["nombre"] = name_tag.text.strip() if name_tag else None

#                 # Extraer URL del producto
#                 url_tag = div.find("a", {"class": "pod-link"})
#                 a = url_tag.text.strip()
#                 print(a)
#                 # if url_tag and "href" in url_tag.attrs:
#                 #     data["link"] = url_tag["href"]

#                 # Extraer el precio del producto
#                 price_tag = div.find("li", {"data-event-price": True})
#                 if price_tag:
#                     raw_price = price_tag.text.strip()
#                     match = re.search(r"\$\s*([\d\.,]+)", raw_price)
#                     data["precio"] = match.group(1) if match else None

#                 # Extraer la URL de la imagen del producto
#                 img_tag = div.find("img", {"class": "jsx-1996933093"})
#                 data["imagen"] = (
#                     img_tag["src"] if img_tag and "src" in img_tag.attrs else None
#                 )

#                 # Extraer el nombre del vendedor
#                 seller_tag = div.find("span", {"class": "pod-sellerText"})
#                 data["vendedor"] = seller_tag.text.strip() if seller_tag else None

#                 # Extraer comentarios
#                 comentarios = [
#                     comment.text.strip()
#                     for comment in div.find_all("p", {"class": "_review-text_16yc3_2"})
#                 ]
#                 data["comentarios"] = comentarios if comentarios else None

#                 products_array.append(data)

#         return products_array if products_array else []
#     except Exception as e:
#         traceback.print_exc()
#         print(e)


# # Solicitar al usuario el nombre del producto a buscar
# nombre_producto = input("¿Qué producto quieres buscar?: ")
# productos = falabella(nombre_producto)

# # Mostrar los resultados obtenidos
# if productos:
#     for producto in productos:
#         nombre = producto.get("nombre", "N/A")
#         precio = producto.get("precio", "N/A")
#         vendedor = producto.get("vendedor", "N/A")
#         imagen = producto.get("imagen", "N/A")
#         url = producto.get("link", "N/A")
#         print(
#             f"Nombre: {nombre}, Precio: {precio}, Vendedor: {vendedor}, Imagen: {imagen}, Link: {url}"
#         )
# else:
#     print("No se encontraron productos.")
