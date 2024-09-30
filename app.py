import os
from flask import Flask, render_template, flash, redirect, url_for
from IAProcess.recognizeProduct import ProcessInformation 
from IAProcess.rankProcess.rankProduct import rankProduct
from IAProcess.Web_Scrape.indexscrapping import scrapping
from config.config import Config
from utils.db import db  # Importa desde extensiones
from templates.formsApp.form import FormSearchProduct
from models.producto import Producto
from models.opinion import Opinion  # Asegúrate de importar Opinion si lo usas

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'KKJRE54573FSLKD*DF5FDLOLYSVVFW83472386JXT'
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

# Inicializa la base de datos
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = FormSearchProduct()
    if form.validate_on_submit():
        try:
            flash(f'Form submitted successfully! Name: {form.productName.data}', 'success')
            product = ProcessInformation(form.productName.data)
            nombre_producto = product['nombre']
            scrapping(nombre_producto)
            return redirect(url_for('products'))  # Redirige a una página de resultados
        except Exception as e:
            flash(f'Ocurrió un error: {str(e)}', 'danger')
    return render_template('search.html', form=form)

@app.route('/products')
def products():
    try:
        products = Producto.query.all()  # Obtiene todos los productos de la base de datos
        ranked_products = rankProduct([product.to_dict() for product in products])  # Asegúrate de tener un método to_dict en tu modelo
        return render_template('products.html', productos=ranked_products)
    except Exception as e:
        flash(f'Ocurrió un error al obtener los productos: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/products/details/<int:id>')
def itemDetails(id):
    return render_template('productDetails.html', product_id=id)
