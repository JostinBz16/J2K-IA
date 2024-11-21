import google.generativeai as genai
import os


def ProcessInformation(enunciado):
    genai.configure(api_key="AIzaSyBQ9sACIcYwd1byP4ktm_bZ4jqjwhILt3E")
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        f"I want you to give me a detailed description of a product in dictionary format. Based on the provided statement, generate a structure in which the 'name' of the product is appropriate and the 'features' describe the main attributes of the product based on the purpose and specifications mentioned. Here is the statement: '{enunciado}'"
    )
    return response


resultado = ProcessInformation(
    "Busco un teléfono inteligente con una buena cámara para tomar fotos de alta calidad, que tenga suficiente almacenamiento para muchas aplicaciones y fotos, y una batería que dure todo el día. También quiero que sea resistente al agua y que tenga una pantalla grande y de alta resolución para ver videos en buena calidad"
)
print(resultado)
