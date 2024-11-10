from IAProcess.Web_Scrape.Platform.Mercado_Libre import mercado_libre
from IAProcess.Web_Scrape.Platform.Fallabela import falabella


def scrapping(nombre_producto):
    # Obtener productos de Mercado Libre
    # productos_ml = mercado_libre(nombre_producto)

    # Obtener productos de Falabella
    productos_falabella = falabella(nombre_producto)

    # Combinar las listas de productos de ambas plataformas

    return productos_falabella
