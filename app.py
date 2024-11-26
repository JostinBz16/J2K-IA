from flask import Flask, render_template, flash, redirect, url_for, request
import traceback

# from IAProcess.AppProcess.recognizeProduct import ProcessInformation
from IAProcess.AppProcess.recognizeProduct import ProcessInformation
from IAProcess.AppProcess.ranking import recomendar_productos
from IAProcess.Web_Scrape.indexscrapping import scrapping
from IAProcess.AppProcess.analizateProduct import analizateProductsProcess
from config.config import Config
from templates.formsApp.form import FormSearchProduct
from services.Producto import ProductoService
from utils.db import db  # Importa db desde utils/db.py

app = Flask(__name__)
app.config["SECRET_KEY"] = "KKJRE54573FSLKDDF5FDLOLYSVVFW83472386JXT"
app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

# Inicializa la base de datos
db.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["GET", "POST"])
async def search():
    form = FormSearchProduct()
    error_message = None  # Inicializamos el mensaje de error como None

    if form.validate_on_submit():
        product_name = form.productName.data
        ProductoService.set_product_name(product_name)
        try:
            # Llama a la función de scraping y espera los resultados
            recognize = ProcessInformation(product_name)
            nombre_producto = recognize["nombre"]
            result = scrapping(nombre_producto)

            analizateProductsProcess(
                result
            )  # Obtiene los productos de la base de datos

            # Redirige a la página de productos con el nombre del producto
            return redirect(url_for("products"))

        except Exception as e:
            error_message = f"Ocurrió un error inesperado: {str(e)}"

    return render_template("search.html", form=form, error_message=error_message)


@app.route("/products")
def products():
    try:
        # Obtiene el parámetro 'product_name' de la URL
        product_name = ProductoService.get_product_name()

        # Procesa las recomendaciones de productos
        ranked_products = recomendar_productos(product_name)

        # Renderiza los productos recomendados
        return render_template(
            "products.html", productos=ranked_products, product_name=product_name
        )

    except Exception as e:
        flash(f"Ocurrió un error al obtener los productos: {str(e)}", "danger")
        traceback.print_exc()
        return redirect(url_for("index"))


@app.route("/products/details/<int:id>")
def itemDetails(id):
    return render_template("productDetails.html", product_id=id)
