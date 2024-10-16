import os
from flask import Flask, render_template, flash, redirect, url_for
from IAProcess.recognizeProduct import ProcessInformation
from IAProcess.rankProcess.rankProduct import rankProduct
from IAProcess.Web_Scrape.indexscrapping import scrapping
from config.config import Config
from flask import flash
from utils.db import db  # Importa desde extensiones
from utils.convert import Convert  # Importa desde extensiones
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
    error_message = None  # Inicializamos el mensaje de error como None

    if form.validate_on_submit():
        product_name = form.productName.data

        try:
            # Llama a la función de scraping y espera los resultados
            result = scrapping(product_name)

            # Verifica si la lista de productos no está vacía
            if not result or len(result) == 0:
                raise NoProductsFoundException("No se encontraron productos")

            for product in result:
                # Verificar si el vendedor ya existe en la base de datos
                vendedor = VendedorService.existe_vendedor(product["vendedor"])
                valoracion = (
                    float(product["calificacion"])
                    if product["calificacion"] not in [None, "", "null"]
                    else 0.0
                )
                if vendedor is None:
                    # Validar el valor de "confiable" y asignar False si no está presente o es inválido
                    es_confiable = product.get("confiable", False)

                    nombre_vendedor = product["vendedor"]

                    # Agregar el vendedor
                    VendedorService.agregar_vendedor(nombre_vendedor, es_confiable)

                new_vendedor = VendedorService.existe_vendedor(product["vendedor"])
                # Verificar si el producto ya existe usando el id correcto
                existing_product = ProductoService.existe_producto(
                    product["nombre_articulo"],
                    new_vendedor.id,  # Usar el id del vendedor actual
                )

                if existing_product is not None:
                    continue  # Si el producto ya existe, continuar con el siguiente
                else:
                    # Convertir los precios y crear un nuevo producto
                    precio_actual = Convert.convert_price_to_float(
                        product.get("precio")
                    )

                    # Usar el servicio para agregar el nuevo producto
                    ProductoService.agregar_producto(
                        nombre=product["nombre_articulo"],
                        precio=precio_actual,
                        image_url=product["imagen"],
                        url_producto=product["link"],
                        valoracion=valoracion,
                        vendedor_id=new_vendedor.id,  # Asegurarse de usar el id del vendedor correcto
                    )

                product_exists = ProductoService.existe_producto(
                    product["nombre_articulo"],
                    new_vendedor.id,  # Usar el id del vendedor actual
                )
                print(product_exists)

                # Ahora puedes agregar las opiniones utilizando el ID del nuevo producto
                # Validar si hay comentarios antes de iterar
                comentarios = product.get("comentarios", [])
                if comentarios and isinstance(comentarios, list):
                    # Agregar opiniones si existen comentarios válidos
                    for comentario in comentarios:
                        OpinionService.agregar_opinion(
                            contenido=comentario,
                            producto_id=product_exists.id,  # Usa el ID del producto agregado
                        )

                # Commit de todas las adiciones al final
                db.session.commit()

        except NoProductsFoundException as e:
            error_message = str(e)  # Capturamos el error y lo pasamos al template

        except Exception as e:
            db.session.rollback()  # Revertir cualquier cambio en caso de error
            error_message = f"Ocurrió un error inesperado: {str(e)}"

    return render_template("search.html", form=form, error_message=error_message)


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
