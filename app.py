from flask import Flask, render_template, url_for, flash, redirect
from formsApp.form import FormSearchProduct


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
        print(form.productName.data)
        return redirect(url_for('products'))  # Redirige a una página de resultados
    return render_template('search.html', form=form)

@app.route('/products')
def products():
    # Aquí podrías listar productos o mostrar detalles de un producto específico
    return render_template('products.html')

@app.route('/products/details/<int:id>')
def itemDetails(id):
    # Aquí podrías obtener y mostrar los detalles de un producto específico basado en el ID
    return render_template('productDetails.html', product_id=id)

if __name__ == '__main__':
    app.run(debug=True)
