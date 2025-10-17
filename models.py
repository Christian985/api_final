from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base, relationship


engine = create_engine('sqlite:///informacoes.sqlite3')

# Gerencia as sessões com o Banco de Dados
db_session = scoped_session(sessionmaker(bind=engine))


Base = declarative_base()
Base.query = db_session.query_property()


# MODELO USUÁRIOS
class User(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    senha = Column(String(200), nullable=False, index=True)
    perfil = Column(String(50), default="cliente", nullable=False, index=True)

    pedidos = relationship("Order", backref="usuario", lazy=True)
    reviews = relationship("Review", backref="autor", lazy=True)
    pesquisas = relationship("SearchHistory", backref="usuario", lazy=True)

    def __repr__(self):
        return '<User: {} {} {} {}>'.format( self.nome,
                                              self.email,
                                              self.senha,
                                              self.perfil
                                              )

    # Função para Salvar no Banco
    def save(self):
        db_session.add(self)
        db_session.commit()

    # Função para Deletar no Banco
    def delete(self):
        db_session.delete(self)
        db_session.commit()

    # Coloca os Dados na Tabela
    def serialize(self):
        dados_user = {
            'nome': self.nome,
            'categoria': self.email,
            'senha': self.senha,
            'perfil': self.perfil,
        }
        return dados_user



# MODELO PRODUTOS
class Product(Base):
    __tablename__ = "produto"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False, index=True)
    descricao = Column(String(200), nullable=False, index=True)
    preco = Column(Integer, nullable=False, index=True)
    imagem_url = Column(String(255), nullable=False, index=True)
    validade = Column(String(50), nullable=False, index=True)
    quantidade = Column(Integer, nullable=False, index=True)
    categoria = Column(String(50), nullable=False, index=True)

    itens = relationship("OrderItem", backref="produto", lazy=True)
    reviews = relationship("Review", backref="produto", lazy=True)

    def __repr__(self):
        return '<Produto: {} {} {} {} {} {} {}>'.format( self.nome,
                                                        self.descricao,
                                                        self.preco,
                                                        self.imagem_url,
                                                        self.validade,
                                                        self.quantidade,
                                                        self.categoria,
                                                        )

    # Função para Salvar no Banco
    def save(self):
        db_session.add(self)
        db_session.commit()

    # Função para Deletar no Banco
    def delete(self):
        db_session.delete(self)
        db_session.commit()

    # Coloca os Dados na Tabela
    def serialize(self):
        dados_user = {
            'nome': self.nome,
            'descricao': self.descricao,
            'preco': self.preco,
            'imagem_url': self.imagem_url,
            'validade': self.validade,
            'quantidade': self.quantidade,
            'categoria': self.categoria,
        }
        return dados_user


# MODELO PEDIDOS
class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    status = Column(String(50), default="pendente", nullable=False, index=True)
    local_origem = Column(String(100), nullable=False, index=True)
    horario_abertura = Column(String(50), nullable=False, index=True)

    itens = relationship("OrderItem", backref="pedido", lazy=True)

    def __repr__(self):
        return '<Produto: {} {} {} {}>'.format( self.user_id,
                                                        self.status,
                                                        self.local_origem,
                                                        self.horario_abertura,
                                                        )

    # Função para Salvar no Banco
    def save(self):
        db_session.add(self)
        db_session.commit()

    # Função para Deletar no Banco
    def delete(self):
        db_session.delete(self)
        db_session.commit()

    # Coloca os Dados na Tabela
    def serialize(self):
        dados_user = {
            'user_id': self.user_id,
            'status': self.status,
            'local_origem': self.local_origem,
            'horario_abertura': self.horario_abertura,
        }
        return dados_user


# MODELO ITENS DO PEDIDO
class OrderItem(Base):
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantidade = Column(Integer, nullable=False, index=True)
    preco_unitario = Column(String(100), nullable=False, index=True)

    def __repr__(self):
        return '<Produto: {} {} {} {}>'.format( self.order_id,
                                                        self.product_id,
                                                        self.quantidade,
                                                        self.preco_unitario,
                                                        )

    # Função para Salvar no Banco
    def save(self):
        db_session.add(self)
        db_session.commit()

    # Função para Deletar no Banco
    def delete(self):
        db_session.delete(self)
        db_session.commit()

    # Coloca os Dados na Tabela
    def serialize(self):
        dados_user = {
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantidade': self.quantidade,
            'preco_unitario': self.preco_unitario,
        }
        return dados_user


# MODELO REVIEWS
class Review(Base):
    __tablename__ = "review"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    nota = Column(Integer, nullable=False, index=True)
    comentario = Column(String(100), nullable=False, index=True)

    def __repr__(self):
        return '<Produto: {} {} {} {}>'.format( self.user_id,
                                                        self.product_id,
                                                        self.nota,
                                                        self.comentario,
                                                        )

    # Função para Salvar no Banco
    def save(self):
        db_session.add(self)
        db_session.commit()

    # Função para Deletar no Banco
    def delete(self):
        db_session.delete(self)
        db_session.commit()

    # Coloca os Dados na Tabela
    def serialize(self):
        dados_user = {
            'user_id': self.user_id,
            'product_id': self.product_id,
            'nota': self.nota,
            'comentario': self.comentario,
        }
        return dados_user


# MODELO HISTÓRICO DE PESQUISA
class SearchHistory(Base):
    __tablename__ = "search_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    termo_pesquisa = Column(String(255), nullable=False, index=True)

    def __repr__(self):
        return '<Produto: {} {}>'.format( self.user_id,
                                                self.termo_pesquisa,
                                                )

    # Função para Salvar no Banco
    def save(self):
        db_session.add(self)
        db_session.commit()

    # Função para Deletar no Banco
    def delete(self):
        db_session.delete(self)
        db_session.commit()

    # Coloca os Dados na Tabela
    def serialize(self):
        dados_user = {
            'user_id': self.user_id,
            'termo_pesquisa': self.termo_pesquisa,
        }
        return dados_user

# Método para criar Banco
def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    init_db()