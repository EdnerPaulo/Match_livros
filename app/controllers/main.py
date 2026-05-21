from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import SessionLocal, Livro, Usuario
from app.controllers.auth import criar_token, verificar_senha, hash_senha

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# AUTH ROUTES
@router.post("/auth/register")
def register(dados: dict, db: Session = Depends(get_db)):
    novo_user = Usuario(username=dados['username'], password_hash=hash_senha(dados['password']))
    db.add(novo_user)
    db.commit()
    return {"status": "sucesso"}

@router.post("/auth/login")
def login(dados: dict, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.username == dados['username']).first()
    if not user or not verificar_senha(dados['password'], user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return {"token": criar_token({"sub": user.username})}

# CRUD LIVROS
@router.get("/livros")
def listar_livros(db: Session = Depends(get_db)):
    return db.query(Livro).all()

@router.post("/livros")
def criar_livro(livro: dict, db: Session = Depends(get_db)):
    # <<< ACRÉSCIMO CIRÚRGICO: Adicionado o campo foto_url vindo do dicionário se ele existir
    novo = Livro(
        titulo=livro['titulo'], 
        autor=livro['autor'],
        foto_url=livro.get('foto_url')  # Pega a foto se enviada, senão fica None
    )
    db.add(novo)
    db.commit()
    return {"status": "criado"}

@router.put("/livros/{id}")
def editar_livro(id: int, dados: dict, db: Session = Depends(get_db)):
    livro = db.query(Livro).filter(Livro.id == id).first()
    if not livro: raise HTTPException(status_code=404)
    livro.titulo = dados['titulo']
    livro.autor = dados['autor']
    db.commit()
    return {"status": "atualizado"}

@router.delete("/livros/{id}")
def excluir_livro(id: int, db: Session = Depends(get_db)):
    livro = db.query(Livro).filter(Livro.id == id).first()
    if not livro: raise HTTPException(status_code=404)
    db.delete(livro)
    db.commit()
    return {"status": "removido"}