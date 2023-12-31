from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update

from model import Session, Aluno
from logger import logger
from schemas import *
from flask_cors import CORS

from schemas.aluno import AlunoBuscaPorNomeSchema

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)

CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
aluno_tag = Tag(name="Aluno", description="Adição, visualização e remoção de alunos à base")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/aluno', tags=[aluno_tag],
          responses={"200": AlunoViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_aluno(form: AlunoSchema):
    """Adiciona um novo Aluno à base de dados

    Retorna uma representação dos alunos.
    """
    aluno = Aluno(
        nome=form.nome,
        data_nascimento=form.data_nascimento,
        sexo=form.sexo,
        nome_responsavel=form.nome_responsavel)
    logger.debug(f"Adicionando aluno de nome: '{aluno.nome}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando aluno
        session.add(aluno)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado aluno de nome: '{aluno.nome}'")
        return apresenta_aluno(aluno), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Aluno de mesmo nome já salvo na base :/"
        logger.warning(f"Erro ao adicionar aluno '{aluno.nome}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar aluno '{aluno.nome}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.get('/alunos', tags=[aluno_tag],
         responses={"200": ListagemAlunosSchema, "404": ErrorSchema})
def get_alunos():
    """Faz a busca por todos os Aluno cadastrados

    Retorna uma representação da listagem de alunos.
    """
    logger.debug(f"Coletando alunos ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    alunos = session.query(Aluno).all()

    if not alunos:
        # se não há alunos cadastrados
        return {"alunos": []}, 200
    else:
        logger.debug(f"%d alunos econtrados" % len(alunos))
        # retorna a representação de aluno
        print(alunos)
        return apresenta_alunos(alunos), 200

@app.get('/aluno', tags=[aluno_tag],
         responses={"200": AlunoBuscaPorNomeSchema, "404": ErrorSchema})
def get_aluno(query: AlunoBuscaPorNomeSchema):
    """Faz a busca por um Aluno a partir do nome do aluno

    Retorna uma representação aluno.
    """
    aluno_nome = query.nome
    logger.info(f"Coletando dados sobre o aluno #{aluno_nome}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    aluno = session.query(Aluno).filter(Aluno.nome == aluno_nome).first()

    if not aluno:
        # se o produto não foi encontrado
        error_msg = "Aluno não encontrado na base :/"
        logger.warning(f"Erro ao buscar produto '{aluno_nome}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.info("Aluno econtrado: %s" % aluno)
        # retorna a representação de produto
        return apresenta_aluno(aluno), 200


@app.delete('/aluno', tags=[aluno_tag],
            responses={"200": AlunoDelSchema, "404": ErrorSchema})
def del_aluno(query: AlunoDelSchema):
    """Deleta um Aluno a partir do nome do aluno informado

    Retorna uma mensagem de confirmação da remoção.
    """
    aluno_nome = query.nome
    print(aluno_nome)
    logger.debug(f"Deletando dados sobre aluno #{aluno_nome}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    delete = session.query(Aluno).filter(Aluno.nome == aluno_nome).delete()
    session.commit()

    if delete:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado aluno #{aluno_nome}")
        return {"mesage": "Aluno removido", "Nome": aluno_nome}
    else:
        # se o aluno não foi encontrado
        error_msg = "Aluno não encontrado na base :/"
        logger.warning(f"Erro ao deletar aluno #'{aluno_nome}', {error_msg}")
        return {"mesage": error_msg}, 404

@app.put('/aluno/<nome>', tags=[aluno_tag],
          responses={"200": AlunoViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def put_aluno(path: AlunoBuscaPorNomeSchema, form: AlunoSchema):
    """Atualiza um Aluno

    Retorna uma representação do aluno.
    """
    aluno_nome = path.nome
    data_nascimento = form.data_nascimento
    sexo = form.sexo
    nome_responsavel = form.nome_responsavel

    logger.info(f"Coletando dados sobre o aluno #{aluno_nome}")
    # criando conexão com a base
    
    # fazendo a busca
    #aluno = session.query(Aluno).filter(Aluno.nome == aluno_nome).first()
    aluno = Aluno(
        nome=aluno_nome,
        data_nascimento=data_nascimento,
        sexo=sexo,
        nome_responsavel=nome_responsavel
    )
    
    try:
        logger.info("Alterando aluno")
        session = Session()
        stmt = update(Aluno) \
            .where(Aluno.nome == aluno.nome) \
            .values( \
                data_nascimento = aluno.data_nascimento, \
                sexo = aluno.sexo, \
                nome_responsavel = aluno.nome_responsavel)
        
        session.execute(stmt)
        session.commit()
        logger.info(f"Aluno atualizado com suceso: '{aluno.nome}'")
        return apresenta_aluno(aluno), 200
    
    except Exception as e:
            # caso um erro fora do previsto
            error_msg = "Não foi possível atualizar item :/"
            logger.warning(f"Erro ao atualizar aluno '{aluno.nome}', {error_msg}")
            return {"mesage": error_msg}, 400
    

        