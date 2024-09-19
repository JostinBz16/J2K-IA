import json
import requests
from bs4 import BeautifulSoup

# Leer el archivo JSON
with open('productos.json', 'r') as f:
    data = json.load(f)

# Función para hacer scraping y extraer la información
def scrape_producto(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraer el nombre del producto
        nombre = soup.find('h1', {'class': 'ui-pdp-title'})
        nombre = nombre.get_text() if nombre else 'Nombre no encontrado'

        # Extraer el precio del producto
        precio = soup.find('span', {'class': 'andes-money-amount'})
        precio = precio.get_text() if precio else 'Precio no encontrado'

        # Extraer la imagen del producto
        imagen = soup.find('img')
        imagen = imagen['src'] if imagen else 'Imagen no encontrada'

        # Extraer la valoración (si existe)
        valoracion = soup.find('div', {'class': 'ui-pdp-header__info'})
        valoracion = valoracion.get_text() if valoracion else 'Valoración no encontrada'

        return {
            'nombre': nombre,
            'precio': precio,
            'imagen': imagen,
            'valoracion': valoracion
        }
    else:
        return {'error': 'No se pudo acceder a la página'}

# Crear una lista para almacenar los resultados
productos_scrapeados = []

# Recorrer los productos y hacer scraping a cada uno
for producto in data:
    url = producto['link']
    print(f"Scraping el producto: {producto['nombre_articulo']}")
    resultado = scrape_producto(url)
    
    # Comprobar que el scraping no haya dado errores
    if 'error' not in resultado:
        productos_scrapeados.append({
            'nombre': resultado.get('nombre', 'Nombre no encontrado'),
            'precio': resultado.get('precio', 'Precio no encontrado'),
            'imagen': resultado.get('imagen', 'Imagen no encontrada'),
            'valoracion': resultado.get('valoracion', 'Valoración no encontrada')
        })
    else:
        print(f"Error scraping {url}: {resultado['error']}")

# Guardar los resultados en un archivo JSON
with open('productos_scrapeados.json', 'w') as outfile:
    json.dump(productos_scrapeados, outfile, indent=4, ensure_ascii=False)

print("Scraping completado. Resultados guardados en 'productos_scrapeados.json'.")
