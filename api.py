from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite acesso do HTML

# Banco de dados em memória
pedidos = []

@app.route('/pedidos', methods=['GET'])
def listar_pedidos():
    return jsonify(pedidos)

@app.route('/pedidos', methods=['POST'])
def adicionar_pedido():
    data = request.get_json()
    if not data or 'cliente' not in data or 'produto' not in data:
        return jsonify({'erro': 'Dados inválidos!'}), 400

    novo_pedido = {
        'id': len(pedidos) + 1,
        'cliente': data['cliente'],
        'produto': data['produto'],
        'status': 'Parado'  # status inicial
    }
    pedidos.append(novo_pedido)
    return jsonify(novo_pedido), 201

@app.route('/pedidos/<int:id>', methods=['DELETE'])
def deletar_pedido(id):
    global pedidos
    pedidos = [p for p in pedidos if p['id'] != id]
    return jsonify({'mensagem': f'Pedido {id} removido com sucesso.'})

@app.route('/pedidos/<int:id>', methods=['PATCH'])
def atualizar_status(id):
    data = request.get_json()
    for p in pedidos:
        if p['id'] == id:
            if 'status' in data:
                p['status'] = data['status']
                return jsonify(p)
    return jsonify({'erro': 'Pedido não encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)
