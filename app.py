import os
from flask import Flask, render_template, flash, redirect, url_for
from IAProcess.recognizeProduct import ProcessInformation
from IAProcess.rankProcess.rankProduct import rankProduct
from IAProcess.Web_Scrape.indexscrapping import scrapping
from config.config import Config
from flask import flash
from utils.db import db  # Importa desde extensiones
from templates.formsApp.form import FormSearchProduct
from services.Producto import ProductoService
from services.Vendedor import VendedorService
from services.Opinion import OpinionService

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


@app.route("/search", methods=["GET", "POST"])
def search():
    form = FormSearchProduct()

    if form.validate_on_submit():
        product_name = form.productName.data
        print("nombre del producto:", product_name)

        try:
            # Llamar a la función de scraping para obtener los productos
            result = scrapping(product_name)

            # Si no se obtienen resultados, lanzar una excepción personalizada
            if not result or len(result) == 0:
                raise NoProductsFoundException("No se encontraron productos")

            for product in result:
                try:
                    # Extraer y validar información del producto
                    nombre_producto = product["nombre_articulo"]
                    url_producto = product["link"]
                    precio = float(
                        product.get("precio_antes", "0")
                        .replace("$", "")
                        .replace(",", "")
                    )
                    valoracion = float(product.get("calificacion", "0"))

                    # Intentar agregar el producto si no existe ya con el mismo nombre y URL
                    nuevo_producto = ProductoService.agregar_producto(
                        nombre=nombre_producto,
                        precio=precio,
                        image_url=product.get("imagen"),
                        url_producto=url_producto,
                        valoracion=valoracion,
                    )

                    # Guardar opiniones asociadas al producto
                    opiniones = product.get("comentarios", [])
                    for comentario in opiniones:
                        # Busca el producto por nombre para obtener el ID
                        producto_bd = ProductoService.buscar_producto_por_nombre(
                            nombre_producto
                        )

                        if producto_bd:
                            OpinionService.agregar_opinion(
                                contenido=comentario,
                                producto_id=producto_bd.id,  # Usa el ID del producto encontrado
                            )

                except ValueError as e:
                    # Si ocurre un error en el producto, continuar con el siguiente
                    error_msg = (
                        f"Error en el producto '{product['nombre_articulo']}': {str(e)}"
                    )
                    print(error_msg)
                    flash(error_msg, "danger")
                    continue

        except NoProductsFoundException as e:
            error_msg = str(e)
            print(error_msg)
            flash(error_msg, "danger")
            return render_template("search.html", form=form)

        except Exception as e:
            error_msg = f"Error durante el procesamiento: {e}"
            print(error_msg)
            flash(error_msg, "danger")
            return render_template("search.html", form=form)

    return render_template("search.html", form=form)

    # if form.validate_on_submit():
    #     try:
    #         flash(f'Form submitted successfully! Name: {form.productName.data}', 'success')
    #         # product = ProcessInformation(form.productName.data)
    #         # nombre_producto = product['nombre']

    #         # scrapping(nombre_producto)
    #         return redirect(url_for('products'))  # Redirige a una página de resultados
    #     except Exception as e:
    #         flash(f'Ocurrió un error: {str(e)}', 'danger')
    # return render_template('search.html', form=form)


@app.route("/products")
def products():
    try:
        # products = (
        #     Producto.query.all()
        # )  # Obtiene todos los productos de la base de datos
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
