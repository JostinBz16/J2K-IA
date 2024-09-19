from flask import Flask, render_template, url_for, flash, redirect, jsonify
from flask import Flask, render_template, url_for, flash, redirect
from templates.formsApp.form import FormSearchProduct
from models.producto import Producto
from IAProcess.recognizeProduct import ProcessInformation 
from IAProcess.rankProcess.rankProduct import rankProduct
from IAProcess.Web_Scrape.indexscrapping import scrapping

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
    data = [
        {"id": 1, "nombre": "Producto A", "precio": 20, "calidad": 8, "ventas": 500},
        {"id": 2, "nombre": "Producto B", "precio": 35, "calidad": 9, "ventas": 1500},
        {"id": 3, "nombre": "Producto C", "precio": 15, "calidad": 6, "ventas": 200}
    ]
    # Aquí podrías listar productos o mostrar detalles de un producto específico
    products = rankProduct(data)  # Llama a la función que genera el ranking
    # products = jsonify(resultado_dict)  # Devuelve el resultado como una respuesta JSON
    return render_template('products.html', productos = products)

@app.route('/products/details/<int:id>')
def itemDetails(id):
    # Aquí podrías obtener y mostrar los detalles de un producto específico basado en el ID
    return render_template('productDetails.html', product_id=id)

if __name__ == '__main__':
    app.run(debug=True)
