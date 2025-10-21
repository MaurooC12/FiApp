from flask import Flask, render_template, request, redirect, url_for
from models import productos

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/productos')
def productos_view():
    lista = productos.listar()
    return render_template('productos.html', productos=lista)

@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    nombre = request.form['nombre']
    categoria = request.form['categoria']
    precio = float(request.form['precio'])
    stock = int(request.form['stock'])
    productos.agregar(nombre, categoria, precio, stock)
    return redirect(url_for('productos_view'))

@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):
    productos.eliminar(id)
    return redirect(url_for('productos_view'))

if __name__ == '__main__':
    productos.crear_tabla()
    app.run(debug=True)
