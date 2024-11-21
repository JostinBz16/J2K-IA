from flask import Flask, render_template, flash, redirect, url_for

# from IAProcess.AppProcess.recognizeProduct import ProcessInformation
from IAProcess.AppProcess.recognizeProduct import ProcessInformation
from IAProcess.AppProcess.rankProduct import rankProduct
from IAProcess.Web_Scrape.indexscrapping import scrapping
from IAProcess.AppProcess.analizateProduct import analizateProductsProcess
from config.config import Config
from templates.formsApp.form import FormSearchProduct
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
def search():
    form = FormSearchProduct()
    error_message = None  # Inicializamos el mensaje de error como None

    if form.validate_on_submit():
        product_name = form.productName.data

        try:
            # Llama a la función de scraping y espera los resultados
            recognize = ProcessInformation(product_name)
            nombre_producto = recognize["nombre"]
            result = scrapping(nombre_producto)

            analizateProductsProcess(
                result
            )  # Obtiene los productos de la base de datos
        except Exception as e:
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
