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
    "Busco un teléfono xiaomi redmi note 12 color blanco de 128gb con 6gb de ram"
)
print(resultado)
