import requests
from bs4 import BeautifulSoup
import pandas as pd
import json


String = input("Ingresa el nombre del producto: ")
r = requests.get("https://listado.mercadolibre.com.co/{}#D[A:{}]".format(String.replace(' ', '-'), String))
contenido = r.content

soup = BeautifulSoup(contenido, 'html.parser')

# Ultima página
try:
    pagination = soup.find('ul', {'class': 'andes-pagination'}).find_all('li')
    last_page_modified = int(pagination[-2].text)  # Obtenemos la penúltima entrada que contiene el número de la última página
except:
    last_page_modified = 1  # En caso de error, asumir que solo hay una página

# Array para añadir los objetos
products_array = []

for page in range(0, last_page_modified):
    result = requests.get('https://listado.mercadolibre.com.co/{}_Desde_{}_NoIndex_True'.format(String.replace(' ', '-'), (page*50)+1))
    content_pagination = result.content
    soup_pagination = BeautifulSoup(content_pagination, 'html.parser')

    # Asegúrate de usar el selector correcto para los productos
    alldivs = soup_pagination.find_all('div', {'class': 'ui-search-result__wrapper'})  # Cambiar selector por el actual

    for item in alldivs:
        data = {}
        data['nombre_articulo'] = item.find('h2', {'class': 'poly-box poly-component__title'}).text
        data['precio'] = item.find('span', {'class': 'andes-money-amount'}).text
        data['link'] = item.find('a', {'class': ''})['href']
        products_array.append(data)
        #print(data)

# Convertir a DataFrame y mostrar
df = pd.DataFrame(products_array)
print(df)

archivo_json = 'productos.json'
with open(archivo_json, 'w') as file:
    json.dump(products_array, file, indent=4, ensure_ascii=False)