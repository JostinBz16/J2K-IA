import spacy

# Cargar el modelo de SpaCy para español
nlp_es = spacy.load("es_core_news_sm")

# Biblioteca de características ampliada y en minúsculas
caracteristicas_biblioteca = {
    "tamaño": {"cm", "metros", "pulgadas", "tamaño", "medida", "mida", "dimensiones"},
    "color": {"color", "colores","tono", "tonos"},
    "peso": {"kg", "gramos", "peso", "libras"},
    "ram": {"ram"},
    "almacenamiento": {"gb","gigabite","jigas","gigas","tb","teras","almacenamiento","megas","ssd", "hdd", "mb","capacidad", "capacidades","memoria"},
    "pantalla": {"pantalla", "hd", "full hd", "4k", "oled", "lcd", "ips", "oled"},
    "garantía": {"garantía", "soporte", "servicio", "devolución", "devolucion", "devoluciones", "devolucin", "garantia", "garantias"},
    "procesador": {"procesador", "cpu", "núcleo","nucleo", "ghz"},
    "tarjerta grafica": {"gpu", "GPU", "tarjeta grafica","nvidia", "RTX", "amd"},
    "velocidad": {"velocidad", "fps", "latencia", "refresh rate"},
    "conectividad": {"bluetooth", "wifi", "ethernet", "usb", "hdmi"},
    "batería": {"batería", "autonomía", "mah"},
    "material": {"material", "plástico", "metal", "aluminio", "fibra", "cuero"},
    "precio": {"precio", "precios", "valor", "usd", "eur", "cop", "pesos", "millon", "mil", "won", "dolares", "euro", "costo", "coste"}
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
    producto_caracteristicas = {
        "nombre": None,
        "caracteristicas": {}
    }

    doc = nlp_es(enunciado)

    producto = []
    caracteristica_actual = []
    categoria_actual = None
    en_caracteristicas = False

    it = iter(doc)

    palabras_clave_caracteristicas = set()
    for palabras in caracteristicas_biblioteca.values():
        palabras_clave_caracteristicas.update(palabras)

    for palabra in it:
        if palabra.text.lower() in {"y", "o", "pero", "sin", "sin embargo"}:
            categoria_actual = None
            en_caracteristicas = False
            caracteristica_actual = []
            continue

        if palabra.pos_ == "PUNCT":
            if categoria_actual and len(caracteristica_actual) > 0:
                valor_caracteristica = " ".join(caracteristica_actual).strip()
                if categoria_actual in producto_caracteristicas["caracteristicas"]:
                    producto_caracteristicas["caracteristicas"][categoria_actual] += f", {valor_caracteristica}"
                else:
                    producto_caracteristicas["caracteristicas"][categoria_actual] = valor_caracteristica
                caracteristica_actual = []
            categoria_actual = None
            en_caracteristicas = True
            continue

        if palabra.text.lower() in palabras_clave_caracteristicas:
            if categoria_actual and len(caracteristica_actual) > 0:
                valor_caracteristica = " ".join(caracteristica_actual).strip()
                if categoria_actual in producto_caracteristicas["caracteristicas"]:
                    producto_caracteristicas["caracteristicas"][categoria_actual] += f", {valor_caracteristica}"
                else:
                    producto_caracteristicas["caracteristicas"][categoria_actual] = valor_caracteristica
                caracteristica_actual = []
            categoria_actual = determinar_categoria(palabra.text)
            en_caracteristicas = True
            continue

        if categoria_actual and palabra.pos_ in ["NUM", "ADJ", "NOUN", "PROPN", "VERB"]:
            if palabra.pos_ == "NUM":
                try:
                    siguiente = next(it)
                                      
                    caracteristica_actual.append(f"{palabra.text} {siguiente.text}")
                    continue
                except StopIteration:
                    caracteristica_actual.append(palabra.text)
            else:
                caracteristica_actual.append(palabra.text)
        else:
            if not en_caracteristicas and palabra.pos_ in ["NOUN", "PROPN", "ADJ"]:
                producto.append(palabra.text)

    producto_caracteristicas["nombre"] = " ".join(producto).strip()

    if categoria_actual and len(caracteristica_actual) > 0:
        valor_caracteristica = " ".join(caracteristica_actual).strip()
        if categoria_actual in producto_caracteristicas["caracteristicas"]:
            producto_caracteristicas["caracteristicas"][categoria_actual] += f", {valor_caracteristica}"
        else:
            producto_caracteristicas["caracteristicas"][categoria_actual] = valor_caracteristica

    print(producto_caracteristicas)
    return producto_caracteristicas

# Ejemplo de uso
if __name__ == "__main__":
    enunciado1 = "Portátil ASUS TUF gaming F15, 8 GB de RAM, 500 GB de almacenamiento, pantalla de 15.6 pulgadas, color negro, procesador Intel i7, GPU NVIDIA RTX 3060 y tenga un precio menor de 1500 USD"
    resultado1 = ProcessInformation(enunciado1)
    print("Resultado 1:", resultado1)
    
    enunciado2 = "Lápiz mongol azul y que mida 30 cm, peso de 0.5 kg, material de madera, disponible en tienda online y física, precio de 2.5 USD"
    resultado2 = ProcessInformation(enunciado2)
    print("Resultado 2:", resultado2)
    
    enunciado3 = "Smartphone Samsung Galaxy S21, 128 GB de almacenamiento, 8 GB de RAM, pantalla de 6.2 pulgadas, color azul, batería de 4000 mAh, disponible en tiendas oficiales, precio de 799 EUR"
    resultado3 = ProcessInformation(enunciado3)
    print("Resultado 3:", resultado3)
