from flask import Flask, render_template, url_for, flash, redirect, jsonify
from templates.formsApp.form import FormSearchProduct
from models.producto import Producto
from IAProcess.recognizeProduct import ProcessInformation 
from IAProcess.rankProcess.rankProduct import rankProduct
from IAProcess.Web_Scrape.indexscrapping import scrapping
import json

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'KKJRE54573FSLKD*DF5FDLOLYSVVFW83472386JXT'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = FormSearchProduct()
    if form.validate_on_submit():
        flash(f'Form submitted successfully! Name: {form.productName.data}', 'success')
        product = ProcessInformation(form.productName.data)
        nombre_producto = product['nombre']
        scrapping(nombre_producto)
        return redirect(url_for('products'))  # Redirige a una página de resultados
    return render_template('search.html', form=form)

@app.route('/products')
def products(): 
    productos_scrapeados = './productos_scrapeados.json'
    try:
        productos_rankeados = rankProduct(productos_scrapeados)
        if not productos_rankeados:
            flash('No se pudieron cargar los productos. Por favor, intente más tarde.', 'error')
            return redirect(url_for('index'))
        return render_template('products.html', productos=productos_rankeados)
    except Exception as e:
        print(f"Error al procesar productos: {e}")
        flash('Ocurrió un error al procesar los productos. Por favor, intente más tarde.', 'error')
        return redirect(url_for('index'))

@app.route('/products/details/<int:id>')
def itemDetails(id):
    # Aquí podrías obtener y mostrar los detalles de un producto específico basado en el ID
    return render_template('productDetails.html', product_id=id)

if __name__ == '__main__':
    app.run(debug=True)