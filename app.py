from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from sqlalchemy import select
from datetime import datetime
from models import *
from flask_jwt_extended import create_access_token, jwt_required, JWTManager

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = "03050710"
jwt = JWTManager(app)



# Cadastro (POST)
@app.route('/pessoas/cadastrar', methods=['POST'])
def cadastrar_pessoas():
    db_session = local_session()
    try:
        dados_pessoas = request.get_json()

        campos_obrigatorios = ["nome_pessoa", "cpf_pessoa", "cargo", "senha", "status"]
        if not all(campo in dados_pessoas for campo in campos_obrigatorios):
            return jsonify({"error": "Campo inexistente"}), 400

        if any(not dados_pessoas[campo] for campo in campos_obrigatorios):
            return jsonify({"error": "Preencher todos os campos"}), 400

        nome_pessoa = dados_pessoas["nome_pessoa"]
        cpf = dados_pessoas["cpf_pessoa"]
        cargo = dados_pessoas["cargo"]
        senha = dados_pessoas["senha"]
        status_texto = dados_pessoas["status"]   # ← vem como "Ativo" ou "Inativo"

        #  CONVERSÃO DE TEXTO PARA BOOLEANO
        status_limpo = status_texto.strip().lower()
        if status_limpo == "ativo":
            status_bool = True
        elif status_limpo == "inativo":
            status_bool = False
        else:
            return jsonify({"error": "Status inválido. Use 'Ativo' ou 'Inativo'."}), 400

        # Validação básica do CPF
        if not cpf or len(cpf) != 11:
            return jsonify({"msg": "O CPF deve conter exatamente 11 dígitos numéricos."}), 400

        form_nova_pessoa = Pessoa(
            nome_pessoa=nome_pessoa,
            cpf_pessoa=cpf,
            cargo=cargo,
            status=status_bool,      # agora é booleano
        )

        form_nova_pessoa.set_senha_hash(senha)
        form_nova_pessoa.save(db_session)

        dicio = form_nova_pessoa.serialize()
        resultado = {"success": "Cadastrado com sucesso", "pessoas": dicio}

        return jsonify(resultado), 201

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        db_session.close()



@app.route('/produtos/cadastrar', methods=['POST'])
def cadastrar_produto():
    # Abre a sessão do banco
    db_session = local_session()
    try:
        # Recebe os dados enviados pelo JS (JSON)
        dados_produto = request.get_json()

        # Campos obrigatórios
        campos_obrigatorios = [
            "id_categoria",
            "nome_produto",
            "tamanho",
            "genero",
            "marca_produto",
            "custo_produto"
        ]

        # Verifica se algum campo obrigatório está faltando
        if not all(campo in dados_produto for campo in campos_obrigatorios):
            return jsonify({"error": "Campo inexistente"}), 400

        # Verifica se algum campo obrigatório está vazio (None ou string vazia)
        if any(dados_produto[campo] in [None, ""] for campo in campos_obrigatorios):
            return jsonify({"error": "Preencher todos os campos"}), 400

        # Monta o objeto Produto
        form_novo_produto = Produto(
            id_categoria=dados_produto['id_categoria'],
            nome_produto=dados_produto['nome_produto'],
            tamanho=dados_produto['tamanho'],
            genero=dados_produto['genero'],
            marca_produto=dados_produto['marca_produto'],
            custo_produto=dados_produto['custo_produto']
        )

        # Salva no banco
        form_novo_produto.save(db_session)

        # Serializa o produto cadastrado
        produto_serializado = form_novo_produto.serialize()

        # Retorna sucesso + dados do produto
        return jsonify({
            "success": "Produto cadastrado com sucesso!",
            "produtos": produto_serializado
        }), 201

    except Exception as e:
        # Retorna erro caso ocorra algum problema
        return jsonify({"error": str(e)}), 500

    finally:
        # Fecha a sessão do banco
        db_session.close()



@app.route("/entradas", methods=["POST"])
def cadastrar_entrada():
    # Pega a Informação
    dados = request.json

    # Campos obrigatórios
    campos_obrigatorios = ["id_pessoa", "id_produto", "quantidade", "nota_fiscal", "valor_entrada"]
    if not all(campo in dados for campo in campos_obrigatorios):
        return jsonify({"error": "Campos obrigatórios ausentes"}), 400

    # Caso os Campos não tenham sido Preenchidos
    if any(dados[campo] == "" for campo in campos_obrigatorios):
        return jsonify({"error": "Preencha todos os campos"}), 400

    # Verificar se o Produto existe
    produto = local_session.query(Produto).filter_by(id_produto=dados["id_produto"]).first()
    if not produto:
        return jsonify({"error": "Insumo não encontrado"}), 404
    # Verificar se a Pessoa existe
    pessoa = local_session.query(Pessoa).filter_by(id_pessoa=dados["id_pessoa"]).first()
    if not produto:
        return jsonify({"error": "Insumo não encontrado"}), 404

    # Mostra a Data e Horário Cadastrada da Entrada
    data_entrada = str(datetime.now())

    # Validações numéricas
    try:
        qtd = int(dados["quantidade"])
        valor = float(dados["valor_entrada"])
    # Caso o Valor de Entrada seja Inválido
    except ValueError:
        return jsonify({"error": "Quantidade e valor devem ser numéricos"}), 400

    # Caso o Valor seja Menor ou igual a Zero
    if qtd <= 0 or valor <= 0:
        return jsonify({"error": "Quantidade e Valor devem ser maiores que Zero"}), 400

    # Atualiza o estoque do insumo
    produto.qtd_produto += qtd

    # Cria a entrada
    nova_entrada = Entrada(
        nota_fiscal=dados["nota_fiscal"],
        data_entrada=data_entrada,
        quantidade=qtd,
        valor_entrada=valor,
        id_produto=produto.id_produto,
        id_pessoa=pessoa.id_pessoa
    )

    try:
        # Salva a Entrada
        nova_entrada.save(local_session)
        produto.save(local_session)

        return jsonify({
            "success": "Entrada cadastrada com sucesso",
            "entrada": nova_entrada.serialize()
        }), 201

    # Caso não tenha Salvado
    except Exception as e:
        return jsonify({"error": f"Erro ao salvar entrada: {str(e)}"}), 500


@app.route('/vendas', methods=['POST'])
def cadastrar_venda():
    # Abre o Banco
    db_session = local_session()
    try:
        # Pega a Informação
        dados = request.get_json()
        campos = ["forma_pagamento", "quantidade", "id_pessoa", "id_produto"]

        # Caso os Campos não tenham sido Preenchidos
        if not all(campo in dados for campo in campos):
            return jsonify({"error": "Campos obrigatórios não informados"}), 400

        # Tabela para Cadastrar Vendas
        forma_pagamento = dados["forma_pagamento"]
        quantidade = dados["quantidade"]
        data_emissao = str(datetime.now())
        id_produto = dados["id_produto"]
        id_pessoa = dados["id_pessoa"]

        produto = db_session.query(Produto).filter_by(id_produto=id_produto).first()
        pessoa = db_session.query(Pessoa).filter_by(id_pessoa=id_pessoa).first()

        # Caso não encontre o Produto
        if not produto:
            return jsonify({"error": "produto não encontrado"}), 404
        # Caso não encontre a Pessoa
        if not pessoa:
            return jsonify({"error": "Pessoa não encontrada"}), 404

        # Verificar Estoque
        if produto.qtd_produto < quantidade:
            return jsonify({"error": f"Estoque insuficiente para: {produto.nome_produto}"}), 400

        # Dar Baixa no Produto
        produto = db_session.query(Produto).filter_by(id_produto=id_produto).first()
        produto.qtd_produto -= quantidade
        db_session.add(produto)

        # Registrar Vendas
        vendas_registradas = []
        for _ in range(quantidade):
            nova_venda = Venda(
                data_emissao=data_emissao,
                id_produto=id_produto,
                id_pessoa=id_pessoa,
                quantidade=quantidade,
                valor_venda=produto.custo_produto,
                forma_pagamento=forma_pagamento,
            )
            # Salva as Vendas Cadastradas
            nova_venda.save(db_session)
            venda_dict = nova_venda.serialize()
            # converter de volta para int no retorno
            vendas_registradas.append(venda_dict)

        # Mostra todas as Vendas Cadastradas
        return jsonify({
            "success": f"{quantidade} vendas registradas com sucesso",
            "vendas": vendas_registradas
        }), 201

    # Caso ocorra algum Erro
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
    # Fecha o Banco
    finally:
        db_session.close()


@app.route('/categorias', methods=['POST'])
def cadastrar_categoria():
    # Abre o Banco
    db_session = local_session()
    try:
        # Pega a Informação
        dados_categoria = request.get_json()

        # Caso o Campo não exista
        if not 'nome_categoria' in dados_categoria:
            return jsonify({
                "error": "Campo inexistente",
            })
        # Caso não tenha Preenchido todos
        if dados_categoria['nome_categoria'] == "":
            return jsonify({
                "error": "Preencher todos os campos"
            })
        else:
            # Cria a Categoria
            nome_categoria = dados_categoria['nome_categoria']
            form_nova_categoria = Categoria(
                nome_categoria=nome_categoria,
            )
            # Salva a Categoria
            form_nova_categoria.save(db_session)

            dicio = form_nova_categoria.serialize()
            # Mostra se Salvou e mostra todas as Categorias
            resultado = {"success": "Categoria cadastrada com sucesso", "categorias": dicio}

            return jsonify(resultado), 201
    except Exception as e:
        # Caso ocorra algum Erro
        return jsonify({"error": str(e)})
    # Fecha o Banco
    finally:
        db_session.close()



# LISTAR (GET)
@app.route('/produtos/listar', methods=['GET'])
def listar_produtos():
    # Abre o Banco
    db_session = local_session()
    try:
        # Pega e mostra todos os Produtos
        sql_produto = select(Produto)
        resultado_produtos = db_session.execute(sql_produto).scalars()
        produtos = []

        for n in resultado_produtos:
            produtos.append(n.serialize())
        return jsonify({
            "produtos": produtos,
            "success": "Listado com sucesso",
        })
    # Caso ocorra algum Erro
    except Exception as e:
        return jsonify({"error": str(e)})
    # Fecha o Banco
    finally:
        db_session.close()


@app.route('/categorias', methods=['GET'])
def listar_categorias():
    # Abre o Banco
    db_session = local_session()
    try:
        # Pega e Mostra todas as Categorias
        sql_categorias = select(Categoria)
        resultado_categorias = db_session.execute(sql_categorias).scalars()
        categorias = []
        for n in resultado_categorias:
            categorias.append(n.serialize())
        return jsonify({
            "categorias": categorias,
            "success": "Listado com sucesso",
        })
    # Caso ocorra algum Erro
    except Exception as e:
        return jsonify({"error": str(e)})
    # Fecha o Banco
    finally:
        db_session.close()


@app.route('/entradas', methods=['GET'])
def listar_entradas():
    # Abre o Banco
    db_session = local_session()
    try:
        # Pega e mostra todas as Entradas
        sql_entradas = select(Entrada)
        resultado_entradas = db_session.execute(sql_entradas).scalars()
        entradas = []
        for n in resultado_entradas:
            entradas.append(n.serialize())
        return jsonify({
            "entradas": entradas,
            "success": "Listado com sucesso",
        })
    # Caso ocorra algum Erro
    except Exception as e:
        return jsonify({"error": str(e)})
    # Fecha o Banco
    finally:
        db_session.close()


@app.route('/vendas', methods=['GET'])
def listar_vendas():
    # Abre o Banco
    db_session = local_session()
    try:
        # Pega e mostra todas as Vendas
        sql_vendas = select(Venda)
        venda_resultado = db_session.execute(sql_vendas).scalars()
        vendas = []
        for n in venda_resultado:
            vendas.append(n.serialize())
        return jsonify({
            "vendas": vendas
        })
    # Caso ocorra algum Erro
    except Exception as e:
        return jsonify({"error": str(e)})
    # Fecha o Banco
    finally:
        db_session.close()


@app.route('/pessoas', methods=['GET'])
def listar_pessoas():
    # Abre o Banco
    db_session = local_session()
    try:
        # Pega e mostra todas as Pessoas
        sql_pessoa = select(Pessoa)
        resultado_pessoas = db_session.execute(sql_pessoa).scalars()
        pessoas = []
        for n in resultado_pessoas:
            pessoas.append(n.serialize())

        return jsonify({
            "pessoas": pessoas,
            "success": "Listado com sucesso"
        })
    # Caso ocorra um Erro
    except Exception as e:
        return jsonify({"error": str(e)})
    # Fecha o Banco
    finally:
        db_session.close()



# EDITAR (PUT)
@app.route('/produtos/<id_produto>', methods=['PUT'])
def editar_produto(id_produto):
    db_session = local_session()
    try:
        # Pega a Informação
        dados_editar_produto = request.get_json()

        produto_resultado = db_session.execute(select(Produto).filter_by(id_produto=int(id_produto))).scalar()

        # Caso o Produto não seja encontrado
        if not produto_resultado:
            return jsonify({"error": "produto não encontrado"}), 400

        campos_obrigatorios = ["id_categoria", "nome_produto", "tamanho", "genero", "marca_produto", "custo_produto"]

        # Caso não tenha Preenchido todos os Campos
        if any(not dados_editar_produto[campo] for campo in campos_obrigatorios):
            return jsonify({"error": "Preencher todos os campos"}), 400

        # Caso não exista o Campo
        if not all(campo in dados_editar_produto for campo in campos_obrigatorios):
            return jsonify({"error": "Campo inexistente"}), 400

        # Tabela para Editar Produto
        else:
            produto_resultado.nome_produto = dados_editar_produto['nome_produto']
            produto_resultado.tamanho = dados_editar_produto['tamanho']
            produto_resultado.marca_produto = dados_editar_produto['marca_produto']
            produto_resultado.custo_produto = dados_editar_produto['custo_produto']
            produto_resultado.genero = dados_editar_produto['genero']
            produto_resultado.id_categoria = dados_editar_produto['id_categoria']

            # Salva o Produto
            produto_resultado.save(db_session)
            dicio = produto_resultado.serialize()
            resultado = {"success": "produto editado com sucesso", "produtos": dicio}

            return jsonify(resultado), 201

    # Caso o Valor seja Inválido
    except ValueError:
        return jsonify({
            "error": "Valor inserido inválido"
        }), 400

    # Caso ocorra algum Erro
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()


@app.route('/categorias/<id_categoria>', methods=['PUT'])
def editar_categoria(id_categoria):
    db_session = local_session()
    try:
        dados_editar_categoria = request.get_json()

        categoria_resultado = db_session.execute(select(Categoria).filter_by(id_categoria=int(id_categoria))).scalar()

        # Caso não exista a Categoria
        if not categoria_resultado:
            return jsonify({
                "error": "Categoria não encontrada"
            })

        # Caso o Campo não exista
        if not 'nome_categoria' in dados_editar_categoria:
            return jsonify({
                "error": "Campo inexistente"
            }), 400

        # Caso não tenha Preenchido todos os Campos
        if dados_editar_categoria['nome_categoria'] == "":
            return jsonify({
                "error": "Preencher todos os campos"
            }), 400

        # Tabela para Editar Categoria
        else:
            categoria_resultado.nome_categoria = dados_editar_categoria['nome_categoria']

            # Salva a Categoria
            categoria_resultado.save(db_session)

            dicio = categoria_resultado.serialize()
            resultado = {"success": "categoria editado com sucesso", "categorias": dicio}

            return jsonify(resultado), 200

    # Caso o Valor Inserido seja Inválido
    except ValueError:
        return jsonify({
            "error": "Valor inserido inválido"
        }), 400

    # Caso exista algum Erro
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        db_session.close()



@app.route('/pessoas/<id_pessoa>', methods=['PUT'])
# @jwt_required()
def editar_pessoa(id_pessoa):
    db_session = local_session()
    try:
        # Pega a Informação
        dados_editar_pessoa = request.get_json()

        pessoa_resultado = db_session.execute(select(Pessoa).filter_by(id_pessoa=int(id_pessoa))).scalar()

        # Caso não exista a Pessoa
        if not pessoa_resultado:
            return jsonify({"error": "Pessoa não encontrada"}), 400

        campos_obrigatorios = ["nome_pessoa", "cargo", "senha", "cpf_pessoa"]

        # Caso não tenha Preenchido todos os Campos
        if any(not dados_editar_pessoa[campo] for campo in campos_obrigatorios):
            return jsonify({"error": "Preencher todos os campos"}), 400

        # Caso não exista o Campo
        if not all(campo in dados_editar_pessoa for campo in campos_obrigatorios):
            return jsonify({"error": "Campo inexistente"}), 400

        # Edita a Tabela Pessoa
        else:
            pessoa_resultado.nome_pessoa = dados_editar_pessoa['nome_pessoa']
            pessoa_resultado.cargo = dados_editar_pessoa['cargo']
            pessoa_resultado.senha = dados_editar_pessoa['senha']
            pessoa_resultado.cpf_pessoa = dados_editar_pessoa['cpf_pessoa']

            # Salva a Senha Nova
            pessoa_resultado.set_senha_hash(pessoa_resultado.senha)
            pessoa_resultado.save(db_session)

            dicio = pessoa_resultado.serialize()
            resultado = {"success": "Pessoa editada com sucesso", "pessoas": dicio}

            return jsonify(resultado), 200

    # Caso o Valor Inserido seja Inválido
    except ValueError:
        return jsonify({
            "error": "Valor inserido inválido"
        })

    # Caso ocorra algum Erro
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        db_session.close()


# Inicia
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
