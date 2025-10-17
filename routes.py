import requests
from api import *
from flask import Blueprint, request, jsonify
from models import Base, User, Product, Order, OrderItem, Review, SearchHistory


routes = Blueprint("routes", __name__)

# USUÁRIOS
@routes.route("/usuarios", methods=["POST"])
def criar_usuario():
    data = request.json
    novo = User(
        nome=data["nome"],
        email=data["email"],
        senha=data["senha"],
        perfil=data.get("perfil", "cliente")
    )
    db.session.add(novo)
    db.session.commit()
    return jsonify({"msg": "Usuário criado com sucesso!"}), 201


@routes.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = User.query.all()
    return jsonify([{"id": u.id, "nome": u.nome, "email": u.email, "perfil": u.perfil} for u in usuarios])


# PRODUTOS
@routes.route("/produtos", methods=["POST"])
def criar_produto():
    data = request.json
    novo = Product(
        nome=data["nome"],
        descricao=data.get("descricao"),
        preco=data["preco"],
        imagem_url=data.get("imagem_url"),
        validade=data.get("validade"),
        quantidade=data["quantidade"],
        categoria=data.get("categoria")
    )
    db.session.add(novo)
    db.session.commit()
    return jsonify({"msg": "Produto cadastrado com sucesso!"}), 201


@routes.route("/produtos", methods=["GET"])
def listar_produtos():
    produtos = Product.query.all()
    return jsonify([{"id": p.id, "nome": p.nome, "preco": p.preco, "quantidade": p.quantidade} for p in produtos])


# PEDIDOS
@routes.route("/pedidos", methods=["POST"])
def criar_pedido():
    data = request.json
    novo = Order(
        user_id=data["user_id"],
        local_origem=data.get("local_origem"),
        horario_abertura=data.get("horario_abertura")
    )
    db.session.add(novo)
    db.session.commit()
    return jsonify({"msg": "Pedido criado com sucesso!"}), 201


@routes.route("/pedidos", methods=["GET"])
def listar_pedidos():
    pedidos = Order.query.all()
    return jsonify([{"id": o.id, "status": o.status, "data": o.data_pedido} for o in pedidos])


# ITENS DO PEDIDO
@routes.route("/itens", methods=["POST"])
def adicionar_item():
    data = request.json
    novo = OrderItem(
        order_id=data["order_id"],
        product_id=data["product_id"],
        quantidade=data["quantidade"],
        preco_unitario=data["preco_unitario"]
    )
    db.session.add(novo)
    db.session.commit()
    return jsonify({"msg": "Item adicionado ao pedido!"}), 201


# AVALIAÇÕES
@routes.route("/reviews", methods=["POST"])
def criar_review():
    data = request.json
    novo = Review(
        user_id=data["user_id"],
        product_id=data["product_id"],
        nota=data["nota"],
        comentario=data.get("comentario")
    )
    db.session.add(novo)
    db.session.commit()
    return jsonify({"msg": "Avaliação registrada!"}), 201


@routes.route("/reviews/<int:produto_id>", methods=["GET"])
def listar_reviews(produto_id):
    reviews = Review.query.filter_by(product_id=produto_id).all()
    return jsonify([{"id": r.id, "nota": r.nota, "comentario": r.comentario} for r in reviews])


# HISTÓRICO DE PESQUISA
@routes.route("/pesquisas", methods=["POST"])
def salvar_pesquisa():
    data = request.json
    nova = SearchHistory(
        user_id=data["user_id"],
        termo_pesquisa=data["termo"]
    )
    db.session.add(nova)
    db.session.commit()
    return jsonify({"msg": "Pesquisa registrada!"}), 201


@routes.route("/pesquisas/<int:user_id>", methods=["GET"])
def listar_pesquisas(user_id):
    pesquisas = SearchHistory.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": p.id, "termo": p.termo_pesquisa, "data": p.data_pesquisa} for p in pesquisas])

 # ***********
 # ***********
def get_order(id_order):
    caminho = f"http://127.0.0.1:5000/api/orders/{id_order}"
    response = requests.get(caminho)
    # se der certo == 200
    if response.status_code == 200:
        print(response.json()) # printa o q tem no banco
    # se der errado
    else:
        print(response.status_code) # printa codigo de status (504, 300...)
        print(response.json())
