import os
from flask import Flask, render_template, flash, redirect, url_for
from IAProcess.recognizeProduct import ProcessInformation
from IAProcess.rankProcess.rankProduct import rankProduct
from IAProcess.Web_Scrape.indexscrapping import scrapping
from config.config import Config
from flask import flash
from utils.db import db  # Importa desde extensiones
from templates.formsApp.form import FormSearchProduct
from models.producto import Producto
from models.opinion import Opinion  # Asegúrate de importar Opinion si lo usas

app = Flask(__name__, static_folder="static")
app.config["SECRET_KEY"] = "KKJRE54573FSLKD*DF5FDLOLYSVVFW83472386JXT"
app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

# Inicializa la base de datos
db.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")


class NoProductsFoundException(Exception):
    """Excepción personalizada para cuando no se encuentran productos"""

    pass


def convert_price_to_float(price_string):
    """
    Convierte un string de precio en formato "$3.399.150" o "3.999.000" en un float.
    """
    if price_string:
        # Eliminamos el símbolo de moneda y los separadores de miles
        price_string = price_string.replace("$", "").replace(".", "").replace(",", ".")
        try:
            return float(price_string)
        except ValueError:
            return 0.0
    return 0.0


@app.route("/search", methods=["GET", "POST"])
def search():
    form = FormSearchProduct()
    error_message = None  # Inicializamos el mensaje de error como None

    if form.validate_on_submit():
        product_name = form.productName.data
        print(f"nombre del producto: {product_name}")

        try:
            # Llama a la función de scraping y espera los resultados
            result = scrapping(product_name)

            # Verifica si la lista de productos no está vacía
            if not result or len(result) == 0:
                raise NoProductsFoundException("No se encontraron productos")

            for product in result:
                existing_product = Producto.query.filter(
                    Producto.url_producto == product["link"]
                ).first()

                if existing_product:
                    continue

                # Convertir los precios y crear un nuevo producto
                precio_actual = convert_price_to_float(product.get("precio"))
                valoracion = (
                    float(product["calificacion"])
                    if "calificacion" in product
                    else None
                )

                new_product = Producto(
                    nombre=product["nombre_articulo"],
                    precio=precio_actual,
                    image_url=product.get("imagen"),
                    url_producto=product["link"],
                    valoracion=valoracion,
                )
                db.session.add(new_product)
                db.session.commit()

                for comentario in product.get("comentarios", []):
                    new_opinion = Opinion(
                        contenido=comentario, producto_id=new_product.id
                    )
                    db.session.add(new_opinion)

                db.session.commit()

        except NoProductsFoundException as e:
            error_message = str(e)  # Capturamos el error y lo pasamos al template

        except Exception as e:
            error_message = f"Ocurrió un error inesperado: {str(e)}"

    return render_template("search.html", form=form, error_message=error_message)


@app.route("/products")
def products():
    try:
        products = (
            Producto.query.all()
        )  # Obtiene todos los productos de la base de datos
        ranked_products = rankProduct(
            [product.to_dict() for product in products]
        )  # Asegúrate de tener un método to_dict en tu modelo
        return render_template("products.html", productos=ranked_products)
    except Exception as e:
        flash(f"Ocurrió un error al obtener los productos: {str(e)}", "danger")
        return redirect(url_for("index"))


@app.route("/products/details/<int:id>")
def itemDetails(id):
    return render_template("productDetails.html", product_id=id)
