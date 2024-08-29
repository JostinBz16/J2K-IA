from flask import Flask, render_template, request

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('query')
    # Aquí iría la lógica para buscar productos
    # Simularemos algunos resultados de búsqueda
    results = ["Producto 1", "Producto 2", "Producto 3"]  # Debes reemplazar esto con la búsqueda real
    return render_template('search.html', results=results)

@app.route('/products')
def products():
    # Aquí podrías listar productos o mostrar detalles de un producto específico
    return render_template('products.html')

@app.route('/products/<int:id>')
def itemDetails(id):
    # Aquí podrías obtener y mostrar los detalles de un producto específico basado en el ID
    return render_template('productDetails.html', product_id=id)

if __name__ == '__main__':
    app.run(debug=True)
