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


@app.route("/search", methods=["GET", "POST"])
def search():
    form = FormSearchProduct()

    if form.validate_on_submit():
        product_name = form.productName.data
        print(
            "nombre del producto:", product_name
        )  # Asegúrate de que se imprime el nombre correcto

        try:
            # Llama a la función de scraping y espera los resultados
            result = scrapping(product_name)  # Cambia `data` por `product_name`

            # Verifica si la lista de productos no está vacía
            if not result or len(result) == 0:
                raise NoProductsFoundException("No se encontraron productos")

            for product in result:
                if product:
                    # Verifica si el producto ya existe en la base de datos por nombre o URL
                    existing_product = Producto.query.filter(
                        (Producto.nombre == product["nombre_articulo"])
                        | (Producto.url_producto == product["link"])
                    ).first()

                    if existing_product:
                        print(
                            f"El producto '{existing_product.nombre}' ya existe en la base de datos.",
                            "info",
                        )
                        continue  # No guarda el producto si ya existe, sigue con el siguiente

                    # Si no existe, lo guarda en la base de datos
                    precio = (
                        float(product["precio_antes"].replace("$", "").replace(",", ""))
                        if product.get("precio_antes")
                        else 0.0
                    )
                    valoracion = (
                        float(product["calificacion"])
                        if "calificacion" in product
                        else None
                    )

                    new_product = Producto(
                        nombre=product["nombre_articulo"],
                        precio=precio,
                        image_url=product.get("imagen"),
                        url_producto=product["link"],
                        valoracion=valoracion,
                    )
                    db.session.add(new_product)
                    db.session.commit()  # Guarda el producto primero

                    # Guardar los comentarios asociados (si existen)
                    for comentario in product.get("comentarios", []):
                        new_opinion = Opinion(
                            contenido=comentario, producto_id=new_product.id
                        )
                        db.session.add(new_opinion)

                    db.session.commit()  # Guarda todas las opiniones

        except NoProductsFoundException as e:
            print(str(e))
            flash("No se encontraron productos con ese nombre.", "danger")
            return render_template("search.html", form=form)

        except Exception as e:
            print(f"Error durante el procesamiento: {str(e)}")
            flash("Ocurrió un error inesperado.", "danger")
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
