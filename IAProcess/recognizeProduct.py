import spacy

nlp_es = spacy.load("es_core_news_sm")

producto_caracteristicas = {
    "nombre": None,
    "caracteristicas": {}
}

def ProcessInformation(enunciado) :
    print(enunciado)

