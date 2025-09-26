from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

app = Flask(__name__)

base_url = "http://10.135.235.11:5002"

def post_login(email, senha):
    try:
        url = f"{base_url}/login"
        dados = {
            "email": email,
            "senha": senha,
        }
        response = requests.post(url, json=dados)
        return response.json()
    except Exception as e:
        print(e)
        return {
            "Error": f"{e}",
        }


def get_usuarios(token):
    try:
        url = f"{base_url}/usuarios"
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
        return response.json()
    except Exception as e:
        print(e)
        return {
            "Error": f"{e}",
        }


def post_usuario(nome, email, senha, papel, token):
    try:
        url = f"{base_url}/usuarios"
        dados = {
            "email": email,
            "senha": senha,
            "nome": nome,
            "papel": papel,
        }
        response = requests.post(url, json=dados, headers={"Authorization": f"Bearer {token}"})
        return response.status_code
    except Exception as e:
        print(e)
        return {
            "Error": f"{e}",
        }


@app.route('/')
def template():
    return render_template('template.html')


@app.route('/cadastro_clientes')
def cadastro_cliente():
    return render_template('cadastro_cliente.html')




@app.route('/cadastro_calcados')
def cadastro_calcados():
    return render_template('cadastro_calcados.html')


@app.route('/cadastro_pedidos')
def cadastro_pedidos():
    return render_template('cadastro_pedidos.html')


@app.route('/lista_calcados')
def lista_calcados():
    return render_template('lista_calcados.html')


@app.route('/lista_pedidos')
def lista_pedidos():
    return render_template('lista_pedidos.html')


@app.route('/pedidos')
def pedidos():
    return render_template('pedidos.html')


@app.route('/lista_clientes')
def lista_clientes():
    return render_template('lista_clientes.html')

@app.route("/lista_cliente_api", methods=["GET"])
def get_clientes():
    return jsonify(clientes)

# Endpoint para adicionar cliente
@app.route("/api/clientes", methods=["POST"])
def add_cliente():
    novo_cliente = request.json
    novo_cliente["id"] = len(clientes) + 1
    clientes.append(novo_cliente)
    return jsonify(novo_cliente), 201



@app.route("/lista_cliente_api", methods=["GET"])
def get_clientes():
    return jsonify(lista_clientes)

# Endpoint para adicionar cliente
@app.route("/api/clientes", methods=["POST"])
def add_cliente():
    novo_cliente = request.json
    novo_cliente["id"] = len(clientes) + 1
    clientes.append(novo_cliente)
    return jsonify(novo_cliente), 201


@app.route('/submit', methods=['POST'])
def login():
    email = request.form['email']
    senha = request.form['senha']
    tipo = request.form['tipo']

    # Aqui você faria a verificação com banco de dados
    if tipo == 'admin' and email == 'admin@site.com' and senha == 'admin123':
        return redirect('/admin-dashboard')
    elif tipo == 'usuario' and email == 'usuario@site.com' and senha == 'usuario123':
        return redirect('/usuario-dashboard')
    else:
        return "Credenciais inválidas", 401

if __name__ == '__main__':
    app.run(debug=True)
