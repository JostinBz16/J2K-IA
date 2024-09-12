import spacy

# Cargar el modelo de SpaCy para español
nlp_es = spacy.load("es_core_news_sm")

# Función para procesar el enunciado
def ProcessInformation(enunciado):
    # Limpiar el diccionario antes de procesar un nuevo enunciado
    producto_caracteristicas = {
        "nombre": None,
        "caracteristicas": {}
    }

    # Procesar el enunciado con el modelo de SpaCy
    doc = nlp_es(enunciado)

    producto = []
    caracteristica_actual = []
    clave_actual = None

    # Palabras clave que típicamente indican el tipo de características
    palabras_clave_caracteristicas = {"GB", "RAM", "almacenamiento", "color", "cm", "mida"}

    for palabra in doc:
        print(palabra.text, palabra.pos_)  # Ver las etiquetas POS de cada palabra

        # Si encontramos una coma, es el fin de la característica actual
        if palabra.pos_ == "PUNCT":
            if clave_actual and len(caracteristica_actual) > 0:
                producto_caracteristicas["caracteristicas"][clave_actual] = " ".join(caracteristica_actual)
                caracteristica_actual = []  # Limpiar para la siguiente característica
            clave_actual = None
            continue

        # Detectar si estamos en las características o aún en el nombre del producto
        if palabra.text in palabras_clave_caracteristicas:
            clave_actual = palabra.text  # Asignamos la palabra clave como el nombre de la característica
            continue

        # Detectar números o adjetivos que podrían ser parte del valor de una característica
        if clave_actual and palabra.pos_ in ["NUM", "ADJ", "NOUN", "PROPN"]:
            caracteristica_actual.append(palabra.text)
        else:
            # Si estamos en el nombre del producto
            if palabra.pos_ in ["NOUN", "PROPN"] and not clave_actual:
                producto.append(palabra.text)

    # Unir el nombre del producto
    producto_caracteristicas["nombre"] = " ".join(producto)

    # Agregar la última característica si no fue añadida
    if clave_actual and len(caracteristica_actual) > 0:
        producto_caracteristicas["caracteristicas"][clave_actual] = " ".join(caracteristica_actual)

    print(producto_caracteristicas)
    return producto_caracteristicas


# # Ejemplo de uso
# enunciado = "Portatil ASUS TUF gaming F15, 8 GB de RAM, 500 GB de almacenamiento"
# resultado = ProcessInformation(enunciado)
# print(resultado)

# enunciado2 = "Lapiz mongol azul y que mida 30 cm"
# resultado2 = ProcessInformation(enunciado2)
# print(resultado2)
