import spacy

# Cargar el modelo de SpaCy para español
nlp_es = spacy.load("es_core_news_sm")

# Biblioteca de características ampliada y en minúsculas
caracteristicas_biblioteca = {
    "tamaño": {"cm", "metros", "pulgadas", "tamaño", "medida", "mida", "dimensiones"},
    "color": {
        "color",
        "colores",
        "tono",
        "tonos",
        "azul",
        "rojo",
        "negro",
        "blanco",
        "verde",
        "amarillo",
        "gris",
        "lila",
        "marron",
        "naranja",
    },
    "peso": {"kg", "gramos", "peso", "libras"},
    "ram": {"ram"},
    "almacenamiento": {
        "gb",
        "gigabite",
        "jigas",
        "gigas",
        "tb",
        "teras",
        "almacenamiento",
        "megas",
        "ssd",
        "hdd",
        "mb",
        "capacidad",
        "capacidades",
        "memoria",
    },
    "tamaño de pantalla": {
        "pantalla",
        "cm",
        "metros",
        "pulgadas",
        "tamaño",
        "medida",
        "mida",
        "dimensiones",
    },
    "resolucion": {"hd", "full hd", "4k"},
    "tipo de pantalla": {"ips", "oled", "lcd", "led", "pantalla oled"},
    "garantía": {"garantía", "soporte", "servicio", "devolución", "garantia"},
    "procesador": {"procesador", "cpu", "núcleo", "nucleo", "ghz"},
    "tarjerta grafica": {"tarjeta grafica", "nvidia", "RTX", "amd"},
    "velocidad": {"velocidad", "fps", "latencia", "refresh rate"},
    "conectividad": {"bluetooth", "wifi", "ethernet", "usb", "hdmi"},
    "batería": {"batería", "autonomía", "mah"},
    "material": {
        "material",
        "plástico",
        "metal",
        "aluminio",
        "fibra",
        "cuero",
        "tela",
        "microfiber",
    },
    "precio": {
        "precio",
        "precios",
        "valor",
        "usd",
        "eur",
        "cop",
        "pesos",
        "millon",
        "mil",
        "won",
        "dolares",
        "euro",
        "euros",
        "wones",
        "costo",
        "coste",
    },
}


# Función para determinar la categoría de una palabra clave
def determinar_categoria(palabra_clave):
    palabra_clave_lower = palabra_clave.lower()
    for categoria, palabras in caracteristicas_biblioteca.items():
        if palabra_clave_lower in palabras:
            return categoria
    return None


# Función para procesar el enunciado
def ProcessInformation(enunciado):
    # Se inicializa el diccionario que almacenará el nombre del producto y sus características
    producto_caracteristicas = {"nombre": None, "caracteristicas": {}}

    # Procesamos el enunciado con el modelo de SpaCy para obtener un objeto doc con las palabras del texto
    doc = nlp_es(enunciado)

    # Inicialización de variables auxiliares
    producto = []  # Para almacenar el nombre del producto
    caracteristica_actual = (
        []
    )  # Para almacenar las características que vamos recogiendo
    categoria_actual = (
        None  # La categoría actual de la característica (e.g., "color", "peso", etc.)
    )
    en_caracteristicas = False  # Indicador de si estamos dentro de una característica

    # Creamos un iterador sobre el doc para procesar cada palabra
    it = iter(doc)

    # Conjunto para almacenar las palabras clave de todas las categorías de características
    palabras_clave_caracteristicas = set()
    for palabras in caracteristicas_biblioteca.values():
        palabras_clave_caracteristicas.update(
            palabras
        )  # Añadir todas las palabras clave a un conjunto

    # Iteramos sobre las palabras del documento
    for palabra in it:
        print(f"Palabra: {palabra.text} | Tipo de palabra: {palabra.pos_}")

        # Si encontramos palabras clave de relación como "y", "o", etc., terminamos de leer una característica
        if palabra.text.lower() in {"y", "o", "pero", "sin", "sin embargo"}:
            categoria_actual = None  # Resetear la categoría
            en_caracteristicas = False  # Salimos de las características
            caracteristica_actual = []  # Limpiamos la lista de características
            continue

        # Si encontramos una puntuación (como coma o punto)
        if palabra.pos_ == "PUNCT":
            # Si hay una característica pendiente, la agregamos a la lista de características del producto
            if categoria_actual and len(caracteristica_actual) > 0:
                valor_caracteristica = " ".join(
                    caracteristica_actual
                ).strip()  # Unimos las palabras de la característica
                if categoria_actual in producto_caracteristicas["caracteristicas"]:
                    # Si ya existe una característica de esa categoría, la agregamos al valor
                    producto_caracteristicas["caracteristicas"][
                        categoria_actual
                    ] += f", {valor_caracteristica}"
                else:
                    # Si no existe, la añadimos por primera vez
                    producto_caracteristicas["caracteristicas"][
                        categoria_actual
                    ] = valor_caracteristica
                caracteristica_actual = []  # Limpiamos la lista de características
            categoria_actual = None  # Reseteamos la categoría
            en_caracteristicas = (
                True  # Indicamos que no estamos leyendo una característica
            )
            continue

        # Si la palabra es una de las palabras clave de características (color, RAM, etc.)
        if palabra.text.lower() in palabras_clave_caracteristicas:
            # Si ya teníamos una característica pendiente, la agregamos antes de procesar la nueva
            if categoria_actual and len(caracteristica_actual) > 0:
                valor_caracteristica = " ".join(
                    caracteristica_actual
                ).strip()  # Unimos la característica
                if categoria_actual in producto_caracteristicas["caracteristicas"]:
                    producto_caracteristicas["caracteristicas"][
                        categoria_actual
                    ] += f", {valor_caracteristica}"
                else:
                    producto_caracteristicas["caracteristicas"][
                        categoria_actual
                    ] = valor_caracteristica
                caracteristica_actual = []  # Limpiamos la lista de características

            categoria_actual = determinar_categoria(
                palabra.text
            )  # Determinamos la categoría de la característica
            en_caracteristicas = (
                True  # Indicamos que ahora estamos leyendo una característica
            )
            continue

        # Si estamos en una categoría y la palabra es un número, adjetivo, sustantivo, o verbo
        if categoria_actual and palabra.pos_ in ["NUM", "ADJ", "NOUN", "PROPN", "VERB"]:
            if palabra.pos_ == "NUM":
                try:
                    siguiente = next(it)  # Intentamos obtener la siguiente palabra
                    if siguiente.pos_ in ["PROPN"]:
                        # Si la siguiente palabra es una unidad (GB, USD, etc.), las unimos con el número
                        caracteristica_actual.append(f"{palabra.text} {siguiente.text}")
                    continue  # Continuamos con la siguiente palabra
                except StopIteration:
                    caracteristica_actual.append(
                        palabra.text
                    )  # Si no hay siguiente palabra, solo agregamos el número
            else:
                caracteristica_actual.append(
                    palabra.text
                )  # Agregamos la palabra a la característica

        # Si no estamos en una característica, pero la palabra es un sustantivo o adjetivo, la consideramos parte del nombre del producto
        else:
            if not en_caracteristicas and palabra.pos_ in ["NOUN", "PROPN"]:
                producto.append(palabra.text)  # Añadimos al nombre del producto

    # Al final del proceso, aseguramos de que las características pendientes se agreguen al diccionario
    producto_caracteristicas["nombre"] = " ".join(
        producto
    ).strip()  # El nombre del producto es lo que queda en la lista 'producto'

    # Si había una característica pendiente, la agregamos
    if categoria_actual and len(caracteristica_actual) > 0:
        valor_caracteristica = " ".join(caracteristica_actual).strip()
        if categoria_actual in producto_caracteristicas["caracteristicas"]:
            producto_caracteristicas["caracteristicas"][
                categoria_actual
            ] += f", {valor_caracteristica}"
        else:
            producto_caracteristicas["caracteristicas"][
                categoria_actual
            ] = valor_caracteristica

    return producto_caracteristicas  # Retornamos el diccionario con el nombre del producto y sus características


# Ejemplo de uso
if __name__ == "__main__":
    enunciado1 = "Portátil ASUS TUF gaming F15, 8 GB de RAM, 500 GB de almacenamiento, pantalla de 15.6 pulgadas, color negro, procesador Intel i7, GPU NVIDIA RTX 3060 y tenga un precio menor de 1500 USD"
    resultado1 = ProcessInformation(enunciado1)
    print("Resultado 1:", resultado1)

    enunciado2 = "Lápiz mongol azul que mida 30 cm, peso de 0.5 kg, material de madera, precio de 2.5 USD"
    resultado2 = ProcessInformation(enunciado2)
    print("Resultado 2:", resultado2)

    # enunciado3 = "Smartphone Samsung Galaxy S21, 128 GB de almacenamiento, 8 GB de RAM, pantalla de 6.2 pulgadas, color azul, batería de 4000 mAh, disponible en tiendas oficiales, precio de 799 EUR"
    # resultado3 = ProcessInformation(enunciado3)
    # print("Resultado 3:", resultado3)
