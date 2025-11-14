from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base, relationship
from werkzeug.security import generate_password_hash, check_password_hash

# Configuração do banco de dados
engine = create_engine('sqlite:///Banco.db', connect_args={"check_same_thread": False})
local_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()


class Categoria(Base):
    __tablename__ = 'categorias'
    id_categoria = Column(Integer, primary_key=True)
    nome_categoria = Column(String(50), nullable=False, unique=True)

    # Relação com Produto
    produtos = relationship("Produto", back_populates="categoria")

    def __repr__(self):
        return f"<Categoria(nome={self.nome_categoria})>"

    def save(self, db_session):
        try:
            db_session.add(self)
            db_session.commit()
        except:
            db_session.rollback()
            raise

    def delete(self, db_session):
        try:
            db_session.delete(self)
            db_session.commit()
        except:
            db_session.rollback()
            raise

    def serialize(self):
        var_categoria = {
            'id_categoria': self.id_categoria,
        }
        return var_categoria


class Produto(Base):
    __tablename__ = 'produtos'
    id_produto = Column(Integer, primary_key=True)
    nome_produto = Column(String(50), nullable=False)
    qtd_produto = Column(Integer, default=0, nullable=False, index=True)
    tamanho = Column(String(20))
    marca_produto = Column(String(30))
    custo_produto = Column(Float, nullable=False)
    genero = Column(String(20))
    disponivel = Column(Boolean, default=True)

    id_categoria = Column(Integer, ForeignKey('categorias.id_categoria'))
    categoria = relationship("Categoria", back_populates="produtos")

    # Relações com Venda e Entrada
    vendas = relationship("Venda", back_populates="produto")
    entradas = relationship("Entrada", back_populates="produto")

    def __repr__(self):
        return f"<Produto(nome={self.nome_produto}, marca={self.marca_produto})>"

    def save(self, db_session):
        try:
            db_session.add(self)
            db_session.commit()
        except:
            db_session.rollback()
            raise

    def delete(self, db_session):
        try:
            db_session.delete(self)
            db_session.commit()
        except:
            db_session.rollback()
            raise

    def serialize(self):
        var_produto = {
            'id_produto': self.id_produto,
            'nome_produto': self.nome_produto,
            'qtd_produto': self.qtd_produto,
            'genero': self.genero,
            'tamanho': self.tamanho,
            'marca_produto': self.marca_produto,
            'custo_produto': self.custo_produto,
            'disponivel': self.disponivel,
            'id_categoria': self.id_categoria,
        }
        return var_produto


class Pessoa(Base):
    __tablename__ = 'pessoas'
    id_pessoa = Column(Integer, primary_key=True)
    nome_pessoa = Column(String(50), nullable=False)
    cpf_pessoa = Column(String(14), unique=True)
    cargo = Column(String(30))
    senha_hash = Column(String(128))
    status = Column(Boolean, default=True)

    # Relações
    vendas = relationship("Venda", back_populates="pessoa")
    entradas = relationship("Entrada", back_populates="pessoa")

    def __repr__(self):
        return f"<Pessoa(nome={self.nome_pessoa}, cargo={self.cargo})>"

    def set_senha_hash(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password_hash(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def save(self, db_session):
        try:
            db_session.add(self)
            db_session.commit()
        except:
            db_session.rollback()
            raise

    def delete(self, db_session):
        try:
            db_session.delete(self)
            db_session.commit()
        except:
            db_session.rollback()
            raise

    def serialize(self):
        var_pessoa = {
            'id_pessoa': self.id_pessoa,
            'nome_pessoa': self.nome_pessoa,
            'cpf_pessoa': self.cpf_pessoa,
            'cargo': self.cargo,
            'status': self.status,
        }
        return var_pessoa


class Venda(Base):
    __tablename__ = 'vendas'
    id_venda = Column(Integer, primary_key=True)
    forma_pagamento = Column(String(30))
    quantidade = Column(Integer, nullable=False)
    data_emissao = Column(String(30))
    valor_venda = Column(Float, nullable=False)

    id_pessoa = Column(Integer, ForeignKey('pessoas.id_pessoa'))
    id_produto = Column(Integer, ForeignKey('produtos.id_produto'))

    pessoa = relationship("Pessoa", back_populates="vendas")
    produto = relationship("Produto", back_populates="vendas")

    def __repr__(self):
        return f"<Venda(id={self.id_venda}, produto={self.id_produto}, quantidade={self.quantidade})>"

    def save(self, db_session):
        try:
            db_session.add(self)
            db_session.commit()
        except:
            db_session.rollback()
            raise

    def delete(self, db_session):
        try:
            db_session.delete(self)
            db_session.commit()
        except:
            db_session.rollback()
            raise

    def serialize(self):
        var_venda = {
            'id_venda': self.id_venda,
            'forma_pagamento': self.forma_pagamento,
            'quantidade': self.quantidade,
            'data_emissao': self.data_emissao,
            'valor_venda': self.valor_venda,
            'id_pessoa': self.id_pessoa,
            'id_produto': self.id_produto,
        }
        return var_venda


class Entrada(Base):
    __tablename__ = 'entradas'
    id_entrada = Column(Integer, primary_key=True)
    nota_fiscal = Column(String(50))
    valor_entrada = Column(Float, nullable=False)
    quantidade = Column(Integer, nullable=False)
    data_entrada = Column(String(30))

    id_pessoa = Column(Integer, ForeignKey('pessoas.id_pessoa'))
    id_produto = Column(Integer, ForeignKey('produtos.id_produto'))

    pessoa = relationship("Pessoa", back_populates="entradas")
    produto = relationship("Produto", back_populates="entradas")

    def __repr__(self):
        return f"<Entrada(id={self.id_entrada}, produto={self.id_produto}, quantidade={self.quantidade})>"


    def save(self, db_session):
        try:
            db_session.add(self)
            db_session.commit()
        except:
            db_session.rollback()
            raise

    def delete(self, db_session):
        try:
            db_session.delete(self)
            db_session.commit()
        except:
            db_session.rollback()
            raise

    def serialize(self):
        var_entrada = {
            'id_entrada': self.id_entrada,
            'nota_fiscal': self.nota_fiscal,
            'valor_entrada': self.valor_entrada,
            'quantidade': self.quantidade,
            'data_entrada': self.data_entrada,
            'id_pessoa': self.id_pessoa,
            'id_produto': self.id_produto,
        }
        return var_entrada


def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()